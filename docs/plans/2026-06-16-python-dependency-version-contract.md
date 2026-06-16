# Document Python and Dependency Versions

Status: Planned

## Context

Weatherbot already pins Bottle, Requests, and WebTest exactly and verifies the
repository on Python 3.10, 3.12, and 3.14. The roadmap still describes Python
and API versions as legacy until documented, so maintainers do not have one
stable statement that connects the manifests to the hosted compatibility
matrix.

## Goals

- Document the exact runtime and test dependency pins.
- Document Python 3.10, 3.12, and 3.14 as the verified compatibility matrix.
- Keep the matrix, manifest contents, and guidance mutation-sensitive.
- Remove the completed documentation item and legacy ambiguity from the vision.

## Non-Goals

- Do not change dependency versions or add a package manager.
- Do not claim compatibility with Python versions outside the hosted matrix.
- Do not claim a current Wit.ai, Messenger, or OpenWeather API-version contract
  without credential-backed integration verification.
- Do not change runtime behavior, provider requests, or deployment settings.

## Implementation

1. Add one canonical supported-version statement to README, security,
   contributor, vision, and changelog guidance.
2. Update the vision to distinguish verified Python/dependency versions from
   provider API versions that still require live review.
3. Extend `scripts/check_weatherbot_contracts.py` to preserve the exact
   manifests, hosted matrix, guidance, and completed plan.

## Validation

- Run the dependency-free contract suite and Bottle/WebTest route suite.
- Run repository and external-directory `make check` with the pinned packages.
- Reject mutations that change a runtime pin, test pin, Python matrix,
  guidance, completed status, or verification evidence.
- Audit the exact diff, Python syntax, artifacts, credentials, conflict markers,
  modes, and whitespace before commit.

## Risks

- Exact pins require deliberate updates when upstream security or compatibility
  releases are adopted.
- Provider API behavior remains environment-dependent and is not converted into
  an offline version guarantee by this documentation.
- PR #18 will be stacked on open PR #17 and requires base-first ordering;
  neither pull request may be merged or closed without explicit authorization.
