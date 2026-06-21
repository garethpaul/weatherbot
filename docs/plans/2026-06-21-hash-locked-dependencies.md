# Hash-Lock Supported Python Dependency Graphs

## Status: Completed

## Context

The runtime and test manifests pinned Bottle, Requests, and WebTest exactly,
but hosted installs still resolved mutable transitive versions and accepted
unreviewed distribution artifacts. The same source commit could therefore
produce a different environment after an upstream release.

## Requirements

- Keep `requirements.txt` and `test-requirements.txt` as reviewable direct-pin
  inputs.
- Generate complete Python 3.10, 3.12, and 3.14 Linux dependency graphs with
  SHA-256 hashes from the public PyPI index.
- Install the matrix-matched lockfile with pip `--require-hashes` in CI.
- Provide one deterministic `make lock` regeneration command for all three
  supported interpreters.
- Verify complete-file digests, exact package sets, direct pins, and artifact
  hashes in the dependency-free contract gate.

## Scope Boundaries

- Do not change Weatherbot request, webhook, provider, or response behavior.
- Do not load provider credentials or perform live provider requests.
- Do not add dependency upgrades beyond the versions resolved from the current
  direct pins at lock-generation time.

## Verification

- Fresh Python 3.10, 3.12, and 3.14 environments installed their matching
  lockfile with `--require-hashes`, passed `pip check`, and imported Bottle,
  Requests, and WebTest.
- Repository and external-directory `make check` passed 59 dependency-free
  contracts and 37 Bottle/WebTest route tests.
- Lockfile-regeneration, matrix-selection, hash-removal, package-version,
  completed-plan, and documentation mutations were rejected.
- Workflow YAML, Python syntax, lockfile digests, artifact, diff, and
  changed-line credential audits passed.
