# Weatherbot Messenger Object Guard

Status: Completed

## Context

The Messenger POST route already rejects malformed JSON and ignores unsupported
page events without calling Wit. Non-page webhook objects still returned a
success-shaped HTTP 200 response, which made unrelated payloads look like
accepted Messenger webhook traffic.

## Plan

- Return HTTP 400 for Messenger POST payloads whose top-level `object` is not
  `page`.
- Stop before event parsing or Wit action calls for non-page payloads.
- Add a dependency-free contract for the non-page payload path.

## Verification

- `python3 scripts/check_weatherbot_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

Legacy Python 2 `test_messenger` still runs only when Python 2 and the
historical dependencies are installed; otherwise the Makefile reports the skip.
