# Root-Independent Cleanup

Status: Completed

## Problem

The Makefile roots lint and test commands, but the final `make clean` recursion
uses the caller's working directory. Invoking the canonical gate through an
absolute Makefile path from outside the repository therefore passes all tests
and then fails because the caller has no `clean` target.

## Plan

1. Reinvoke cleanup through the repository Makefile path.
2. Extend the portable checker to require rooted recursive cleanup.
3. Verify the complete gate from both repository and external directories.

## Verification

- Repository-local `make check`
- External-working-directory `make -f /absolute/path/Makefile check`
- Rooted-cleanup mutation
- Python compilation and `git diff --check`
