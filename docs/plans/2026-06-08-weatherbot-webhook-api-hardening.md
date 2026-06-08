# Weatherbot Webhook And API Hardening Plan

Date: 2026-06-08

status: completed

## Goal

Make the Messenger weather bot safer to run by validating webhook payloads, keeping page tokens out of URLs, and bounding external API calls.

## Scope

- Reject invalid Messenger webhook JSON with a deterministic 400.
- Ignore unsupported Messenger events without calling Wit actions.
- Route supported sender/text message events to Wit through guarded field access.
- Send Facebook page tokens in the `Authorization` header instead of URL query strings.
- Add explicit timeouts to Messenger, OpenWeather, and Wit HTTP calls.
- Add dependency-free contract checks and local Makefile verification targets.

## TDD Notes

- Red: `python3 scripts/check_weatherbot_contracts.py` failed with `TypeError: 'NoneType' object is not subscriptable` for invalid webhook JSON.
- Red: after Messenger/OpenWeather hardening, the Wit timeout contract failed with `AssertionError: wit request timeout: expected 5, got None`.
- Green: `python3 scripts/check_weatherbot_contracts.py` passed with 6 webhook and API client contract checks.

## Verification

- `make lint`
- `make test`
- `make build`
- `make verify`
- `make check`
- `git diff --check`
- Legacy Python 2 `test_messenger` is skipped by `make test` in this environment when Python 2 dependencies are unavailable.
