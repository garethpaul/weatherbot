# Changes

## 2026-06-09

- Disabled Bottle debug mode by default and made it opt-in with
  `WEATHERBOT_DEBUG`.
- Added dependency-free contract coverage for debug-mode environment parsing.
- Added safe `REQUEST_TIMEOUT` parsing for Messenger, Wit, and OpenWeather
  requests so invalid, non-finite, or non-positive values fall back to five
  seconds.
- Added dependency-free contract coverage for request timeout parsing.
- Validated OpenWeather response shape before reading conditions and returned a
  missing forecast state for malformed weather payloads.
- Added dependency-free contract coverage for malformed weather results and
  stale forecast clearing.

## 2026-06-08

- Treated missing or malformed Wit location entities as missing-location
  forecast input instead of raising during webhook handling.
- Made Messenger webhook verification fail closed when the verify token is unset or the challenge is missing.
- Tightened docs-plan verification to require recorded `make check` evidence.
- Added a local `make verify` gate with dependency-free webhook and API client contract checks.
- Validated Messenger webhook JSON before reading nested message fields.
- Ignored unsupported Messenger delivery/read events without calling Wit actions.
- Sent Messenger page tokens in an authorization header instead of URL query strings.
- Added bounded request timeouts and status checks for outbound Messenger, Wit, and weather API calls.
