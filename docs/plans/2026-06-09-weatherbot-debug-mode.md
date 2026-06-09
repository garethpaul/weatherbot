# Weatherbot Debug Mode

## Status: Completed

## Context

The Bottle app enabled debug mode unconditionally during import. Debug behavior
is useful during local development, but webhook services process user messages,
platform identifiers, and token-protected routes, so debug mode should be
opt-in instead of the default runtime posture.

## Objectives

- Preserve an easy way to enable Bottle debug mode locally.
- Keep debug mode disabled by default.
- Parse the debug flag from an explicit environment variable.
- Cover default, truthy, and falsey debug flag values in dependency-free tests.

## Work Completed

- Added `truthy_env` to parse `WEATHERBOT_DEBUG`.
- Replaced unconditional `debug(True)` with `debug(truthy_env("WEATHERBOT_DEBUG"))`.
- Extended `scripts/check_weatherbot_contracts.py` to capture Bottle debug
  calls during module import.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_weatherbot_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add user-facing fallback text for weather lookup failures.
- Avoid debug logging of user messages in Wit request traces unless explicitly
  enabled for local troubleshooting.
