# Messenger Message Replay Guard

Status: In Progress

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

- Run focused suppression, batch, no-ID, malformed-ID, bounded-eviction, and
  failure-release tests.
- Run the full `make check` gate locally and from an external working
  directory.
- Reject hostile mutations for parsing, claim ordering, suppression, bounded
  storage, failure release, locking, and stale plan status.
- Run Python compilation, `git diff --check`, artifact review, and focused
  secret review.
- Do not perform live Messenger, Wit.ai, or OpenWeather requests.
