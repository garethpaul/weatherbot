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
import math
import os
import requests
from sys import argv
from wit import Wit
from bottle import Bottle, request, response, debug

# Wit.ai parameters
WIT_TOKEN = os.environ.get('WIT_TOKEN')
# Messenger API parameters
FB_PAGE_TOKEN = os.environ.get('FB_PAGE_TOKEN')
# A user secret to verify webhook get request.
FB_VERIFY_TOKEN = os.environ.get('FB_VERIFY_TOKEN')
# Weather API
OPEN_WEATHER_TOKEN = os.environ.get('OPEN_WEATHER_TOKEN')
FB_MESSAGES_URL = 'https://graph.facebook.com/me/messages'
OPEN_WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'


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


# Facebook Messenger GET Webhook
@app.get('/webhook')
def messenger_webhook():
    """
    A webhook to return a challenge
    """
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

    left = str(left)
    right = str(right)
    compare_digest = getattr(hmac, 'compare_digest', None)
    if compare_digest:
        return compare_digest(left, right)

    if len(left) != len(right):
        return False

    result = 0
    for left_char, right_char in zip(left, right):
        result |= ord(left_char) ^ ord(right_char)
    return result == 0


# Facebook Messenger POST Webhook
@app.post('/webhook')
def messenger_post():
    """
    Handler for webhook (currently for postback and messages)
    """
    data = request.json
    if not isinstance(data, dict):
        response.status = 400
        return 'Invalid payload'

    if data.get('object') != 'page':
        # Returned another event
        return 'Received Different Event'

    for fb_id, text in messenger_text_messages(data):
        # Let's forward the message to the Wit.ai Bot Engine
        client.run_actions(session_id=fb_id, message=text)

    # must send back response quickly
    return 'ok'


def messenger_text_messages(data):
    """
    Extract supported Messenger sender/text pairs from a webhook payload.
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
            sender = event.get('sender') or {}
            message = event.get('message') or {}
            fb_id = clean_text_value(sender.get('id'))
            text = clean_text_value(message.get('text'))
            if fb_id and text:
                messages.append((fb_id, text))
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
    return resp.content


def get_weather(text):
    qs = {'q': text, 'appid': OPEN_WEATHER_TOKEN}
    resp = requests.get(OPEN_WEATHER_URL, params=qs, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, dict):
        return None
    weather = data.get('weather')
    if not isinstance(weather, list) or not weather:
        return None
    current = weather[0]
    if not isinstance(current, dict):
        return None
    main = current.get('main')
    if not main:
        return None
    return str(main)


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
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val


def send(request, response):
    """
    Sender function
    """
    # We use the fb_id as equal to session_id
    fb_id = request['session_id']
    text = response['text']
    # send message
    fb_message(fb_id, text)


def get_forecast(request):
    context = request['context']
    entities = request['entities']
    loc = first_entity_value(entities, 'location')
    if loc:
        # This is where we could use a weather service api to get the weather.
        try:
            conditions = get_weather(loc)
        except Exception:
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
