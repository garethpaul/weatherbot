# Weatherbot Weather Exception Fallback

## Status: Completed

## Context

`get_weather` raises on outbound request status failures and can also raise
while decoding or handling external API responses. The forecast action already
treated malformed weather payloads as missing forecasts, but exceptions from
the lookup path could still abort action handling instead of updating the
existing missing-forecast state.

## Objectives

- Preserve successful OpenWeather lookups.
- Treat lookup exceptions as missing forecasts for known locations.
- Clear stale forecast and missing-location state on lookup failure.
- Extend dependency-free checks so exception fallback remains covered.

## Work Completed

- Wrapped the `get_weather` call in `get_forecast` with exception fallback.
- Reused the existing missing-forecast state path when lookup exceptions occur.
- Extended `scripts/check_weatherbot_contracts.py` with exception fallback
  coverage and completed-plan coverage.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_weatherbot_contracts.py`
- `make check`
- `git diff --check`

## Follow-Up Candidates

- Add user-facing fallback text that distinguishes unavailable weather from a
  missing location.
- Document production retry/backoff expectations for OpenWeather failures.
