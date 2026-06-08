# Changes

## 2026-06-08

- Added a local `make verify` gate with dependency-free webhook and API client contract checks.
- Validated Messenger webhook JSON before reading nested message fields.
- Ignored unsupported Messenger delivery/read events without calling Wit actions.
- Sent Messenger page tokens in an authorization header instead of URL query strings.
- Added bounded request timeouts and status checks for outbound Messenger, Wit, and weather API calls.
