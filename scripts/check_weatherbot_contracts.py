#!/usr/bin/env python3
"""Dependency-free route and API contract checks for weatherbot."""
import importlib.util
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-08-weatherbot-webhook-api-hardening.md"


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


def test_wit_requests_use_timeout():
    _messenger, _request, _response, requests, _calls = load_messenger()
    wit = sys.modules["wit"]

    result = wit.Wit("wit-token").message("weather in Yountville")

    assert_equal(result, {}, "wit message response")
    method, url, kwargs = requests.calls[0]
    assert_equal(method, "request", "wit request method")
    assert_equal(url, "https://api.wit.ai/message", "wit message url")
    assert_equal(kwargs.get("timeout"), 5, "wit request timeout")


def test_completed_plan_is_in_docs_plans():
    assert_true(PLAN_PATH.is_file(), "weatherbot hardening plan must live under docs/plans")
    assert_true("status: completed" in PLAN_PATH.read_text(), "weatherbot hardening plan must be completed")


def main():
    tests = [
        test_messenger_post_rejects_invalid_json_shape,
        test_messenger_post_ignores_non_message_events,
        test_messenger_post_routes_text_messages_to_wit,
        test_fb_message_uses_header_auth_and_timeout,
        test_weather_lookup_uses_https_params_and_timeout,
        test_wit_requests_use_timeout,
        test_completed_plan_is_in_docs_plans,
    ]
    for test in tests:
        test()
    print("weatherbot contract checks passed ({0} tests)".format(len(tests)))


if __name__ == "__main__":
    main()
