import unittest
import json
import os
import hashlib
import hmac
import logging
from unittest import mock

os.environ.setdefault('WIT_TOKEN', 'test-wit-token')
os.environ.setdefault('FB_PAGE_TOKEN', 'test-page-token')
os.environ.setdefault('FB_VERIFY_TOKEN', 'test-verify-token')
os.environ.setdefault('FB_APP_SECRET', 'test-app-secret')
os.environ.setdefault('OPEN_WEATHER_TOKEN', 'test-weather-token')

import messenger
import wit
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
        messenger.recent_messenger_message_ids = messenger.RecentMessageIds(
            messenger.MAX_RECENT_MESSENGER_MESSAGE_IDS)

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

    def test_facebook_verification_challenge_is_plain_text(self):
        response = test_app.get(
            '/webhook?hub.challenge=%3Cscript%3Ealert(1)%3C%2Fscript%3E'
            '&hub.verify_token=test-verify-token')

        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.text, '<script>alert(1)</script>')
        self.assertEqual(response.content_type, 'text/plain')

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

    def test_facebook_echo_is_ignored_before_later_user_message(self):
        data = {'object': 'page',
                'entry': [{'messaging': [
                    {'sender': {'id': 'page-1'},
                     'message': {'text': 'page reply', 'is_echo': True}},
                    {'sender': {'id': 'user-2'},
                     'message': {'text': 'weather in Yountville'}},
                ]}]}

        class FakeClient(object):
            def __init__(self):
                self.calls = []

            def run_actions(self, session_id, message):
                self.calls.append((session_id, message))

        original_client = messenger.client
        fake_client = FakeClient()
        messenger.client = fake_client
        try:
            response = self.post_signed_json(data)
        finally:
            messenger.client = original_client

        self.assertEqual(response.status_int, 200)
        self.assertEqual(fake_client.calls, [
            ('user-2', 'weather in Yountville'),
        ])

    def test_facebook_malformed_nested_events_do_not_hide_later_messages(self):
        data = {'object': 'page',
                'entry': [{'messaging': [
                    {'sender': ['malformed'], 'message': {'text': 'ignored'}},
                    {'sender': {'id': 'ignored'}, 'message': ['malformed']},
                    {'sender': {'id': 'user-2'},
                     'message': {'text': 'weather in Yountville'}},
                ]}]}
        calls = []
        original_client = messenger.client
        messenger.client = mock.Mock(
            run_actions=lambda session_id, message: calls.append((session_id, message)))
        try:
            response = self.post_signed_json(data)
        finally:
            messenger.client = original_client

        self.assertEqual(response.status_int, 200)
        self.assertEqual(calls, [('user-2', 'weather in Yountville')])

    def test_facebook_caps_valid_message_batch(self):
        events = [
            {'sender': {'id': 'user-{0}'.format(index)},
             'message': {'mid': 'batch-{0}'.format(index),
                         'text': 'weather-{0}'.format(index)}}
            for index in range(messenger.MAX_MESSENGER_MESSAGES_PER_WEBHOOK + 1)
        ]
        calls = []
        original_client = messenger.client
        messenger.client = mock.Mock(
            run_actions=lambda session_id, message: calls.append((session_id, message)))
        try:
            response = self.post_signed_json(
                {'object': 'page', 'entry': [{'messaging': events}]})
        finally:
            messenger.client = original_client

        self.assertEqual(response.status_int, 200)
        self.assertEqual(len(calls), messenger.MAX_MESSENGER_MESSAGES_PER_WEBHOOK)
        self.assertEqual(calls[0], ('user-0', 'weather-0'))
        self.assertEqual(calls[-1], ('user-19', 'weather-19'))

    def test_facebook_replayed_message_id_runs_actions_once(self):
        class FakeClient(object):
            def __init__(self):
                self.calls = []

            def run_actions(self, session_id, message):
                self.calls.append((session_id, message))

        original_client = messenger.client
        fake_client = FakeClient()
        messenger.client = fake_client
        try:
            first = self.post_signed_json(self.data)
            replay = self.post_signed_json(self.data)
        finally:
            messenger.client = original_client

        self.assertEqual(first.status_int, 200)
        self.assertEqual(replay.status_int, 200)
        self.assertEqual(fake_client.calls, [(self.user_id, 'hey')])

    def test_facebook_duplicate_batch_item_does_not_block_later_message(self):
        data = {'object': 'page',
                'entry': [{'messaging': [
                    {'sender': {'id': 'user-1'},
                     'message': {'mid': 'mid-1', 'text': 'first'}},
                    {'sender': {'id': 'user-1'},
                     'message': {'mid': 'mid-1', 'text': 'first'}},
                    {'sender': {'id': 'user-2'},
                     'message': {'mid': 'mid-2', 'text': 'second'}},
                ]}]}

        calls = []
        original_client = messenger.client
        messenger.client = mock.Mock(
            run_actions=lambda session_id, message: calls.append((session_id, message)))
        try:
            response = self.post_signed_json(data)
        finally:
            messenger.client = original_client

        self.assertEqual(response.status_int, 200)
        self.assertEqual(calls, [('user-1', 'first'), ('user-2', 'second')])

    def test_facebook_wit_failure_releases_message_claim_for_retry(self):
        calls = []

        def run_actions(session_id, message):
            calls.append((session_id, message))
            if len(calls) == 1:
                raise messenger.WitError('Wit request failed.')

        original_client = messenger.client
        messenger.client = mock.Mock(run_actions=run_actions)
        try:
            first = self.post_signed_json(self.data)
            retry = self.post_signed_json(self.data)
        finally:
            messenger.client = original_client

        self.assertEqual(first.status_int, 200)
        self.assertEqual(retry.status_int, 200)
        self.assertEqual(calls, [(self.user_id, 'hey'), (self.user_id, 'hey')])

    def test_facebook_unexpected_failure_releases_message_claim_for_retry(self):
        calls = []

        def run_actions(session_id, message):
            calls.append((session_id, message))
            if len(calls) == 1:
                raise RuntimeError('programming error')

        original_client = messenger.client
        messenger.client = mock.Mock(run_actions=run_actions)
        try:
            failed = self.post_signed_json(self.data, expect_errors=True)
            retry = self.post_signed_json(self.data)
        finally:
            messenger.client = original_client

        self.assertEqual(failed.status_int, 500)
        self.assertEqual(retry.status_int, 200)
        self.assertEqual(calls, [(self.user_id, 'hey'), (self.user_id, 'hey')])

    def test_facebook_messages_without_ids_preserve_compatibility(self):
        data = {'object': 'page',
                'entry': [{'messaging': [{'sender': {'id': 'user-1'},
                                          'message': {'text': 'weather'}}]}]}
        calls = []
        original_client = messenger.client
        messenger.client = mock.Mock(
            run_actions=lambda session_id, message: calls.append((session_id, message)))
        try:
            self.post_signed_json(data)
            self.post_signed_json(data)
        finally:
            messenger.client = original_client

        self.assertEqual(calls, [('user-1', 'weather'), ('user-1', 'weather')])

    def test_facebook_malformed_message_ids_preserve_compatibility(self):
        data = {'object': 'page',
                'entry': [{'messaging': [{'sender': {'id': 'user-1'},
                                          'message': {'mid': {'bad': 'id'},
                                                      'text': 'weather'}}]}]}
        calls = []
        original_client = messenger.client
        messenger.client = mock.Mock(
            run_actions=lambda session_id, message: calls.append((session_id, message)))
        try:
            self.post_signed_json(data)
            self.post_signed_json(data)
        finally:
            messenger.client = original_client

        self.assertEqual(calls, [('user-1', 'weather'), ('user-1', 'weather')])

    def test_recent_message_ids_evict_oldest_claim_at_bound(self):
        recent = messenger.RecentMessageIds(2)

        self.assertTrue(recent.claim('mid-1'))
        self.assertTrue(recent.claim('mid-2'))
        self.assertTrue(recent.claim('mid-3'))
        self.assertFalse(recent.claim('mid-3'))
        self.assertTrue(recent.claim('mid-1'))

    def test_facebook_wit_failure_does_not_block_later_messages(self):
        data = {'object': 'page',
                'entry': [{'messaging': [
                    {'sender': {'id': 'user-1'},
                     'message': {'text': 'first'}},
                    {'sender': {'id': 'user-2'},
                     'message': {'text': 'second'}},
                ]}]}

        class FakeClient(object):
            def __init__(self):
                self.calls = []

            def run_actions(self, session_id, message):
                self.calls.append((session_id, message))
                if message == 'first':
                    raise messenger.WitError('Wit request failed.')

        original_client = messenger.client
        fake_client = FakeClient()
        messenger.client = fake_client
        try:
            response = self.post_signed_json(data)
        finally:
            messenger.client = original_client

        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.text, 'ok')
        self.assertEqual(fake_client.calls, [
            ('user-1', 'first'),
            ('user-2', 'second'),
        ])

    def test_facebook_unexpected_action_error_is_not_swallowed(self):
        class FakeClient(object):
            def run_actions(self, session_id, message):
                raise RuntimeError('programming error')

        original_client = messenger.client
        messenger.client = FakeClient()
        try:
            response = self.post_signed_json(self.data, expect_errors=True)
        finally:
            messenger.client = original_client

        self.assertEqual(response.status_int, 500)

    def test_facebook_invalid_payload(self):
        """
        Invalid JSON payloads should not raise server errors.
        """
        r = test_app.post('/webhook', '', content_type='text/plain',
                          headers={'X-Hub-Signature-256': 'sha256=invalid'},
                          expect_errors=True)
        self.assertEqual(r.status_int, 415)

    def test_facebook_accepts_json_content_type_parameters(self):
        response = self.post_signed_json(
            self.data,
            content_type='Application/JSON; charset=UTF-8')
        self.assertEqual(response.status_int, 200)

    def test_facebook_rejects_json_prefix_spoof(self):
        body = json.dumps(self.data).encode('utf-8')
        signature = 'sha256=' + hmac.new(
            messenger.FB_APP_SECRET.encode('utf-8'),
            body,
            hashlib.sha256).hexdigest()
        response = test_app.post(
            '/webhook', body, content_type='application/jsonp',
            headers={'X-Hub-Signature-256': signature},
            expect_errors=True)
        self.assertEqual(response.status_int, 415)

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

    def post_signed_json(self, payload, expect_errors=False,
                         content_type='application/json'):
        body = json.dumps(payload).encode('utf-8')
        signature = 'sha256=' + hmac.new(
            messenger.FB_APP_SECRET.encode('utf-8'),
            body,
            hashlib.sha256).hexdigest()
        return test_app.post('/webhook', body, content_type=content_type,
                             headers={'X-Hub-Signature-256': signature},
                             expect_errors=expect_errors)

    def test_wit_transport_failure_uses_stable_error_with_cause(self):
        transport_error = wit.requests.RequestException(
            'request exposed token and private URL')

        with mock.patch.object(wit.requests, 'request', side_effect=transport_error):
            with self.assertRaises(wit.WitError) as raised:
                wit.req(logging.getLogger('test'), 'secret-token', 'GET', '/message', {})

        self.assertEqual(str(raised.exception), 'Wit request failed.')
        self.assertIs(raised.exception.__cause__, transport_error)

    def test_wit_invalid_json_uses_stable_error_with_cause(self):
        decode_error = ValueError('provider body contained private data')
        fake_response = mock.Mock(status_code=200)
        fake_response.json.side_effect = decode_error

        with mock.patch.object(wit.requests, 'request', return_value=fake_response):
            with self.assertRaises(wit.WitError) as raised:
                wit.req(logging.getLogger('test'), 'secret-token', 'GET', '/message', {})

        self.assertEqual(str(raised.exception), 'Wit response was invalid.')
        self.assertIs(raised.exception.__cause__, decode_error)

    def test_wit_non_object_json_uses_stable_error(self):
        fake_response = mock.Mock(status_code=200)
        fake_response.json.return_value = ['unexpected', 'response']

        with mock.patch.object(wit.requests, 'request', return_value=fake_response):
            with self.assertRaises(wit.WitError) as raised:
                wit.req(logging.getLogger('test'), 'secret-token', 'GET', '/message', {})

        self.assertEqual(str(raised.exception), 'Wit response was invalid.')

    def test_wit_provider_error_does_not_expose_response_details(self):
        fake_response = mock.Mock(status_code=200)
        fake_response.json.return_value = {
            'error': 'provider body exposed a token and private message',
        }

        with mock.patch.object(wit.requests, 'request', return_value=fake_response):
            with self.assertRaises(wit.WitError) as raised:
                wit.req(logging.getLogger('test'), 'secret-token', 'GET', '/message', {})

        self.assertEqual(str(raised.exception), 'Wit responded with an error.')

    def test_facebook_response(self):
        """
        A test to send a FB message test
        """
        calls = []
        original_post = messenger.requests.post

        class FakeResponse(object):
            def __init__(self, user_id):
                self.content = json.dumps({'recipient_id': user_id})

            def raise_for_status(self):
                return None

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

    def test_facebook_response_raises_for_http_error(self):
        original_post = messenger.requests.post

        class FailedResponse(object):
            content = b'provider error'

            def raise_for_status(self):
                raise RuntimeError('provider rejected reply')

        messenger.requests.post = lambda _url, **_kwargs: FailedResponse()
        try:
            with self.assertRaisesRegex(RuntimeError, 'provider rejected reply'):
                messenger.fb_message(self.user_id, 'hello this is a test')
        finally:
            messenger.requests.post = original_post

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

    def test_wit_entity_values_are_normalized(self):
        malformed_values = [
            None,
            {'location': [{'value': {'confidence': 0.9}}]},
            {'location': [{'value': {'value': []}}]},
            {'location': [{'value': 42}]},
            {'location': [{'value': '   '}]},
        ]
        for entities in malformed_values:
            self.assertIsNone(messenger.first_entity_value(entities, 'location'))

        self.assertEqual(
            messenger.first_entity_value(
                {'location': [{'value': '  Yountville  '}]}, 'location'),
            'Yountville')
        self.assertEqual(
            messenger.first_entity_value(
                {'location': [{'value': {'value': '  Napa  '}}]}, 'location'),
            'Napa')


if __name__ == '__main__':
    unittest.main()
