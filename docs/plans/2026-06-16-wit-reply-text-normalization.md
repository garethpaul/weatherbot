# Wit Reply Text Normalization

## Status: Planned

## Priority

P1 functional correctness. On every documented Python 3 runtime, the vendored
Wit action loop converts a normal Unicode reply to `bytes` before calling the
Messenger send action. Requests' JSON encoder cannot serialize bytes, so valid
Wit message responses fail before Messenger delivery.

## Problem

`Wit.__run_actions()` calls `.encode('utf8')` on the provider's `msg` field.
That was compatible with the repository's historical Python 2 origin but is
incorrect under Python 3. The existing send tests inject strings directly and
therefore do not cover the actual Wit-to-Messenger boundary.

## Approach

- Require Wit message replies to be nonblank text.
- Preserve normalized Unicode text instead of producing bytes.
- Raise the stable `WitError` for missing, non-text, or blank reply values.
- Add executable tests that drive `Wit.run_actions()` into the real send action
  and prove Unicode text remains JSON serializable.
- Extend dependency-free contracts, guidance, changelog, and completed evidence.

## Files

- `wit.py`
- `test_messenger.py`
- `scripts/check_weatherbot_contracts.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-16-wit-reply-text-normalization.md`

## Verification

- Preserve the pre-fix reproduction showing a bytes reply and JSON
  serialization failure.
- Run focused runtime tests and the full pinned package gate from the repository
  and an external directory.
- Reject mutations restoring byte encoding, accepting malformed replies,
  weakening executable/static tests, drifting guidance, or leaving the plan
  incomplete.
- Audit exact paths, generated artifacts, secrets, conflict markers, modes,
  binaries, large files, and whitespace.

## Scope Boundaries

- Do not change provider endpoints, credentials, API versions, action-loop
  limits, webhook authentication, Messenger payload shape, weather behavior,
  dependencies, or workflow configuration.
- Do not make live Wit.ai, Messenger, or OpenWeather requests.
- Keep PR #19 and its predecessors open and preserve base-first stack ordering.

## Success Criteria

- Valid Wit Unicode replies reach Messenger as `str` and serialize as JSON.
- Missing, non-text, and blank Wit replies fail with the stable public
  `WitError`.
- Python 3.10, 3.12, and 3.14 hosted lanes retain the same contract.

## Verification Completed

Pending implementation and bounded verification.
