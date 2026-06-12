# Weatherbot Wit Failure Isolation

## Status: Completed

## Context

Messenger webhook payloads can contain multiple text events. The handler calls
Wit synchronously for each event without containing expected provider failures.
If a later Wit request fails after an earlier event has already sent a reply,
the webhook returns an error and Messenger can retry the complete batch,
duplicating earlier side effects.

The bundled Wit client also lets `requests` transport errors and malformed JSON
escape outside its public `WitError` contract.

## Priority

Webhook delivery is at-least-once and reply actions are not idempotent. Expected
provider failures must be isolated to their event so one bad or transient Wit
response cannot amplify retries across an otherwise valid batch.

## Prioritized Engineering Backlog

1. Normalize expected Wit transport and response-decode failures and isolate
   them per Messenger text event now.
2. Add durable event-ID deduplication if the sample gains persistent storage.
3. Move provider work behind an asynchronous queue if the sample evolves into
   a production multi-user service.

## Requirements

- R1. Wit request transport failures and malformed JSON must raise `WitError`
  with stable text and preserve the original cause.
- R2. A `WitError` for one text event must not stop later text events in the
  same authenticated Messenger payload.
- R3. The webhook must acknowledge an authenticated valid page payload after
  isolating expected Wit failures to avoid batch retry amplification.
- R4. Unexpected programming exceptions must continue to propagate rather than
  being silently swallowed.
- R5. Failure handling must not log sender IDs, message text, tokens, URLs, or
  provider response bodies.
- R6. Tests, docs, and repository contracts must preserve the behavior.

## Implementation Units

### U1. Normalize Wit request failures

- **Files:** `wit.py`
- Wrap `requests.RequestException` and response JSON decode failures in stable
  `WitError` instances with exception chaining.

### U2. Isolate expected failures per event

- **Files:** `messenger.py`
- Catch only `WitError` around each `run_actions` call and continue processing
  the authenticated batch.

### U3. Add offline regressions and contracts

- **Files:** `test_messenger.py`, `scripts/check_weatherbot_contracts.py`,
  `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`
- Prove failed events do not block later events, valid batches are acknowledged,
  causes are retained, and unrelated exceptions still surface.

## Scope Boundaries

- Do not add persistent webhook deduplication or a background queue.
- Do not retry Wit requests inside the webhook process.
- Do not change signature verification, request size limits, or weather lookup
  fallback behavior.

## Verification

- `make check PYTHON=.venv/bin/python`
- `.venv/bin/python -m unittest test_messenger`
- `.venv/bin/python scripts/check_weatherbot_contracts.py`
- `.venv/bin/python -m pip check`
- `git diff --check`
- Mutations removing provider normalization, per-event continuation, or
  unexpected-error propagation must fail the regression suite.

Completed on 2026-06-12 with the full `make check` gate, focused route and
contract suites, dependency validation, and diff hygiene checks passing.
