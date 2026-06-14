# Protect the Make Repository Root from Overrides

## Status: Planned

## Context

The Makefile-derived root anchors Messenger contracts, runtime tests, and
cleanup, but an ordinary assignment can be replaced from the command line and
redirect verification away from the reviewed checkout.

## Requirements

- Protect the Makefile-derived root with GNU Make's `override` directive.
- Preserve the configurable Python command and final rooted cleanup.
- Require exact protected root and Python lines in the dependency-free checker.
- Pass local, external-directory, and hostile-root full pinned gates.
- Reject root, checker, Python override, cleanup, and plan regressions.
- Preserve Messenger, Wit.ai, weather-provider, workflow, and dependency behavior.

## Verification Plan

- focused hosted/Makefile contract and Python compilation
- bounded local, external-directory, and hostile-root `make check`
- focused mutations and pinned dependency integrity
- workflow YAML, artifact, whitespace, and changed-line credential audits

## Scope Boundaries

- Do not alter runtime behavior, dependencies, workflows, or provider policy.
- Do not merge or close stacked pull requests without owner authorization.
