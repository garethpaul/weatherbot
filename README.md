# weatherbot

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/weatherbot` is a Python web API or service project. A chat bot for the weather

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: Python (3).

## Repository Contents

- `README.md` - project overview and local usage notes
- `requirements.txt` and `test-requirements.txt` - reviewable direct pins
- `requirements-py310.lock`, `requirements-py312.lock`, and
  `requirements-py314.lock` - complete SHA-256-locked dependency graphs
- `Procfile`
- `SECURITY.md` - security reporting and disclosure guidance
- `VISION.md` - project direction and maintenance guardrails

Additional scan context:

- Source directories: no top-level source directories detected
- Dependency and build manifests: Procfile, requirements.txt
- Entry points or build surfaces: none detected
- Test-looking files: test_messenger.py

## Getting Started

### Prerequisites

- Git
- Python 3.10 or newer; deployment tracks the Python 3.14 line
- Verified support covers Python 3.10, 3.12, and 3.14 with Bottle 0.13.4, Requests 2.34.2, and WebTest 3.0.7 pinned exactly.

### Setup

```bash
git clone https://github.com/garethpaul/weatherbot.git
cd weatherbot
python -m pip install --require-hashes -r requirements-py314.lock
```

Use `requirements-py310.lock` or `requirements-py312.lock` instead when the
active interpreter is Python 3.10 or 3.12.

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- Run `python messenger.py $PORT` after installing dependencies and setting the required tokens.

## Testing and Verification

- `make verify` runs syntax checks and dependency-free webhook, Wit action,
  Wit entity normalization, Messenger object validation, Messenger sender/text
  normalization, Messenger replay suppression and body size, OpenWeather shape,
  request timeout, outbound API, weather fallback, Wit failure-isolation, and
  Unicode reply normalization, malformed reply rejection, and Wit log-privacy
  contract checks.
- `make check` runs `make verify` with bytecode cleanup before and after.
- `python3 scripts/check_weatherbot_contracts.py` runs just the webhook and outbound API contracts.
- Completed maintenance plans live under `docs/plans` and are checked by
  `make check`.
- `python -m unittest test_messenger` runs the Bottle/WebTest route suite.
- `make lock` regenerates reviewed Python 3.10, 3.12, and 3.14 Linux lockfiles
  from the three direct pins in `requirements.txt` and
  `test-requirements.txt`.
- GitHub Actions installs the matrix-matched hash-locked dependency graph and runs
  `make check` on Python 3.10, 3.12, and 3.14 on Ubuntu 24.04 with read-only
  permissions and cancellation for superseded runs.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- See `PROVIDER_SETUP.md` for provider ownership, secret injection, the shared
  HTTPS `/webhook` GET/POST contract, optional settings, setup order, and
  redacted verification evidence.
- `WIT_TOKEN` configures Wit.ai access.
- `FB_PAGE_TOKEN` configures Facebook Messenger replies.
- `FB_VERIFY_TOKEN` configures Messenger webhook verification.
- Messenger GET verification requires the exact `subscribe` verification mode
  before the configured token and challenge are accepted.
- `FB_APP_SECRET` validates `X-Hub-Signature-256` on Messenger POST payloads.
- Messenger POST bodies are limited to 1 MiB before signature verification.
- Expected Wit transport and response failures are isolated to the affected
  Messenger event so later messages in an authenticated batch still run and
  the valid webhook can be acknowledged.
- Wit message replies remain normalized Unicode text through Messenger JSON
  serialization; missing, non-text, and blank replies fail with a stable error.
- Known-location weather lookup failures send a stable retry-later message
  instead of forwarding stale Wit forecast text or provider details.
- Recent non-empty Messenger message IDs are claimed in a bounded process-local
  cache so retries do not repeat Wit actions; failed actions release claims.
- Unsuccessful Messenger provider HTTP responses raise before reply content is
  accepted, allowing the current webhook message-ID claim to be retried.
- Signed Messenger batches process at most 20 valid user messages in payload
  order; malformed nested events and echoes do not hide later valid messages.
- `OPEN_WEATHER_TOKEN` configures OpenWeather lookup.
- `REQUEST_TIMEOUT` optionally overrides outbound request timeout seconds;
  invalid, non-finite, or non-positive values fall back to `5.0`.
- `WEATHERBOT_DEBUG=1` enables Bottle debug mode for local development; it is
  disabled by default.

## Security and Privacy Notes

- Hosted verification checks out source without persisting Git credentials.
- Review changes touching authentication or token handling; examples from the scan include messenger.py, wit.py.
- Review changes touching external API calls or credential-adjacent configuration; examples from the scan include messenger.py, wit.py.
- Review changes touching network requests, sockets, or service endpoints; examples from the scan include messenger.py, wit.py.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include messenger.py, test_messenger.py, wit.py.
- Review changes touching infrastructure, proxy, cloud, or deployment configuration; examples from the scan include messenger.py.

## Maintenance Notes

- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-weatherbot-webhook-api-hardening.md` for the
  current webhook and API client hardening baseline.
