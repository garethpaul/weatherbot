# Changes

## 2026-06-12

- Normalized Wit transport failures, provider errors, malformed JSON, and
  unexpected response shapes into stable `WitError` results without exposing
  provider details.
- Isolated expected Wit failures per Messenger event so later messages in the
  same authenticated batch still run and the valid webhook is acknowledged.
- Added dependency-free contracts and Bottle/WebTest regressions proving batch
  continuation, stable exception causes, and propagation of programming errors.

## 2026-06-10

- Normalized flat and nested Wit location values, rejecting malformed or
  non-text entity payloads instead of raising or querying OpenWeather with them.
- Limited unauthenticated Messenger webhook bodies to 1 MiB and reject both
  oversized declared and streamed payloads with HTTP 413 before Wit dispatch.
- Added dependency-free and Bottle/WebTest regressions, rooted Make execution,
  and a fixed Ubuntu 24.04 CI runner.
- Migrated the declared runtime from Python 2.7.11 to the Python 3.14 line.
- Upgraded Bottle to 0.13.4 and Requests to 2.34.2, pinned WebTest 3.0.7 as a
  test dependency, and removed unused Nose/Flake8 declarations.
- Updated the route suite for Python 3 response text and made `make test` use
  the configured Python interpreter.
- Added immutable-pinned Python 3.10/3.12/3.14 CI that installs dependencies
  and runs the complete static and runtime route suites.
- Required SHA-256 Messenger signatures before parsing webhook POST payloads.
- Added `.gitignore` exceptions so tracked GitHub workflow files remain
  visible despite the legacy broad dotfile ignore rule.

## 2026-06-09

- Rejected non-page Messenger webhook payloads with HTTP 400 before event
  parsing or Wit action handling.
- Added dependency-free contract coverage for Messenger object validation.
- Rejected blank or non-text Messenger sender IDs and trimmed accepted sender
  IDs before using them as Wit session IDs.
- Added dependency-free contract coverage for Messenger sender ID
  normalization.
- Treated OpenWeather lookup exceptions as missing forecasts instead of letting
  them abort forecast action handling.
- Added dependency-free contract coverage for weather lookup exception fallback.
- Replaced Wit request/response debug logs that included params or JSON payloads
  with generic endpoint traces.
- Added dependency-free contract coverage for Wit debug log privacy.
- Disabled Bottle debug mode by default and made it opt-in with
  `WEATHERBOT_DEBUG`.
- Added dependency-free contract coverage for debug-mode environment parsing.
- Rejected blank Messenger message text and trimmed accepted text before Wit
  action handling.
- Added dependency-free contract coverage for Messenger text normalization.
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
