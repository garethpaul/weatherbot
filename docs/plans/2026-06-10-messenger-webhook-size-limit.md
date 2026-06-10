# Messenger Webhook Size Limit

Status: Completed

## Context

Weatherbot read the complete unauthenticated Messenger request body before
signature verification. A remote sender could therefore force unbounded memory
use without knowing the application secret.

## Changes

- Limited Messenger webhook bodies to 1 MiB.
- Rejected oversized declared lengths before reading request streams.
- Bounded actual reads to `limit + 1` for missing or dishonest length headers.
- Added dependency-free and Bottle/WebTest regression coverage.
- Rooted Make commands and fixed hosted runner and action release annotations.

## Verification

- `make check`
- `python3 -m py_compile scripts/check_weatherbot_contracts.py`
- Mutation checks for both body-limit paths, CI, and rooted Make execution
- `git diff --check`
