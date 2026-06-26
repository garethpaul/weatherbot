# Weather Location Length Bound

Status: Completed

## Context

Wit location entities are normalized for shape and whitespace, but their text
length was not bounded before becoming the OpenWeather `q` parameter. A
provider response or signed webhook flow could therefore drive an unnecessarily
large outbound query up to the repository's broader request-body limit.

## Goals

- Bound normalized weather locations before outbound provider I/O.
- Preserve valid location text and existing missing-location behavior.
- Clear stale forecast state when an overlong value is rejected.
- Keep provider versions, credentials, and live integration behavior unchanged.

## Work Completed

- Added a 256-character weather-location limit.
- Added a dedicated normalization boundary before `get_weather`.
- Treat overlong values as missing locations without calling OpenWeather.
- Added runtime, dependency-free, documentation, and changelog contracts.

## Verification Completed

- The focused red regression proved a 257-character location reached
  `get_weather` before the implementation.
- The focused boundary and no-provider-call regressions passed.
- `make lint`, `make test`, `make build`, `make verify`, and `make check`
  passed with 62 dependency-free contracts and 44 runtime tests.
- Absolute-Makefile `make check` passed from an external working directory.
- Focused hostile mutations removing the limit, bypassing normalization,
  accepting 257 characters, restoring provider I/O, or removing maintained
  evidence were rejected.
- The hash-locked Python 3.14 environment passed `pip check`.
- Isolated Python compilation, generated-bytecode cleanup, and
  `git diff --check` passed.
