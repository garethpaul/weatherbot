# Changes

## 2026-06-08

- Treated missing or malformed Wit location entities as missing-location
  forecast input instead of raising during webhook handling.
- Made Messenger webhook verification fail closed when the verify token is unset or the challenge is missing.
- Tightened docs-plan verification to require recorded `make check` evidence.
- Added a local `make verify` gate with dependency-free webhook and API client contract checks.
- Validated Messenger webhook JSON before reading nested message fields.
- Ignored unsupported Messenger delivery/read events without calling Wit actions.
- Sent Messenger page tokens in an authorization header instead of URL query strings.
- Added bounded request timeouts and status checks for outbound Messenger, Wit, and weather API calls.
