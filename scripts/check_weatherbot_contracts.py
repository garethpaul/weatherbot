#!/usr/bin/env python3
"""Dependency-free route and API contract checks for weatherbot."""
import importlib.util
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


class FakeBottle:
    def get(self, _route):
        return lambda func: func

    def post(self, _route):
        return lambda func: func


class MutableRequest:
    def __init__(self):
        self.query = {}
        self.json = None


class MutableResponse:
    def __init__(self):
        self.status = 200


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
    bottle.Bottle = lambda: FakeBottle()
    bottle.request = request
    bottle.response = response
    bottle.debug = lambda _enabled: None

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
    module.OPEN_WEATHER_TOKEN = "weather-token"
    module.REQUEST_TIMEOUT = 5
    calls = []
    module.client = types.SimpleNamespace(
        run_actions=lambda session_id, message: calls.append((session_id, message))
    )
    return module, request, response, requests, calls


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


def test_wit_requests_use_timeout():
    _messenger, _request, _response, requests, _calls = load_messenger()
    wit = sys.modules["wit"]

    result = wit.Wit("wit-token").message("weather in Yountville")

    assert_equal(result, {}, "wit message response")
    method, url, kwargs = requests.calls[0]
    assert_equal(method, "request", "wit request method")
    assert_equal(url, "https://api.wit.ai/message", "wit message url")
    assert_equal(kwargs.get("timeout"), 5, "wit request timeout")


def test_first_entity_value_handles_malformed_entities():
    messenger, _request, _response, _requests, _calls = load_messenger()

    malformed_cases = [
        None,
        {},
        {"location": []},
        {"location": ["Yountville"]},
        {"location": [{}]},
        {"location": [{"value": ""}]},
    ]

    for entities in malformed_cases:
        assert_equal(
            messenger.first_entity_value(entities, "location"),
            None,
            "malformed entity value",
        )

    assert_equal(
        messenger.first_entity_value({"location": [{"value": "Yountville"}]}, "location"),
        "Yountville",
        "flat entity value",
    )
    assert_equal(
        messenger.first_entity_value({"location": [{"value": {"value": "Yountville"}}]}, "location"),
        "Yountville",
        "nested entity value",
    )


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


def main():
    tests = [
        test_messenger_post_rejects_invalid_json_shape,
        test_messenger_verification_rejects_missing_configured_token,
        test_messenger_verification_rejects_wrong_token,
        test_messenger_verification_accepts_matching_token,
        test_messenger_verification_requires_challenge,
        test_messenger_post_ignores_non_message_events,
        test_messenger_post_routes_text_messages_to_wit,
        test_fb_message_uses_header_auth_and_timeout,
        test_weather_lookup_uses_https_params_and_timeout,
        test_weather_lookup_handles_malformed_results,
        test_wit_requests_use_timeout,
        test_first_entity_value_handles_malformed_entities,
        test_get_forecast_handles_missing_entities,
        test_get_forecast_handles_malformed_weather_results,
        test_completed_plans_are_in_docs_plans,
    ]
    for test in tests:
        test()
    print("weatherbot contract checks passed ({0} tests)".format(len(tests)))


if __name__ == "__main__":
    main()
