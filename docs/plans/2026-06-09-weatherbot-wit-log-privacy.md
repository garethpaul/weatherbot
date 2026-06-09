# Weatherbot Wit Log Privacy

## Status: Completed

## Context

Bottle debug mode is disabled by default, but the local Wit client still logged
request parameters and response JSON at debug level. Those values can include
Messenger user text, session identifiers, entities, and generated replies when
debug logging is enabled during troubleshooting.

## Objectives

- Preserve Wit request and response behavior.
- Keep method and endpoint traces available for debugging.
- Stop logging request params or response JSON payloads.
- Extend dependency-free checks so message-bearing debug logs do not return.

## Work Completed

- Replaced Wit request debug logging with a generic method/endpoint trace.
- Replaced Wit response debug logging with a generic method/endpoint trace.
- Extended `scripts/check_weatherbot_contracts.py` with Wit log privacy checks
  and completed-plan coverage.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_weatherbot_contracts.py`
- `make check`
- `git diff --check`

## Follow-Up Candidates

- Add structured request IDs for troubleshooting without user message contents.
- Document recommended production log levels for webhook deployments.
