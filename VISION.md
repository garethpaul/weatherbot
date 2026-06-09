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
- Keep Wit, Facebook, and weather tokens in environment variables
- Make weather lookup and response flow easy to trace
- Treat malformed Wit entities as missing user location
- Treat malformed OpenWeather results as missing forecasts
- Keep outbound request timeout configuration bounded and non-crashing
- Treat Python and API versions as legacy until documented

Next priorities:

- Add README setup notes for each token and webhook endpoint
- Add user-facing fallback text for weather lookup failures
- Avoid debug logging of user messages by default

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
- Live API tests as the only verification path

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
