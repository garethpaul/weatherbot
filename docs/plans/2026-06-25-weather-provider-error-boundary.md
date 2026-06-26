---
title: Weather Provider Error Boundary
date: 2026-06-25
type: implementation-plan
status: completed
---

# Weather Provider Error Boundary

## Problem

`get_forecast` caught every `Exception` raised by `get_weather`. That preserved
the user-facing fallback for provider outages but also converted programming
defects into ordinary missing forecasts, hiding failures from the webhook retry
and diagnostic path.

## Requirements

- Preserve missing-forecast behavior for Requests transport, timeout, HTTP
  status, and decoding failures.
- Preserve fallback behavior for provider-controlled JSON parsing failures that
  surface as `ValueError` or `RecursionError` on supported Python versions.
- Translate those failures at the `get_weather` ownership boundary into one
  domain-specific error.
- Catch only that domain error in `get_forecast`.
- Let unrelated application exceptions propagate through the existing webhook
  claim-release and retry path.

## Verification

- RED: an injected `RuntimeError` was swallowed and converted to
  `missingForecast`.
- Focused runtime tests cover translated provider failure, plain parser failures,
  and unexpected-error propagation.
- Dependency-free contracts model the provider error and reject restoring the
  broad catch.
- Canonical and external-root `make check` pass with 61 dependency-free
  contracts and 42 runtime tests; the pinned environment also passes `pip check`.
- Four hostile mutations restoring the broad catch or removing transport,
  `ValueError`, or `RecursionError` translation are rejected.
- Independent review, exact-head Codex review, and hosted CI remain required
  before merge.
