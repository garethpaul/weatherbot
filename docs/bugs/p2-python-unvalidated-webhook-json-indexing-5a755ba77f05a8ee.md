# [P2] Validate webhook JSON before indexing nested message fields

## Severity

P2 - correctness/api

## Evidence

- `messenger.py:63`: `data = request.json`
- `messenger.py:64`: `if data['object'] == 'page':`
- `messenger.py:65`: `for entry in data['entry']:`
- `messenger.py:67`: `messages = entry['messaging']`
- `messenger.py:73`: `fb_id = message['sender']['id']`
- `messenger.py:75`: `text = message['message']['text']`

## Problem

The webhook handler reads `request.json` and immediately indexes nested fields such as `entry`, `messaging`, `message`, or `text`. Normal webhook traffic can include verification, postback, delivery, read, malformed, or missing-message events, so those requests can raise `KeyError` or `TypeError` and return 500 instead of a stable acknowledgement.

## Suggested fix

Check that the payload is a dictionary, validate the expected object and messaging shape with `.get()` or schema checks, gracefully ignore unsupported event types, and return a deterministic 2xx/4xx response instead of indexing missing keys.

## Review metadata

- Repository: `garethpaul/weatherbot`
- Reviewed commit: `d20875ef924562c8daf51248ed401f4794ebef4e`
- Labels: `bug`, `codex-review`, `severity:P2`
- Codex review fingerprint: `5a755ba77f05a8ee`
