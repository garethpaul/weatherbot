# Weatherbot Runtime Hardening

## Context

Repo-local findings and GitHub issues report plain HTTP, debug mode, token-in-query URLs, missing timeouts, and unsafe Messenger webhook JSON indexing.

## Plan

1. Gate Bottle debug mode behind `BOTTLE_DEBUG`.
2. Use HTTPS for OpenWeather calls.
3. Add explicit timeouts and status checks to outbound HTTP calls.
4. Send Facebook page tokens as request parameters at call time instead of building tokenized URLs.
5. Validate Messenger webhook JSON shape before indexing nested fields.
6. Add a source-level baseline guard and remove resolved repo-local bug files.

## Verification

- Run `scripts/check-baseline.sh`.
- Run the scanner against this repo.
- Run `git diff --check`.
