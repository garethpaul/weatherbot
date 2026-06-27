#!/usr/bin/env python
# coding:utf-8

# Messenger API integration example
# We assume you have:
# * a Wit.ai bot setup (https://wit.ai/docs/quickstart)
# * a Messenger Platform setup (https://developers.facebook.com/docs/messenger-platform/quickstart)
# You need to `pip install the following dependencies: requests, bottle.
#
# 1. pip install requests bottle
# 2. You can run this example on a cloud service provider like Heroku, Google Cloud Platform or AWS.
#    Note that webhooks must have a valid SSL certificate, signed by a certificate authority and won't work on your localhost.
# 3. Set your environment variables e.g. WIT_TOKEN=your_wit_token
#                                        FB_PAGE_TOKEN=your_page_token
#                                        FB_VERIFY_TOKEN=your_verify_token
# 4. Run your server e.g. python examples/messenger.py {PORT}
# 5. Subscribe your page to the Webhooks using verify_token and `https://<your_host>/webhook` as callback URL.
# 6. Talk to your bot on Messenger!

import hmac
import hashlib
import math
import os
import requests
import threading
from collections import OrderedDict
from sys import argv
from wit import Wit, WitError
from bottle import Bottle, request, response, debug

# Wit.ai parameters
WIT_TOKEN = os.environ.get('WIT_TOKEN')
# Messenger API parameters
FB_PAGE_TOKEN = os.environ.get('FB_PAGE_TOKEN')
# A user secret to verify webhook get request.
FB_VERIFY_TOKEN = os.environ.get('FB_VERIFY_TOKEN')
FB_APP_SECRET = os.environ.get('FB_APP_SECRET')
# Weather API
OPEN_WEATHER_TOKEN = os.environ.get('OPEN_WEATHER_TOKEN')
FB_MESSAGES_URL = 'https://graph.facebook.com/me/messages'
OPEN_WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'
WEATHER_UNAVAILABLE_MESSAGE = (
    "I couldn't get the weather right now. Please try again."
)


class WeatherProviderError(Exception):
    pass


def positive_float_from_env(name, default):
    try:
        value = float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return float(default)

    if value <= 0 or math.isnan(value) or math.isinf(value):
        return float(default)
    return value


def truthy_env(name):
    value = os.environ.get(name, '')
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


REQUEST_TIMEOUT = positive_float_from_env('REQUEST_TIMEOUT', 5.0)

# Setup Bottle Server
debug(truthy_env('WEATHERBOT_DEBUG'))
app = Bottle()
MAX_MESSENGER_WEBHOOK_BYTES = 1024 * 1024
MAX_RECENT_MESSENGER_MESSAGE_IDS = 1024
MAX_MESSENGER_MESSAGES_PER_WEBHOOK = 20
MAX_WEATHER_LOCATION_LENGTH = 256


class RecentMessageIds(object):
    def __init__(self, max_entries):
        self.max_entries = max_entries
        self._in_flight = set()
        self._completed = OrderedDict()
        self._lock = threading.Lock()

    def claim(self, message_id):
        with self._lock:
            if message_id in self._in_flight or message_id in self._completed:
                return False
            self._in_flight.add(message_id)
            return True

    def complete(self, message_id):
        with self._lock:
            if message_id not in self._in_flight:
                return
            self._in_flight.remove(message_id)
            self._completed[message_id] = None
            while len(self._completed) > self.max_entries:
                self._completed.popitem(last=False)

    def release(self, message_id):
        with self._lock:
            self._in_flight.discard(message_id)


recent_messenger_message_ids = RecentMessageIds(
    MAX_RECENT_MESSENGER_MESSAGE_IDS)


# Facebook Messenger GET Webhook
@app.get('/webhook')
def messenger_webhook():
    """
    A webhook to return a challenge
    """
    response.content_type = 'text/plain; charset=UTF-8'
    response.set_header('X-Content-Type-Options', 'nosniff')
    response.set_header(
        'Content-Security-Policy', "default-src 'none'; sandbox")
    if request.query.get('hub.mode') != 'subscribe':
        response.status = 400
        return 'Invalid verification mode'

    verify_token = request.query.get('hub.verify_token')
    # check whether the verify tokens match
    if not secure_compare(verify_token, FB_VERIFY_TOKEN):
        response.status = 403
        return 'Invalid Request or Verification Token'

    # respond with the challenge to confirm
    challenge = request.query.get('hub.challenge')
    if not challenge:
        response.status = 400
        return 'Missing challenge'
    return challenge


def secure_compare(left, right):
    if not (left and right):
        return False

    left = str(left).encode('utf-8')
    right = str(right).encode('utf-8')
    compare_digest = getattr(hmac, 'compare_digest', None)
    if compare_digest:
        return compare_digest(left, right)

    if len(left) != len(right):
        return False

    result = 0
    for left_char, right_char in zip(bytearray(left), bytearray(right)):
        result |= left_char ^ right_char
    return result == 0


