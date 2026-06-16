# Weatherbot Provider And Webhook Setup

## Required Credentials

Create and inject each value through the deployment platform's secret manager or
environment configuration. Do not put values in this repository, command
examples, screenshots, logs, issue text, or pull-request descriptions.

| Variable | Owner | Purpose |
| --- | --- | --- |
| `WIT_TOKEN` | Wit.ai app | Authorizes intent and action requests. |
| `FB_PAGE_TOKEN` | Meta Messenger page | Authorizes replies through the Messenger Send API. |
| `FB_VERIFY_TOKEN` | Operator-chosen secret | Must match the token Meta sends during webhook verification. |
| `FB_APP_SECRET` | Meta app | Verifies the `X-Hub-Signature-256` HMAC on Messenger POST bodies. |
| `OPEN_WEATHER_TOKEN` | OpenWeather account | Authorizes current-weather lookups. |

Keep the Messenger verify token, app secret, and page token distinct. Rotate a
credential at its provider and deployment secret store together, then repeat the
redacted verification steps below.

## Callback Endpoint

Deploy the Bottle process behind a public HTTPS origin and configure this exact
callback URL in the Meta app:

```text
https://<public-host>/webhook
```

Both Messenger operations use `/webhook`:

- `GET /webhook` handles subscription verification. Meta supplies the exact
  `hub.mode=subscribe`, `hub.verify_token`, and `hub.challenge`; Weatherbot
  returns the challenge as plain text only when the mode and configured verify
  token match.
- `POST /webhook` handles events. It requires `Content-Type: application/json`,
  a valid `X-Hub-Signature-256` generated with `FB_APP_SECRET`, a body no larger
  than 1 MiB, and a top-level Messenger object of `page`.

Do not expose a direct HTTP-only callback. TLS termination may occur at the
deployment platform, but the provider-facing callback must be HTTPS.

## Optional Settings

- `PORT` selects the Bottle listener port passed to `messenger.py`.
- `REQUEST_TIMEOUT` sets a positive finite outbound timeout in seconds; invalid
  values use `5.0`.
- `WEATHERBOT_DEBUG=1` enables Bottle debug mode for local development only.
- `WIT_URL` and `WIT_API_VERSION` override the legacy Wit endpoint and API
  version for an intentional compatibility test.

Do not enable debug mode in a public deployment or change provider origins
without a separate security review.

## Setup Order

1. Create the Wit.ai app, Meta app/page, and OpenWeather account.
2. Create or retrieve the five required credentials and inject them through the
   deployment secret store without printing them.
3. Deploy `python messenger.py $PORT` behind the public HTTPS origin.
4. Register `https://<public-host>/webhook` in Meta, using the same
   `FB_VERIFY_TOKEN` value in Meta and the deployment environment.
5. Subscribe the page to message events only after GET verification succeeds.
6. Run `make check` locally or in CI before any optional live provider test.

## Redacted Verification Record

Record the commit SHA, review date, reviewer, public callback hostname, provider
names, and pass/fail status for these checks:

- GET verification succeeds with exact subscription mode and the matching
  verify token, and rejects a missing or malformed mode or mismatched token
  without echoing the challenge.
- Unsigned, incorrectly signed, non-JSON, oversized, and non-page POST requests
  are rejected before Wit actions.
- A synthetic signed event passes the offline route suite without real user
  identifiers, page IDs, conversation text, or provider credentials.
- Optional live checks, when explicitly authorized, confirm one Wit intent, one
  OpenWeather lookup, and one Messenger reply while retaining only redacted
  pass/fail evidence.

Never attach raw webhook payloads, conversation logs, provider responses,
authorization headers, signatures, tokens, page IDs, or user identifiers.
Unresolved verification or credential-boundary failures block deployment.
