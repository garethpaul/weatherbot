# Weatherbot Verify Token Fails Closed Plan

Date: 2026-06-08

Status: Completed

## Goal

Make Messenger webhook verification fail closed when `FB_VERIFY_TOKEN` is
missing, wrong, or supplied without a challenge.

## Scope

- Reject webhook verification requests when the configured token is unset.
- Compare verify tokens without short-circuiting on partial matches.
- Return a deterministic 400 when a matching verify token omits `hub.challenge`.
- Add dependency-free checks for missing config, wrong tokens, matching tokens,
  and missing challenge handling.

## TDD Notes

- Red: `python3 scripts/check_weatherbot_contracts.py` failed with
  `missing configured verify token status: expected 403, got 200`.
- Green: `python3 scripts/check_weatherbot_contracts.py` passed after adding
  fail-closed token comparison and challenge validation.

## Verification

- `python3 scripts/check_weatherbot_contracts.py`
- `make check`
- `git diff --check`
