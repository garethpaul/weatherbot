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

import os
import requests
import json
from sys import argv
from wit import Wit
from bottle import Bottle, request, debug

# Wit.ai parameters
WIT_TOKEN = os.environ.get('WIT_TOKEN')
# Messenger API parameters
FB_PAGE_TOKEN = os.environ.get('FB_PAGE_TOKEN')
# A user secret to verify webhook get request.
FB_VERIFY_TOKEN = os.environ.get('FB_VERIFY_TOKEN')
# Weather API
OPEN_WEATHER_TOKEN = os.environ.get('OPEN_WEATHER_TOKEN')
REQUEST_TIMEOUT = 10


def env_flag(name):
    return os.environ.get(name, '').lower() in ('1', 'true', 'yes', 'on')

# Setup Bottle Server
debug(env_flag('BOTTLE_DEBUG'))
app = Bottle()


# Facebook Messenger GET Webhook
@app.get('/webhook')
def messenger_webhook():
    """
    A webhook to return a challenge
    """
    verify_token = request.query.get('hub.verify_token')
    # check whether the verify tokens match
    if verify_token == FB_VERIFY_TOKEN:
        # respond with the challenge to confirm
        challenge = request.query.get('hub.challenge')
        return challenge
    else:
        return 'Invalid Request or Verification Token'


# Facebook Messenger POST Webhook
@app.post('/webhook')
def messenger_post():
    """
    Handler for webhook (currently for postback and messages)
    """
    data = request.json
    if not isinstance(data, dict):
        return 'Ignored Event'

    if data.get('object') != 'page':
        return 'Received Different Event'

    for fb_id, text in messenger_messages(data):
        client.run_actions(session_id=fb_id, message=text)

    return 'ok'


def messenger_messages(data):
    for entry in data.get('entry') or []:
        if not isinstance(entry, dict):
            continue
        for message in entry.get('messaging') or []:
            if not isinstance(message, dict):
                continue
            fb_id = (message.get('sender') or {}).get('id')
            text = (message.get('message') or {}).get('text')
            if fb_id and text:
                yield fb_id, text


def fb_message(sender_id, text):
    """
    Function for returning response to messenger
    """
    data = {
        'recipient': {'id': sender_id},
        'message': {'text': text}
    }
    # Send POST request to messenger
    resp = requests.post('https://graph.facebook.com/me/messages',
                         params={'access_token': FB_PAGE_TOKEN},
                         json=data,
                         timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.content


def get_weather(text):
    qs = {'q': text, 'appid': OPEN_WEATHER_TOKEN}
    resp = requests.get('https://api.openweathermap.org/data/2.5/weather',
                        params=qs,
                        timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = json.loads(resp.content)
    return str(data['weather'][0]['main'])


def first_entity_value(entities, entity):
    """
    Returns first entity value
    """
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
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
        conditions = get_weather(loc)
        context['forecast'] = conditions
        if context.get('missingLocation') is not None:
            del context['missingLocation']
    else:
        context['missingLocation'] = True
        if context.get('forecast') is not None:
            del context['forecast']
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
