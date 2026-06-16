## Weatherbot Vision

Weatherbot is a Python chatbot for Facebook Messenger that uses Wit.ai for
intent handling and OpenWeather for forecast lookup.

The repository is useful as a compact webhook integration sample with Bottle,
Messenger verification, Wit actions, weather lookup, and screenshots.

The goal is to preserve the bot sample while making token handling, webhook
security, and user-message privacy explicit.

The current focus is:

Priority:

- Preserve Messenger webhook verification and message handling
- Bound unauthenticated Messenger request bodies before signature verification
- Keep Wit, Facebook, and weather tokens in environment variables
- Reject non-page Messenger webhook payloads before Wit action handling
- Reject blank or non-text Messenger sender IDs before Wit action handling
- Reject blank Messenger message text before Wit action handling
- Suppress retried Messenger message IDs before repeating Wit actions
- Process Messenger message batches in order with a fixed per-webhook cap
- Fail Messenger replies on provider HTTP errors so webhook retries remain
  recoverable
- Isolate expected Wit failures per Messenger event to avoid batch retry
  amplification after earlier replies
- Make weather lookup and response flow easy to trace
- Treat malformed Wit entities as missing user location
- Normalize flat and nested Wit location values before weather lookup
- Treat malformed OpenWeather results as missing forecasts
- Treat OpenWeather lookup exceptions as missing forecasts
- Send stable retry-later text when a known-location forecast is unavailable
- Keep outbound request timeout configuration bounded and non-crashing
- Keep Bottle debug mode disabled unless explicitly enabled locally
- Avoid debug logging user messages, entities, or Wit response payloads
- Keep provider credential ownership, HTTPS webhook wiring, and redacted
  verification evidence explicit
- Treat Python and API versions as legacy until documented

Next priorities:

- Document Python and dependency version constraints

Contribution rules:

- One PR = one focused webhook, action, weather API, test, or documentation change.
- Do not commit tokens, page IDs, or private messages.
- Keep live webhook behavior opt-in.
- Add mocks for external API changes.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Messenger bots process user messages and platform identifiers. The bot should
verify webhooks, keep tokens secret, minimize message logging, and make external
API calls explicit.

## What We Will Not Merge (For Now)

- Checked-in platform tokens
- Private conversation logs
- Unverified webhook processing
- Messenger webhook payloads that bypass page-object validation
- Unbounded webhook request bodies
- Live API tests as the only verification path

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
