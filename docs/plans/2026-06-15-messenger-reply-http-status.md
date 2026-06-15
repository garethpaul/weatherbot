# Fail Messenger Replies on Provider HTTP Errors

## Status: Completed

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

## Work Completed

- Added an explicit provider HTTP status check before Messenger reply content is
  accepted.
- Added dependency-free and Bottle/WebTest regressions proving provider HTTP
  errors propagate through Wit actions and release replay claims.
- Added fail-closed source-order, runtime-test, documentation, and completed-plan
  contracts, plus operator and security documentation.

## Verification

- Focused HTTP-status contracts passed 3 tests, and the dependency-free suite
  passed 49 tests.
- Repository and external-directory `make check` passed under pinned Python
  3.12, with 49 contracts and 28 runtime tests in each run.
- Five targeted behavior and documentation mutations were rejected before plan
  completion; the completed-plan mutation was then rejected separately.
- `uv pip check` passed for all 13 installed packages. Direct `pip-audit` runs
  found no known vulnerabilities in runtime or test requirements; the private
  WebOb build was explicitly reported as unavailable on PyPI and unauditable.
- A broader disposable-environment audit found vulnerabilities only in that
  environment's `pip 24.3.1`, which is tooling and is not a repository pin.
