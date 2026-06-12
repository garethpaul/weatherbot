# Messenger JSON Content Type

Status: Completed

## Problem

The signed Messenger POST route bounds the raw body and verifies its HMAC, but
it does not require a JSON media type before Bottle parses `request.json`.
Missing, unrelated, or prefix-spoofed content types therefore reach an
ambiguous parsing boundary.

## Plan

1. Require `application/json` before reading, authenticating, or parsing the
   webhook body.
2. Accept case-insensitive media types with optional parameters.
3. Reject absent, unrelated, suffix, and prefix-spoofed values with HTTP 415.
4. Add dependency-free and Bottle/WebTest regressions.
5. Preserve body-size limits, signature verification, and per-message Wit
   failure isolation for valid requests.

## Verification

- Focused dependency-free media-type contracts passed.
- All 16 Bottle/WebTest `TestMessenger` cases passed under an isolated Python
  3.12 environment with pinned runtime and test dependencies.
- `make check` and an external-working-directory Make invocation passed 34
  dependency-free contracts and the 16-case runtime suite.
- Guard-removal, prefix-acceptance, and parameter-rejection mutations failed.
- Python compilation and `git diff --check` passed.
