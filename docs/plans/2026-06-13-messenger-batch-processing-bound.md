# Bound Messenger Batch Processing

Status: Planned

## Problem

Weatherbot processes every valid Messenger event in a webhook payload. A
signed payload can therefore amplify into an unbounded number of Wit.ai action
calls within the existing 1 MiB body limit. The extractor also assumes nested
`sender` and `message` values are objects, so malformed later events can abort
the whole batch.

## Requirements

1. Process no more than 20 valid user messages from one webhook in payload
   order.
2. Ignore malformed entries, event arrays, events, sender objects, message
   objects, and boolean-true echoes without hiding later valid messages.
3. Preserve per-message replay claims, ID-less compatibility, Wit failure
   isolation, and unexpected-exception propagation.
4. Add executable and dependency-free coverage plus hostile mutations for the
   cap, ordering, malformed nested events, replay continuation, and failure
   cleanup.
5. Document the operational boundary and keep all live provider calls mocked.

## Implementation

- Add a named per-webhook message cap beside the existing body and replay
  limits.
- Validate nested event shapes before field access and return as soon as the
  valid-message cap is reached.
- Extend runtime tests, portable contracts, maintenance documentation, and
  completed-plan registration without new dependencies.

## Verification

- Run focused batch tests and hostile mutations under explicit timeouts.
- Run local and external-working-directory `make check` under explicit
  timeouts.
- Audit Python syntax, workflow YAML, intended paths, generated artifacts,
  conflict markers, whitespace, and changed-line credential patterns.
- Do not use live Messenger, Wit.ai, or OpenWeather credentials or requests.

## Scope Boundaries

- Do not add queues, parallel processing, distributed replay storage, retries,
  or provider API changes.
- Do not merge or close any pull request without explicit owner authorization.
