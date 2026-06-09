# Weatherbot Weather Result Shape

## Status: Completed

## Context

The Messenger webhook and Wit entity parsing paths were hardened, but
`get_weather` still indexed the OpenWeather response as
`data['weather'][0]['main']`. Missing, empty, or malformed weather results could
raise an exception or leave stale forecast context in place.

## Objectives

- Preserve successful OpenWeather lookups.
- Validate the OpenWeather response root before reading nested fields.
- Treat missing or malformed weather arrays as lookup failures.
- Clear stale forecast context when a known location has no usable weather
  result.
- Keep dependency-free contracts covering malformed weather payloads.

## Work Completed

- Added response-shape checks in `get_weather`.
- Returned `None` for malformed OpenWeather payloads instead of indexing nested
  fields directly.
- Added `missingForecast` handling in `get_forecast` for known-location lookup
  failures.
- Cleared stale `forecast` and `missingLocation` values when weather lookup
  fails for a known location.
- Extended `scripts/check_weatherbot_contracts.py` and updated README, VISION,
  and CHANGES.

## Verification

- `python3 scripts/check_weatherbot_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add user-visible fallback copy for `missingForecast` in Wit responses.
- Document OpenWeather configuration and local testing fixtures.