- See `docs/plans/2026-06-08-weatherbot-verify-token-fails-closed.md` for the
  Messenger verify-token fail-closed contract.
- See `docs/plans/2026-06-08-weatherbot-wit-entity-shape.md` for malformed Wit
  entity handling in forecast actions.
- See `docs/plans/2026-06-09-weatherbot-weather-result-shape.md` for malformed
  OpenWeather result handling.
- See `docs/plans/2026-06-09-weatherbot-weather-exception-fallback.md` for
  treating OpenWeather lookup exceptions as missing forecasts.
- See `docs/plans/2026-06-09-weatherbot-request-timeout.md` for bounded
  request timeout environment parsing.
- See `docs/plans/2026-06-09-weatherbot-debug-mode.md` for the opt-in Bottle
  debug-mode guard.
- See `docs/plans/2026-06-09-weatherbot-messenger-text-normalization.md` for
  blank Messenger text rejection and trim behavior before Wit calls.
- See `docs/plans/2026-06-09-weatherbot-messenger-sender-normalization.md` for
  blank or non-text Messenger sender ID rejection before Wit calls.
- See `docs/plans/2026-06-09-weatherbot-messenger-object-guard.md` for
  rejecting non-page Messenger webhook payloads before Wit calls.
- See `docs/plans/2026-06-09-weatherbot-wit-log-privacy.md` for Wit request
  and response debug log privacy coverage.
- See `docs/plans/2026-06-10-python3-runtime-and-ci.md` for the Python 3
  dependency, route-test, and hosted verification baseline.
- See `docs/plans/2026-06-10-messenger-webhook-size-limit.md` for the completed
  unauthenticated request-body limit.
- See `docs/plans/2026-06-10-weatherbot-wit-entity-normalization.md` for
  malformed nested entity rejection and location text normalization.
- See `docs/plans/2026-06-12-messenger-json-content-type.md` for the exact JSON
  media-type requirement on signed Messenger webhook requests.
- See `docs/plans/2026-06-12-messenger-challenge-plain-text.md` for the
  reflected-XSS-safe verification challenge response contract.
- See `docs/plans/2026-06-13-messenger-echo-guard.md` for ignoring page echo
  events without hiding later user messages in the same webhook batch.
- See `docs/plans/2026-06-13-messenger-message-replay-guard.md` for bounded
  process-local retry suppression and per-message failure recovery.
- See `docs/plans/2026-06-13-messenger-batch-processing-bound.md` for ordered,
  bounded Messenger batch handling and malformed-event isolation.
- See `docs/plans/2026-06-14-provider-setup-guide.md` for provider credential,
  endpoint, and redacted verification guidance.
- See `docs/plans/2026-06-15-messenger-reply-http-status.md` for Messenger
  provider HTTP failure handling and replay-claim recovery.
- See `docs/plans/2026-06-16-weather-failure-user-message.md` for the stable
  user-facing reply when a known-location weather lookup is unavailable.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
