# Python 3 Runtime and Hosted Verification

Status: Completed

## Problem

The service still declared Python 2.7.11 and 2016-era dependencies. Portable
Python 3 contracts passed, but `make check` skipped the five dependency-backed
Bottle/WebTest route tests unless a legacy Python 2 environment happened to be
installed.

## Plan

1. Prove the existing application and route suite on current Python 3 packages.
2. Pin Bottle, Requests, and WebTest to current verified releases and remove
   unused Nose/Flake8 declarations.
3. Update deployment metadata to the Python 3.14 line and make runtime tests
   mandatory under the configured interpreter.
4. Add least-privilege immutable-pinned CI on Python 3.10, 3.12, and 3.14 that installs
   dependencies and runs the complete gate.
5. Require Messenger SHA-256 webhook signatures before parsing POST payloads.
6. Add dependency/runtime/workflow drift contracts.

## Verification

- Fresh Python 3.12 virtual environment
- `make check` with 27 dependency-free checks and 6 unittest cases
- `python -m pip check`
- Direct-version OSV queries
- Negative stale-runtime and writable-workflow mutations rejected
- `git diff --check`
