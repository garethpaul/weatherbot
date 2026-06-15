# Fail Messenger Replies on Provider HTTP Errors

## Status: In Progress

## Context

The Messenger reply client applies a timeout and bearer authentication, but it
returns the provider response body without checking the HTTP status. A 4xx or
5xx response is therefore treated as successful, so the enclosing Wit action
does not raise and the webhook's message-ID claim remains consumed.

## Requirements

- Raise on unsuccessful Messenger provider responses before accepting reply
  content.
- Preserve timeout, header authentication, successful response behavior, and
  the existing Wit action boundary.
- Prove that a provider HTTP error propagates through the Wit action and releases
  the webhook replay claim for a later delivery.
- Add fail-closed source, runtime-test, documentation, and plan contracts.

## Verification Plan

- focused Messenger reply and replay contracts
- hostile removal, ordering, fake-response, runtime-test, documentation, and
  plan-status mutations
- repository and external-directory `make check` with bounded execution
- dependency integrity, exact diff, artifact, and credential-pattern audits

## Scope Boundaries

- Do not add automatic provider retries or change provider endpoints or tokens.
- Do not merge or close stacked pull requests without owner authorization.

## Work Pending

- Add the provider HTTP status boundary and mutation-sensitive regressions.
- Update operator and security documentation.
- Run the bounded verification and record the actual evidence.
