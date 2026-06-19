# Messenger Message Replay Guard

Status: Completed

## Problem

Messenger can retry webhook deliveries with the same message ID. Weatherbot
currently forwards every valid text event to Wit.ai, so a retry can repeat bot
actions and outbound replies.

## Plan

1. Parse trimmed non-empty Messenger message IDs with each valid batch message.
2. Claim IDs before Wit.ai work in a bounded, process-local, thread-safe cache.
3. Acknowledge duplicate deliveries without repeating Wit.ai actions.
4. Release claims when Wit.ai work fails, including handled `WitError` failures,
   so provider retries can recover.
5. Preserve batch continuation, echo filtering, messages without usable IDs,
   signature validation, body limits, and malformed-event handling.
6. Add focused runtime and dependency-free contracts plus mutation coverage.
7. Document that replay claims do not span workers or process restarts.

## Verification

- Seven focused runtime tests and seven focused dependency-free contracts
  passed for suppression, batch continuation, no-ID and malformed-ID
  compatibility, bounded eviction, both failure-release branches, and source
  ordering.
- The full `make check` gate passed locally and from an external working
  directory with 43 dependency-free contracts and 25 runtime tests.
- Ten hostile mutations were rejected for ID parsing and tuple propagation,
  claim ordering, duplicate suppression, bounded storage, locking, both
  failure-release branches, and stale plan status.
- Python compilation, `git diff --check`, artifact review, and focused secret
  review passed.
- No live Messenger, Wit.ai, or OpenWeather request was performed.
