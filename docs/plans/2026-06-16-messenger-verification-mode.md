# Require Messenger Subscription Verification Mode

Status: Planned

## Context

The Messenger GET webhook validates the configured verify token and requires a
challenge, but it does not validate `hub.mode`. A request carrying the correct
secret can therefore receive the verification challenge even when it is not an
explicit subscription-verification request.

## Requirements

- Require `hub.mode` to equal `subscribe` before returning a challenge.
- Fail closed for missing, non-text, differently cased, or whitespace-padded
  mode values without echoing the challenge.
- Preserve constant-time verify-token comparison, missing-challenge handling,
  and the plain-text challenge response.
- Add Bottle/WebTest and dependency-free regressions plus mutation-sensitive
  static contracts and maintained provider guidance.
- Keep POST webhook authentication and provider behavior unchanged.

## Implementation Units

### U1. Validate verification intent

- **File:** `messenger.py`
- Reject any GET verification request whose exact mode is not `subscribe`.

### U2. Prove fail-closed behavior

- **Files:** `test_messenger.py`, `scripts/check_weatherbot_contracts.py`
- Cover accepted subscription verification and rejected missing or malformed
  mode values, including checker registration and ordering contracts.

### U3. Maintain operational guidance

- **Files:** `PROVIDER_SETUP.md`, `README.md`, `SECURITY.md`, `VISION.md`,
  `CHANGES.md`
- Document the exact subscription-verification requirement.

## Verification

- Run focused route and dependency-free tests, then repository and external-
  directory non-cleaning verification with explicit timeouts.
- Reject mutations that remove or weaken mode validation, move it after token
  or challenge handling, remove runtime/static coverage, weaken guidance, or
  reopen the plan.
- Audit exact paths, generated artifacts, conflicts, file modes, whitespace,
  and credential-like additions before committing.

## Runtime Boundary

All verification requests are synthetic. No Meta, Wit.ai, OpenWeather, or live
credential interaction is performed.
