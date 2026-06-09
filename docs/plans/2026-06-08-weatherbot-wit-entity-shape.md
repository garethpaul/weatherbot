# Weatherbot Wit Entity Shape

## Status: Completed

## Context

The forecast action assumed Wit.ai always returned `entities["location"][0]`
with a dictionary-shaped value. Missing or malformed entity payloads could raise
while handling a Messenger webhook instead of taking the existing
missing-location path.

## Objectives

- Preserve the existing Wit forecast action behavior for valid locations.
- Treat missing or malformed entities as no location found.
- Clear stale forecasts when entity parsing cannot produce a location.
- Cover the behavior in dependency-free checks under `make check`.

## Work Completed

- Hardened `first_entity_value` against missing, non-dictionary, empty, and
  non-list entity payloads.
- Preserved support for both flat and nested Wit entity values.
- Added contract tests for malformed entity payloads and missing-entity
  forecast handling.
- Updated README, VISION, and CHANGES with the new guardrail.

## Verification

- `python3 scripts/check_weatherbot_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Validate OpenWeather JSON response shape before reading `weather[0].main`.
- Add user-facing fallback text when weather lookup fails.
