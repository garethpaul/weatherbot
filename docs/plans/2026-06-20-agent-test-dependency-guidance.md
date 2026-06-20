# Agent Test Dependency Guidance

## Status

Completed on 2026-06-20.

## Problem

`AGENTS.md` documented installing only `requirements.txt`, but the repository's
`make check` gate imports WebTest from `test-requirements.txt`. A clean
environment following the agent instructions therefore could not run the
documented verification command.

## Change

- Update the agent setup command to install both runtime and test requirements.
- Extend the dependency contract so future guidance cannot omit the test
  dependency manifest.

## Verification

- Run the contract once before the guidance fix and confirm it fails.
- Run `make check` in a clean Python environment after the fix.
- Repeat the gate from an external working directory with a hostile `ROOT`
  override.
