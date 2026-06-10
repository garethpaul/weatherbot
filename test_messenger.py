import unittest
import json
import os
import hashlib
import hmac

os.environ.setdefault('WIT_TOKEN', 'test-wit-token')
os.environ.setdefault('FB_PAGE_TOKEN', 'test-page-token')
os.environ.setdefault('FB_VERIFY_TOKEN', 'test-verify-token')
os.environ.setdefault('FB_APP_SECRET', 'test-app-secret')
os.environ.setdefault('OPEN_WEATHER_TOKEN', 'test-weather-token')

import messenger
from webtest import TestApp
test_app = TestApp(messenger.app)


class TestMessenger(unittest.TestCase):
    """
    Test Cases for FB Messenger Chat Bot Integration
    """
    def setUp(self):
        """
        Setup the data for the test.
        """
        self.data = {'object': 'page',
                     'entry': [{'time': 1468004411422,
                                'id': '101390813631984',
                                'messaging': [{'timestamp': 1468004411349,
                                               'recipient': {'id': '101390813631984'},
                                               'sender': {'id': '1305664346125260'},
                                               'message': {'mid': 'mid.1468004411246:824cff69c065cf1844',
                                                           'text': 'hey',
                                                           'seq': 137}}]}]}
        self.user_id = '1305664346125260'
        self.challenge = '123'
        self.location = 'Yountville'

    def test_facebook_webhook(self):
        """
        A test with a sample payload for the messenger bot.
        """
        class FakeClient(object):
            def __init__(self):
                self.calls = []

            def run_actions(self, session_id, message):
                self.calls.append((session_id, message))

        original_client = messenger.client
        fake_client = FakeClient()
        messenger.client = fake_client
        try:
            r = self.post_signed_json(self.data)
        finally:
            messenger.client = original_client

        self.assertEqual(r.status_int, 200)
        self.assertEqual(fake_client.calls, [(self.user_id, 'hey')])

    def test_facebook_delivery_event_is_ignored(self):
        """
        Delivery events should be acknowledged without calling Wit.
        """
        data = {'object': 'page',
                'entry': [{'messaging': [{'sender': {'id': self.user_id},
                                          'delivery': {'mids': ['mid-1']}}]}]}
        r = self.post_signed_json(data)
        self.assertEqual(r.status_int, 200)
        self.assertEqual(r.text, 'ok')

    def test_facebook_invalid_payload(self):
        """
        Invalid JSON payloads should not raise server errors.
        """
        r = test_app.post('/webhook', '', content_type='text/plain',
                          headers={'X-Hub-Signature-256': 'sha256=invalid'},
                          expect_errors=True)
        self.assertEqual(r.status_int, 403)

    def test_facebook_invalid_signature(self):
        body = json.dumps(self.data).encode('utf-8')
        r = test_app.post('/webhook', body, content_type='application/json',
                          headers={'X-Hub-Signature-256': 'sha256=invalid'},
                          expect_errors=True)
        self.assertEqual(r.status_int, 403)

    def test_facebook_rejects_oversized_payload(self):
        data = {'object': 'page',
                'padding': 'x' * messenger.MAX_MESSENGER_WEBHOOK_BYTES}
        body = json.dumps(data).encode('utf-8')
        signature = 'sha256=' + hmac.new(
            messenger.FB_APP_SECRET.encode('utf-8'),
            body,
            hashlib.sha256).hexdigest()
        r = test_app.post('/webhook', body, content_type='application/json',
                          headers={'X-Hub-Signature-256': signature},
                          expect_errors=True)
        self.assertEqual(r.status_int, 413)

    def post_signed_json(self, payload):
        body = json.dumps(payload).encode('utf-8')
        signature = 'sha256=' + hmac.new(
            messenger.FB_APP_SECRET.encode('utf-8'),
            body,
            hashlib.sha256).hexdigest()
        return test_app.post('/webhook', body, content_type='application/json',
                             headers={'X-Hub-Signature-256': signature})

    def test_facebook_response(self):
        """
        A test to send a FB message test
        """
        calls = []
        original_post = messenger.requests.post

        class FakeResponse(object):
            def __init__(self, user_id):
                self.content = json.dumps({'recipient_id': user_id})

        def fake_post(url, **kwargs):
            calls.append((url, kwargs))
            return FakeResponse(self.user_id)

        messenger.requests.post = fake_post
        try:
            r = messenger.fb_message(self.user_id, "hello this is a test")
        finally:
            messenger.requests.post = original_post

        self.assertTrue(len(r) >= 1)
        self.assertTrue(json.loads(r)['recipient_id'] == self.user_id)
        self.assertTrue('access_token=' not in calls[0][0])
        self.assertEqual(calls[0][1]['headers']['Authorization'],
                         'Bearer ' + messenger.FB_PAGE_TOKEN)
        self.assertEqual(calls[0][1]['timeout'], messenger.REQUEST_TIMEOUT)

    def test_weather(self):
        original_get = messenger.requests.get

        class FakeResponse(object):
            def raise_for_status(self):
                return None

            def json(self):
                return {'weather': [{'main': 'Clouds'}]}

        calls = []

        def fake_get(url, **kwargs):
            calls.append((url, kwargs))
            return FakeResponse()

        messenger.requests.get = fake_get
        try:
            weather = messenger.get_weather(self.location)
        finally:
            messenger.requests.get = original_get

        self.assertTrue(len(weather) >= 1)
        self.assertEqual(calls[0][1]['params']['q'], self.location)
        self.assertEqual(calls[0][1]['timeout'], messenger.REQUEST_TIMEOUT)


if __name__ == '__main__':
    unittest.main()
