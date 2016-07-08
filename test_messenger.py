import unittest
import json
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
        r = test_app.post_json('/webhook', self.data)
        self.assertEqual(r.status_int, 200)

    def test_facebook_response(self):
        """
        A test to send a FB message test
        """
        r = messenger.fb_message(self.user_id, "hello this is a test")
        self.assertTrue(len(r) >= 1)
        self.assertTrue(json.loads(r)['recipient_id'] == self.user_id)

    def test_weather(self):
        weather = messenger.get_weather(self.location)
        self.assertTrue(len(weather) >= 1)


if __name__ == '__main__':
    unittest.main()