# Facebook Messenger POST Webhook
@app.post('/webhook')
def messenger_post():
    """
    Handler for webhook (currently for postback and messages)
    """
    content_length = getattr(request, 'content_length', None)
    if content_length is not None and content_length > MAX_MESSENGER_WEBHOOK_BYTES:
        response.status = 413
        return 'Payload too large'

    if not is_json_content_type(request.headers.get('Content-Type')):
        response.status = 415
        return 'Unsupported media type'

    raw_body = request.body.read(MAX_MESSENGER_WEBHOOK_BYTES + 1)
    if len(raw_body) > MAX_MESSENGER_WEBHOOK_BYTES:
        response.status = 413
        return 'Payload too large'
    try:
        request.body.seek(0)
    except (AttributeError, IOError):
        pass
    if not verify_messenger_signature(
            raw_body, request.headers.get('X-Hub-Signature-256'), FB_APP_SECRET):
        response.status = 403
        return 'Invalid signature'

    data = request.json
    if not isinstance(data, dict):
        response.status = 400
        return 'Invalid payload'

    if data.get('object') != 'page':
        # Returned another event
        response.status = 400
        return 'Invalid payload'

    processed_messages = 0
    for fb_id, text, message_id in messenger_text_messages(data):
        if processed_messages >= MAX_MESSENGER_MESSAGES_PER_WEBHOOK:
            break
        if message_id and not recent_messenger_message_ids.claim(message_id):
            continue
        processed_messages += 1
        # Let's forward the message to the Wit.ai Bot Engine
        try:
            client.run_actions(session_id=fb_id, message=text)
            if message_id:
                recent_messenger_message_ids.complete(message_id)
        except WitError:
            if message_id:
                recent_messenger_message_ids.release(message_id)
            continue
        except Exception:
            if message_id:
                recent_messenger_message_ids.release(message_id)
            raise

    # must send back response quickly
    return 'ok'


def is_json_content_type(value):
    if not isinstance(value, str):
        return False

    media_type = value.split(';', 1)[0].strip().lower()
    return media_type == 'application/json'


def verify_messenger_signature(raw_body, signature, app_secret):
    if not (raw_body is not None and signature and app_secret):
        return False
    if isinstance(raw_body, str):
        raw_body = raw_body.encode('utf-8')
    expected = 'sha256=' + hmac.new(
        app_secret.encode('utf-8'), raw_body, hashlib.sha256).hexdigest()
    return secure_compare(signature, expected)


def messenger_text_messages(data):
    """
    Extract supported Messenger sender/text/message-ID tuples from a payload.
    """
    messages = []
    entries = data.get('entry')
    if not isinstance(entries, list):
        return messages

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        events = entry.get('messaging')
        if not isinstance(events, list):
            continue
        for event in events:
            if not isinstance(event, dict):
                continue
            sender = event.get('sender')
            message = event.get('message')
            if not isinstance(sender, dict) or not isinstance(message, dict):
                continue
            if message.get('is_echo') is True:
                continue
            fb_id = clean_text_value(sender.get('id'))
            text = clean_text_value(message.get('text'))
            message_id = clean_text_value(message.get('mid'))
            if fb_id and text:
                messages.append((fb_id, text, message_id))
    return messages


def clean_text_value(value):
    try:
        text_types = (basestring,)
    except NameError:
        text_types = (str,)

    if not isinstance(value, text_types):
        return None

    value = value.strip()
    return value or None


def clean_weather_location(value):
    value = clean_text_value(value)
    if value is None or len(value) > MAX_WEATHER_LOCATION_LENGTH:
        return None
    return value


def fb_message(sender_id, text):
    """
    Function for returning response to messenger
    """
    data = {
        'recipient': {'id': sender_id},
        'message': {'text': text}
    }
    # Send POST request to messenger
    resp = requests.post(
        FB_MESSAGES_URL,
        json=data,
        headers={'Authorization': 'Bearer {0}'.format(FB_PAGE_TOKEN or '')},
        timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.content


def get_weather(text):
    qs = {'q': text, 'appid': OPEN_WEATHER_TOKEN}
    try:
        resp = requests.get(OPEN_WEATHER_URL, params=qs, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as error:
        raise WeatherProviderError('Weather provider request failed.') from error
    try:
        data = resp.json()
    except (requests.RequestException, ValueError, RecursionError) as error:
        raise WeatherProviderError('Weather provider response was invalid.') from error
    if not isinstance(data, dict):
        return None
    weather = data.get('weather')
    if not isinstance(weather, list) or not weather:
        return None
    current = weather[0]
    if not isinstance(current, dict):
        return None
    return clean_text_value(current.get('main'))


def first_entity_value(entities, entity):
    """
    Returns first entity value
    """
    if not isinstance(entities, dict):
        return None

    values = entities.get(entity)
    if not isinstance(values, list) or not values:
        return None

    first_value = values[0]
    if not isinstance(first_value, dict):
        return None

    val = first_value.get('value')
    if isinstance(val, dict):
        val = val.get('value')
    return clean_text_value(val)


def send(request, response):
    """
    Sender function
    """
    # We use the fb_id as equal to session_id
    fb_id = request['session_id']
    context = request.get('context')
    if isinstance(context, dict) and context.get('missingForecast') is True:
        text = WEATHER_UNAVAILABLE_MESSAGE
    else:
        text = response['text']
    # send message
    fb_message(fb_id, text)


def get_forecast(request):
    context = request['context']
    entities = request['entities']
    loc = clean_weather_location(first_entity_value(entities, 'location'))
    if loc:
        # This is where we could use a weather service api to get the weather.
        try:
            conditions = get_weather(loc)
        except WeatherProviderError:
            conditions = None
        if conditions:
            context['forecast'] = conditions
            if context.get('missingForecast') is not None:
                del context['missingForecast']
            if context.get('missingLocation') is not None:
                del context['missingLocation']
        else:
            context['missingForecast'] = True
            if context.get('forecast') is not None:
                del context['forecast']
            if context.get('missingLocation') is not None:
                del context['missingLocation']
    else:
        context['missingLocation'] = True
        if context.get('forecast') is not None:
            del context['forecast']
        if context.get('missingForecast') is not None:
            del context['missingForecast']
    return context

# Setup Actions
actions = {
    'send': send,
    'getForecast': get_forecast,
}

# Setup Wit Client
client = Wit(access_token=WIT_TOKEN, actions=actions)

if __name__ == '__main__':
    # Run Server
    app.run(host='0.0.0.0', port=argv[1])
