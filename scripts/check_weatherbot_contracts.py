#!/usr/bin/env python3
"""Dependency-free route and API contract checks for weatherbot."""
import importlib.util
import hashlib
import hmac
import io
import os
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
WEBHOOK_API_PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-08-weatherbot-webhook-api-hardening.md"
VERIFY_TOKEN_PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-08-weatherbot-verify-token-fails-closed.md"
WIT_ENTITY_PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-08-weatherbot-wit-entity-shape.md"
WEATHER_RESULT_PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-09-weatherbot-weather-result-shape.md"
REQUEST_TIMEOUT_PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-09-weatherbot-request-timeout.md"
DEBUG_MODE_PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-09-weatherbot-debug-mode.md"
MESSENGER_TEXT_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-09-weatherbot-messenger-text-normalization.md"
)
MESSENGER_SENDER_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-09-weatherbot-messenger-sender-normalization.md"
)
WIT_LOG_PRIVACY_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-09-weatherbot-wit-log-privacy.md"
)
WEATHER_EXCEPTION_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-09-weatherbot-weather-exception-fallback.md"
)
MESSENGER_OBJECT_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-09-weatherbot-messenger-object-guard.md"
)
PYTHON3_CI_PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-10-python3-runtime-and-ci.md"
WEBHOOK_SIZE_PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-10-messenger-webhook-size-limit.md"
WIT_ENTITY_NORMALIZATION_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-10-weatherbot-wit-entity-normalization.md"
)
WIT_FAILURE_ISOLATION_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-12-weatherbot-wit-failure-isolation.md"
)
MESSENGER_CONTENT_TYPE_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-12-messenger-json-content-type.md"
)
ROOTED_CLEANUP_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-12-root-independent-cleanup.md"
)
MESSENGER_CHALLENGE_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-12-messenger-challenge-plain-text.md"
)
MESSENGER_ECHO_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-13-messenger-echo-guard.md"
)


class FakeBottle:
    def get(self, _route):
        return lambda func: func

    def post(self, _route):
        return lambda func: func


class MutableRequest:
    def __init__(self):
        self.query = {}
        self.json = None
        self.body = io.BytesIO(b"")
        self.content_length = 0
        self.headers = {
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=" + hmac.new(
                b"app-secret", b"", hashlib.sha256).hexdigest()
        }


class MutableResponse:
    def __init__(self):
        self.status = 200
        self.content_type = None


class FakeHTTPResponse:
    def __init__(self, content, payload=None):
        self.content = content
        self._payload = payload or {}
        self.status_code = 200
        self.reason = "OK"

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


class FakeRequests(types.SimpleNamespace):
    def __init__(self):
        super(FakeRequests, self).__init__()
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append(("post", url, kwargs))
        return FakeHTTPResponse(b'{"recipient_id": "user-1"}')

    def get(self, url, params=None, **kwargs):
        kwargs["params"] = params
        self.calls.append(("get", url, kwargs))
        return FakeHTTPResponse(
            b'{"weather": [{"main": "Clear"}]}',
            {"weather": [{"main": "Clear"}]},
        )

    def request(self, method, url, **kwargs):
        self.calls.append(("request", url, dict(kwargs, method=method)))
        return FakeHTTPResponse(b"{}", {})


def install_stubs():
    request = MutableRequest()
    response = MutableResponse()
    requests = FakeRequests()

    bottle = types.ModuleType("bottle")
    bottle.debug_calls = []
    bottle.Bottle = lambda: FakeBottle()
    bottle.request = request
    bottle.response = response

    def debug(enabled):
        bottle.debug_calls.append(enabled)

    bottle.debug = debug

    sys.modules["bottle"] = bottle
    sys.modules["requests"] = requests
    return request, response, requests


