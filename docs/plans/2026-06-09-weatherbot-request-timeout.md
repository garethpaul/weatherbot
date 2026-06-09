# Weatherbot Request Timeout Parsing

## Status: Completed

## Context

`messenger.py` and `wit.py` parsed `REQUEST_TIMEOUT` with direct `float(...)`
calls during module import. Invalid values could crash startup, while zero,
negative, NaN, or infinite values could produce unusable outbound request
timeouts.

## Objectives

- Preserve positive numeric timeout overrides.
- Fall back to the default timeout for invalid env values.
- Reject zero, negative, NaN, and infinite timeout values.
- Cover both Messenger/OpenWeather and Wit timeout parsing.

## Work Completed

- Added bounded positive finite timeout parsing in `messenger.py`.
- Added the same timeout parsing guard in `wit.py`.
- Added dependency-free import-time checks for valid and invalid
  `REQUEST_TIMEOUT` values.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_weatherbot_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add user-facing fallback text for weather lookup failures.
- Avoid debug logging of user messages by default.