def load_messenger():
    request, response, requests = install_stubs()
    for module_name in ("weatherbot_messenger", "wit"):
        sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location("weatherbot_messenger", str(ROOT / "messenger.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.FB_PAGE_TOKEN = "page-token"
    module.FB_VERIFY_TOKEN = "verify-token"
    module.FB_APP_SECRET = "app-secret"
    module.OPEN_WEATHER_TOKEN = "weather-token"
    module.REQUEST_TIMEOUT = 5
    calls = []
    module.client = types.SimpleNamespace(
        run_actions=lambda session_id, message: calls.append((session_id, message))
    )
    return module, request, response, requests, calls


def load_timeout_values(value):
    original = os.environ.get("REQUEST_TIMEOUT")
    if value is None:
        os.environ.pop("REQUEST_TIMEOUT", None)
    else:
        os.environ["REQUEST_TIMEOUT"] = value

    try:
        install_stubs()
        for module_name in ("weatherbot_timeout_messenger", "wit"):
            sys.modules.pop(module_name, None)
        spec = importlib.util.spec_from_file_location(
            "weatherbot_timeout_messenger", str(ROOT / "messenger.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.REQUEST_TIMEOUT, sys.modules["wit"].DEFAULT_REQUEST_TIMEOUT
    finally:
        sys.modules.pop("weatherbot_timeout_messenger", None)
        sys.modules.pop("wit", None)
        if original is None:
            os.environ.pop("REQUEST_TIMEOUT", None)
        else:
            os.environ["REQUEST_TIMEOUT"] = original


def load_debug_values(value):
    original = os.environ.get("WEATHERBOT_DEBUG")
    if value is None:
        os.environ.pop("WEATHERBOT_DEBUG", None)
    else:
        os.environ["WEATHERBOT_DEBUG"] = value

    try:
        install_stubs()
        for module_name in ("weatherbot_debug_messenger", "wit"):
            sys.modules.pop(module_name, None)
        spec = importlib.util.spec_from_file_location(
            "weatherbot_debug_messenger", str(ROOT / "messenger.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return list(sys.modules["bottle"].debug_calls)
    finally:
        sys.modules.pop("weatherbot_debug_messenger", None)
        sys.modules.pop("wit", None)
        if original is None:
            os.environ.pop("WEATHERBOT_DEBUG", None)
        else:
            os.environ["WEATHERBOT_DEBUG"] = original


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError("{0}: expected {1!r}, got {2!r}".format(label, expected, actual))


def assert_true(condition, label):
    if not condition:
        raise AssertionError(label)


def test_messenger_post_rejects_invalid_json_shape():
    messenger, request, response, _requests, _calls = load_messenger()

    request.json = None
    response.status = 200

    body = messenger.messenger_post()

    assert_equal(response.status, 400, "invalid json status")
    assert_true(body != "ok", "invalid json must not be acknowledged as valid")


def test_messenger_post_rejects_non_page_object():
    messenger, request, response, _requests, calls = load_messenger()

    request.json = {
        "object": "user",
        "entry": [{
            "messaging": [{
                "sender": {"id": "user-1"},
                "message": {"text": "weather in Yountville"},
            }]
        }],
    }
    response.status = 200

    body = messenger.messenger_post()

    assert_equal(response.status, 400, "non-page Messenger object status")
    assert_true(body != "ok", "non-page Messenger objects must not be acknowledged as valid")
    assert_equal(calls, [], "non-page Messenger objects must not call Wit actions")


def test_messenger_verification_rejects_missing_configured_token():
    messenger, request, response, _requests, _calls = load_messenger()

    messenger.FB_VERIFY_TOKEN = None
    request.query = {"hub.challenge": "challenge-1"}
    response.status = 200

    body = messenger.messenger_webhook()

    assert_equal(response.status, 403, "missing configured verify token status")
    assert_true(body != "challenge-1", "missing configured token must not echo challenge")


def test_messenger_verification_rejects_wrong_token():
    messenger, request, response, _requests, _calls = load_messenger()

    request.query = {"hub.challenge": "challenge-1", "hub.verify_token": "wrong"}
    response.status = 200

    body = messenger.messenger_webhook()

    assert_equal(response.status, 403, "wrong verify token status")
    assert_true(body != "challenge-1", "wrong verify token must not echo challenge")


def test_messenger_verification_accepts_matching_token():
    messenger, request, response, _requests, _calls = load_messenger()

    request.query = {"hub.challenge": "challenge-1", "hub.verify_token": "verify-token"}
    response.status = 200

    body = messenger.messenger_webhook()

    assert_equal(body, "challenge-1", "matching verify token challenge")
    assert_equal(response.status, 200, "matching verify token status")
    assert_equal(response.content_type, "text/plain; charset=UTF-8", "verification challenge content type")


def test_messenger_verification_requires_challenge():
    messenger, request, response, _requests, _calls = load_messenger()

    request.query = {"hub.verify_token": "verify-token"}
    response.status = 200

    body = messenger.messenger_webhook()

    assert_equal(response.status, 400, "missing challenge status")
    assert_true(body != "challenge-1", "missing challenge must not echo challenge")


def test_messenger_post_ignores_non_message_events():
    messenger, request, response, _requests, calls = load_messenger()

    request.json = {
        "object": "page",
        "entry": [{
            "messaging": [{
                "sender": {"id": "user-1"},
                "delivery": {"mids": ["mid-1"]},
            }]
        }],
    }
    response.status = 200

    body = messenger.messenger_post()

    assert_equal(body, "ok", "non-message event response")
    assert_equal(calls, [], "non-message events must not call Wit actions")


def test_messenger_post_ignores_echoes_and_continues_batch():
    messenger, request, response, _requests, calls = load_messenger()
    request.json = {
        "object": "page",
        "entry": [{
            "messaging": [
                {
                    "sender": {"id": "page-1"},
                    "message": {"text": "page reply", "is_echo": True},
                },
                {
                    "sender": {"id": "user-1"},
                    "message": {"text": "weather in Yountville"},
                },
            ]
        }],
    }
    response.status = 200

    body = messenger.messenger_post()

    assert_equal(body, "ok", "Messenger echo event response")
    assert_equal(calls, [("user-1", "weather in Yountville")], "post-echo Wit call")


def test_messenger_post_requires_boolean_true_echo_flag():
    messenger, request, response, _requests, calls = load_messenger()
    request.json = {
        "object": "page",
        "entry": [{
            "messaging": [{
                "sender": {"id": "user-1"},
                "message": {"text": "weather", "is_echo": "false"},
            }]
        }],
    }
    response.status = 200

    body = messenger.messenger_post()

    assert_equal(body, "ok", "non-boolean echo flag response")
    assert_equal(calls, [("user-1", "weather")], "non-boolean echo flag Wit call")


def test_messenger_post_routes_text_messages_to_wit():
    messenger, request, response, _requests, calls = load_messenger()

    request.json = {
        "object": "page",
        "entry": [{
            "messaging": [{
                "sender": {"id": "user-1"},
                "message": {"text": "weather in Yountville"},
            }]
        }],
    }
    response.status = 200

    body = messenger.messenger_post()

    assert_equal(body, "ok", "message event response")
    assert_equal(calls, [("user-1", "weather in Yountville")], "Wit action call")


def test_messenger_post_isolates_wit_failures_per_message():
    messenger, request, response, _requests, _calls = load_messenger()
    processed = []

    def run_actions(session_id, message):
        processed.append((session_id, message))
        if message == "first":
            raise messenger.WitError("Wit request failed.")

    messenger.client = types.SimpleNamespace(run_actions=run_actions)
    request.json = {
        "object": "page",
        "entry": [{
            "messaging": [
                {"sender": {"id": "user-1"}, "message": {"text": "first"}},
                {"sender": {"id": "user-2"}, "message": {"text": "second"}},
            ]
        }],
    }

    body = messenger.messenger_post()

    assert_equal(response.status, 200, "isolated Wit failure status")
    assert_equal(body, "ok", "isolated Wit failure response")
    assert_equal(
        processed,
        [("user-1", "first"), ("user-2", "second")],
        "later messages must run after a Wit failure",
    )


def test_messenger_post_propagates_unexpected_action_errors():
    messenger, request, _response, _requests, _calls = load_messenger()

    def run_actions(session_id, message):
        raise RuntimeError("programming error")

    messenger.client = types.SimpleNamespace(run_actions=run_actions)
    request.json = {
        "object": "page",
        "entry": [{
            "messaging": [{
                "sender": {"id": "user-1"},
                "message": {"text": "weather"},
            }]
        }],
    }

    try:
        messenger.messenger_post()
    except RuntimeError as error:
        assert_equal(str(error), "programming error", "unexpected action error")
    else:
        raise AssertionError("unexpected action errors must propagate")


def test_messenger_post_ignores_blank_message_text():
    messenger, request, response, _requests, calls = load_messenger()

    request.json = {
        "object": "page",
        "entry": [{
            "messaging": [{
                "sender": {"id": "user-1"},
                "message": {"text": "   "},
            }]
        }],
    }
    response.status = 200

    body = messenger.messenger_post()

    assert_equal(body, "ok", "blank message event response")
    assert_equal(calls, [], "blank Messenger text must not call Wit actions")


def test_messenger_post_trims_message_text():
    messenger, request, response, _requests, calls = load_messenger()

    request.json = {
        "object": "page",
        "entry": [{
            "messaging": [{
                "sender": {"id": "user-1"},
                "message": {"text": "  weather in Yountville  "},
            }]
        }],
    }
    response.status = 200

    body = messenger.messenger_post()

    assert_equal(body, "ok", "trimmed message event response")
    assert_equal(calls, [("user-1", "weather in Yountville")], "trimmed Wit action call")


def test_messenger_post_ignores_invalid_sender_ids():
    invalid_sender_ids = [None, "", " \t\n", {"id": "user-1"}, ["user-1"]]
    for sender_id in invalid_sender_ids:
        messenger, request, response, _requests, calls = load_messenger()
        request.json = {
            "object": "page",
            "entry": [{
                "messaging": [{
                    "sender": {"id": sender_id},
                    "message": {"text": "weather in Yountville"},
                }]
            }],
        }
        response.status = 200

        body = messenger.messenger_post()

        assert_equal(body, "ok", "invalid sender id event response")
        assert_equal(calls, [], "invalid Messenger sender IDs must not call Wit actions")


def test_messenger_post_trims_sender_id():
    messenger, request, response, _requests, calls = load_messenger()

    request.json = {
        "object": "page",
        "entry": [{
            "messaging": [{
                "sender": {"id": " user-1 "},
                "message": {"text": "weather in Yountville"},
            }]
        }],
    }
    response.status = 200

    body = messenger.messenger_post()

    assert_equal(body, "ok", "trimmed sender id event response")
    assert_equal(calls, [("user-1", "weather in Yountville")], "trimmed sender id Wit call")


def test_fb_message_uses_header_auth_and_timeout():
    messenger, _request, _response, requests, _calls = load_messenger()

    body = messenger.fb_message("user-1", "hello")

    assert_equal(body, b'{"recipient_id": "user-1"}', "fb response body")
    assert_equal(len(requests.calls), 1, "fb post count")
    method, url, kwargs = requests.calls[0]
    assert_equal(method, "post", "fb request method")
    assert_true("access_token=" not in url, "page token must not be embedded in URL")
    assert_equal(kwargs.get("timeout"), 5, "fb request timeout")
    assert_equal(
        kwargs.get("headers", {}).get("Authorization"),
        "Bearer page-token",
        "fb authorization header",
    )


def test_weather_lookup_uses_https_params_and_timeout():
    messenger, _request, _response, requests, _calls = load_messenger()

    result = messenger.get_weather("Yountville")

    assert_equal(result, "Clear", "weather result")
    method, url, kwargs = requests.calls[0]
    assert_equal(method, "get", "weather request method")
    assert_equal(url, "https://api.openweathermap.org/data/2.5/weather", "weather api url")
    assert_equal(kwargs.get("timeout"), 5, "weather request timeout")
    assert_equal(kwargs.get("params", {}).get("q"), "Yountville", "weather query city")
    assert_equal(kwargs.get("params", {}).get("appid"), "weather-token", "weather api token param")


def test_weather_lookup_handles_malformed_results():
    messenger, _request, _response, requests, _calls = load_messenger()

    malformed_payloads = [
        None,
        {},
        {"weather": []},
        {"weather": ["Clear"]},
        {"weather": [{}]},
        {"weather": [{"main": ""}]},
    ]

    for payload in malformed_payloads:
        def fake_get(url, params=None, **kwargs):
            kwargs["params"] = params
            requests.calls.append(("get", url, kwargs))
            return FakeHTTPResponse(b"{}", payload)

        requests.get = fake_get
        assert_equal(messenger.get_weather("Yountville"), None, "malformed weather response")


def test_request_timeout_accepts_positive_float_env():
    messenger_timeout, wit_timeout = load_timeout_values("2.5")

    assert_equal(messenger_timeout, 2.5, "messenger positive REQUEST_TIMEOUT env")
    assert_equal(wit_timeout, 2.5, "wit positive REQUEST_TIMEOUT env")


def test_request_timeout_defaults_for_invalid_env():
    for value in ("not-a-number", "0", "-3", "nan", "inf"):
        try:
            messenger_timeout, wit_timeout = load_timeout_values(value)
        except Exception as exc:
            raise AssertionError(
                "invalid REQUEST_TIMEOUT must not crash imports: {0}".format(exc)
            )
        assert_equal(messenger_timeout, 5.0, "messenger invalid REQUEST_TIMEOUT {0!r}".format(value))
        assert_equal(wit_timeout, 5.0, "wit invalid REQUEST_TIMEOUT {0!r}".format(value))


def test_bottle_debug_is_disabled_by_default():
    assert_equal(load_debug_values(None), [False], "default Bottle debug flag")


def test_bottle_debug_requires_truthy_env_flag():
    for value in ("1", "true", "TRUE", "yes", "on"):
        assert_equal(load_debug_values(value), [True], "truthy WEATHERBOT_DEBUG {0!r}".format(value))

    for value in ("", "0", "false", "no", "off", "debug"):
        assert_equal(load_debug_values(value), [False], "falsey WEATHERBOT_DEBUG {0!r}".format(value))


def test_wit_requests_use_timeout():
    _messenger, _request, _response, requests, _calls = load_messenger()
    wit = sys.modules["wit"]

    result = wit.Wit("wit-token").message("weather in Yountville")

    assert_equal(result, {}, "wit message response")
    method, url, kwargs = requests.calls[0]
    assert_equal(method, "request", "wit request method")
    assert_equal(url, "https://api.wit.ai/message", "wit message url")
    assert_equal(kwargs.get("timeout"), 5, "wit request timeout")


def test_wit_debug_logs_avoid_message_payloads():
    source = (ROOT / "wit.py").read_text()
    assert_true(
        "logger.debug('%s %s %s', meth, full_url, params)" not in source,
        "Wit request debug logs must not include request params",
    )
    assert_true(
        "logger.debug('%s %s %s', meth, full_url, json)" not in source,
        "Wit response debug logs must not include response JSON",
    )
    assert_true(
        "logger.debug('%s %s request', meth, full_url)" in source,
        "Wit request debug logging may keep method and endpoint only",
    )
    assert_true(
        "logger.debug('%s %s response received', meth, full_url)" in source,
        "Wit response debug logging may keep method and endpoint only",
    )


def test_wit_failures_use_stable_public_errors():
    source = (ROOT / "wit.py").read_text(encoding="utf-8")
    runtime_tests = (ROOT / "test_messenger.py").read_text(encoding="utf-8")
    for contract in [
        "except requests.RequestException as error:",
        "raise WitError('Wit request failed.') from error",
        "except (TypeError, ValueError) as error:",
        "raise WitError('Wit response was invalid.') from error",
        "if not isinstance(data, dict):",
        "raise WitError('Wit responded with an error.')",
    ]:
        assert_true(contract in source, "Wit failure contract: " + contract)
    for test_name in [
        "test_facebook_wit_failure_does_not_block_later_messages",
        "test_facebook_unexpected_action_error_is_not_swallowed",
        "test_wit_transport_failure_uses_stable_error_with_cause",
        "test_wit_invalid_json_uses_stable_error_with_cause",
        "test_wit_non_object_json_uses_stable_error",
        "test_wit_provider_error_does_not_expose_response_details",
    ]:
        assert_true(test_name in runtime_tests, "Wit failure regression: " + test_name)


def test_first_entity_value_handles_malformed_entities():
    messenger, _request, _response, _requests, _calls = load_messenger()

    malformed_cases = [
        None,
        {},
        {"location": []},
        {"location": ["Yountville"]},
        {"location": [{}]},
        {"location": [{"value": ""}]},
        {"location": [{"value": {"confidence": 0.9}}]},
        {"location": [{"value": {"value": []}}]},
        {"location": [{"value": 42}]},
        {"location": [{"value": "   "}]},
    ]

    for entities in malformed_cases:
        assert_equal(
            messenger.first_entity_value(entities, "location"),
            None,
            "malformed entity value",
        )

    assert_equal(
        messenger.first_entity_value({"location": [{"value": "  Yountville  "}]}, "location"),
        "Yountville",
        "trimmed flat entity value",
    )
    assert_equal(
        messenger.first_entity_value({"location": [{"value": {"value": "  Napa  "}}]}, "location"),
        "Napa",
        "trimmed nested entity value",
    )

    source = (ROOT / "messenger.py").read_text(encoding="utf-8")
    runtime_tests = (ROOT / "test_messenger.py").read_text(encoding="utf-8")
    assert_true("return clean_text_value(val)" in source, "Wit entity values must use text normalization")
    assert_true("val['value']" not in source, "nested Wit entity values must not use unchecked indexing")
    assert_true("test_wit_entity_values_are_normalized" in runtime_tests, "runtime tests must cover Wit entity normalization")


def test_get_forecast_handles_missing_entities():
    messenger, _request, _response, _requests, _calls = load_messenger()
    context = {"forecast": "Clear"}

    result = messenger.get_forecast({"context": context, "entities": None})

    assert_equal(result.get("missingLocation"), True, "missing entities location flag")
    assert_true("forecast" not in result, "missing entities must clear stale forecast")


def test_get_forecast_handles_malformed_weather_results():
    messenger, _request, _response, _requests, _calls = load_messenger()
    context = {"forecast": "Rain", "missingLocation": True}
    original_get_weather = messenger.get_weather
    messenger.get_weather = lambda _location: None

    try:
        result = messenger.get_forecast({
            "context": context,
            "entities": {"location": [{"value": "Yountville"}]},
        })
    finally:
        messenger.get_weather = original_get_weather

    assert_equal(result.get("missingForecast"), True, "malformed weather result flag")
    assert_true("forecast" not in result, "malformed weather results must clear stale forecast")
    assert_true("missingLocation" not in result, "known location must clear stale missingLocation")


def test_get_forecast_handles_weather_lookup_exceptions():
    messenger, _request, _response, _requests, _calls = load_messenger()
    context = {"forecast": "Rain", "missingLocation": True}
    original_get_weather = messenger.get_weather

    def raise_lookup_error(_location):
        raise RuntimeError("weather lookup failed")

    messenger.get_weather = raise_lookup_error
    try:
        result = messenger.get_forecast({
            "context": context,
            "entities": {"location": [{"value": "Yountville"}]},
        })
    finally:
        messenger.get_weather = original_get_weather

    assert_equal(result.get("missingForecast"), True, "weather lookup exceptions set missingForecast")
    assert_true("forecast" not in result, "weather lookup exceptions must clear stale forecast")
    assert_true("missingLocation" not in result, "known location must clear stale missingLocation")


def assert_completed_plan(path, label):
    assert_true(path.is_file(), "{0} plan must live under docs/plans".format(label))
    plan_text = path.read_text()
    assert_true("status: completed" in plan_text.lower(), "{0} plan must be completed".format(label))
    assert_true("make check" in plan_text, "{0} plan must document make check verification".format(label))


def test_completed_plans_are_in_docs_plans():
    assert_completed_plan(WEBHOOK_API_PLAN_PATH, "weatherbot hardening")
    assert_completed_plan(VERIFY_TOKEN_PLAN_PATH, "weatherbot verify token")
    assert_completed_plan(WIT_ENTITY_PLAN_PATH, "weatherbot Wit entity shape")
    assert_completed_plan(WEATHER_RESULT_PLAN_PATH, "weatherbot weather result shape")
    assert_completed_plan(REQUEST_TIMEOUT_PLAN_PATH, "weatherbot request timeout")
    assert_completed_plan(DEBUG_MODE_PLAN_PATH, "weatherbot debug mode")
    assert_completed_plan(MESSENGER_TEXT_PLAN_PATH, "weatherbot Messenger text normalization")
    assert_completed_plan(MESSENGER_SENDER_PLAN_PATH, "weatherbot Messenger sender normalization")
    assert_completed_plan(WIT_LOG_PRIVACY_PLAN_PATH, "weatherbot Wit log privacy")
    assert_completed_plan(WEATHER_EXCEPTION_PLAN_PATH, "weatherbot weather exception fallback")
    assert_completed_plan(MESSENGER_OBJECT_PLAN_PATH, "weatherbot Messenger object guard")
    assert_completed_plan(PYTHON3_CI_PLAN_PATH, "weatherbot Python 3 and CI")
    assert_completed_plan(WEBHOOK_SIZE_PLAN_PATH, "weatherbot Messenger webhook size limit")
    assert_completed_plan(WIT_ENTITY_NORMALIZATION_PLAN_PATH, "weatherbot Wit entity normalization")
    assert_completed_plan(WIT_FAILURE_ISOLATION_PLAN_PATH, "weatherbot Wit failure isolation")
    assert_completed_plan(MESSENGER_CONTENT_TYPE_PLAN_PATH, "weatherbot Messenger JSON content type")
    assert_completed_plan(ROOTED_CLEANUP_PLAN_PATH, "weatherbot root-independent cleanup")
    assert_completed_plan(MESSENGER_CHALLENGE_PLAN_PATH, "weatherbot Messenger challenge plain text")
    assert_completed_plan(MESSENGER_ECHO_PLAN_PATH, "weatherbot Messenger echo guard")


def test_runtime_dependencies_and_ci_are_pinned():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for pattern in ["!.github/", "!.github/workflows/", "!.github/workflows/*.yml"]:
        assert_true(pattern in gitignore, "workflow ignore exception: " + pattern)
    assert_equal(
        (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines(),
        ["bottle==0.13.4", "requests==2.34.2"],
        "runtime dependency pins",
    )
    assert_equal(
        (ROOT / "test-requirements.txt").read_text(encoding="utf-8").splitlines(),
        ["WebTest==3.0.7"],
        "test dependency pins",
    )
    assert_equal(
        (ROOT / ".python-version").read_text(encoding="utf-8").strip(),
        "3.14",
        "deployment runtime line",
    )
    assert_true(not (ROOT / "runtime.txt").exists(), "deprecated runtime.txt must remain removed")
    workflow = (ROOT / ".github" / "workflows" / "check.yml").read_text(encoding="utf-8")
    for contract in [
        "permissions:\n  contents: read",
        "concurrency:",
        "cancel-in-progress: true",
        "runs-on: ubuntu-24.04",
        "timeout-minutes: 10",
        'python-version: ["3.10", "3.12", "3.14"]',
        "workflow_dispatch:",
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10",
        "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
        "python -m pip install --requirement requirements.txt --requirement test-requirements.txt",
        "run: make check",
    ]:
        assert_true(contract in workflow, "hosted verification contract: " + contract)
    assert_true("@v" not in workflow, "hosted actions must use immutable commits")
    assert_true("ubuntu-latest" not in workflow, "hosted verification must use a fixed Ubuntu runner")
    assert_true("# v6.0.3" in workflow, "checkout pin annotation must identify the exact release")
    assert_true("# v6.2.0" in workflow, "setup-python pin annotation must identify the exact release")
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert_true("ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))" in makefile, "Makefile must resolve the repository root")
    assert_true('find "$(ROOT)"' in makefile, "Makefile cleanup must stay inside the repository")
    assert_true('"$(ROOT)/scripts/check_weatherbot_contracts.py"' in makefile, "Makefile must use the rooted contract path")
    assert_true('$(MAKE) -f "$(ROOT)/Makefile" clean' in makefile, "final cleanup must use the repository Makefile")
    messenger_source = (ROOT / "messenger.py").read_text(encoding="utf-8")
    runtime_tests = (ROOT / "test_messenger.py").read_text(encoding="utf-8")
    assert_true("verify_messenger_signature" in messenger_source, "Messenger POST signatures must remain required")
    assert_true("MAX_MESSENGER_WEBHOOK_BYTES = 1024 * 1024" in messenger_source, "Messenger webhook size limit must remain 1 MiB")
    assert_true("request.body.read(MAX_MESSENGER_WEBHOOK_BYTES + 1)" in messenger_source, "Messenger request body reads must remain bounded")
    assert_true("test_facebook_rejects_oversized_payload" in runtime_tests, "WebTest must cover oversized Messenger payloads")
    assert_true("is_json_content_type" in messenger_source, "Messenger POST requests must require JSON media types")
    assert_true("test_facebook_rejects_json_prefix_spoof" in runtime_tests, "WebTest must reject JSON prefix spoofing")
    assert_true("response.content_type = 'text/plain; charset=UTF-8'" in messenger_source, "Messenger challenge responses must be plain text")
    assert_true("test_facebook_verification_challenge_is_plain_text" in runtime_tests, "WebTest must cover challenge response type")


def test_messenger_post_rejects_oversized_declared_body():
    messenger, request, response, _requests, calls = load_messenger()
    request.content_length = messenger.MAX_MESSENGER_WEBHOOK_BYTES + 1

    body = messenger.messenger_post()

    assert_equal(response.status, 413, "oversized declared Messenger body status")
    assert_equal(body, "Payload too large", "oversized declared Messenger body response")
    assert_equal(calls, [], "oversized declared Messenger body Wit calls")


def test_messenger_post_rejects_oversized_streamed_body():
    messenger, request, response, _requests, calls = load_messenger()
    request.content_length = None
    request.body = io.BytesIO(b"x" * (messenger.MAX_MESSENGER_WEBHOOK_BYTES + 1))

    body = messenger.messenger_post()

    assert_equal(response.status, 413, "oversized streamed Messenger body status")
    assert_equal(body, "Payload too large", "oversized streamed Messenger body response")
    assert_equal(calls, [], "oversized streamed Messenger body Wit calls")


def test_messenger_post_accepts_json_content_type_parameters():
    messenger, request, response, _requests, calls = load_messenger()
    request.headers["Content-Type"] = "Application/JSON; charset=UTF-8"
    request.json = {"object": "page", "entry": []}

    body = messenger.messenger_post()

    assert_equal(response.status, 200, "parameterized JSON Messenger status")
    assert_equal(body, "ok", "parameterized JSON Messenger response")
    assert_equal(calls, [], "parameterized empty Messenger payload Wit calls")


def test_messenger_post_rejects_non_json_content_types_before_authentication():
    for content_type in (None, "text/plain", "application/jsonp", "application/ld+json"):
        messenger, request, response, _requests, calls = load_messenger()
        request.headers = {"X-Hub-Signature-256": "sha256=invalid"}
        if content_type is not None:
            request.headers["Content-Type"] = content_type
        request.json = {"object": "page", "entry": []}

        body = messenger.messenger_post()

        assert_equal(response.status, 415, "non-JSON Messenger status {0!r}".format(content_type))
        assert_equal(body, "Unsupported media type", "non-JSON Messenger response {0!r}".format(content_type))
        assert_equal(calls, [], "non-JSON Messenger payload Wit calls")


def main():
    tests = [
        test_messenger_post_rejects_oversized_declared_body,
        test_messenger_post_rejects_oversized_streamed_body,
        test_messenger_post_accepts_json_content_type_parameters,
        test_messenger_post_rejects_non_json_content_types_before_authentication,
        test_messenger_post_rejects_invalid_json_shape,
        test_messenger_post_rejects_non_page_object,
        test_messenger_verification_rejects_missing_configured_token,
        test_messenger_verification_rejects_wrong_token,
        test_messenger_verification_accepts_matching_token,
        test_messenger_verification_requires_challenge,
        test_messenger_post_ignores_non_message_events,
        test_messenger_post_ignores_echoes_and_continues_batch,
        test_messenger_post_requires_boolean_true_echo_flag,
        test_messenger_post_routes_text_messages_to_wit,
        test_messenger_post_isolates_wit_failures_per_message,
        test_messenger_post_propagates_unexpected_action_errors,
        test_messenger_post_ignores_blank_message_text,
        test_messenger_post_trims_message_text,
        test_messenger_post_ignores_invalid_sender_ids,
        test_messenger_post_trims_sender_id,
        test_fb_message_uses_header_auth_and_timeout,
        test_weather_lookup_uses_https_params_and_timeout,
        test_weather_lookup_handles_malformed_results,
        test_request_timeout_accepts_positive_float_env,
        test_request_timeout_defaults_for_invalid_env,
        test_bottle_debug_is_disabled_by_default,
        test_bottle_debug_requires_truthy_env_flag,
        test_wit_requests_use_timeout,
        test_wit_debug_logs_avoid_message_payloads,
        test_wit_failures_use_stable_public_errors,
        test_first_entity_value_handles_malformed_entities,
        test_get_forecast_handles_missing_entities,
        test_get_forecast_handles_malformed_weather_results,
        test_get_forecast_handles_weather_lookup_exceptions,
        test_completed_plans_are_in_docs_plans,
        test_runtime_dependencies_and_ci_are_pinned,
    ]
    for test in tests:
        test()
    print("weatherbot contract checks passed ({0} tests)".format(len(tests)))


if __name__ == "__main__":
    main()
