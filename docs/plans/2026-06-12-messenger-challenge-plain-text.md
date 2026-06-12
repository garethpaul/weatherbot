# Messenger Challenge Plain Text

Status: Completed

## Problem

The verified Messenger GET webhook reflects Meta's `hub.challenge` value.
Bottle's default response type can allow that untrusted value to be interpreted
as HTML, which CodeQL reports as reflected server-side cross-site scripting.

## Plan

1. Mark every verification endpoint response as UTF-8 plain text.
2. Preserve exact challenge echoing for valid verification requests.
3. Add dependency-free and Bottle/WebTest response-type regressions.
4. Require the completed plan and response contract in the canonical checker.

## Verification

- Focused dependency-free verification challenge contract
- Focused Bottle/WebTest verification route test
- Local and external `make check`
- Plain-text response mutation
- Python compilation and `git diff --check`
- Exact-head CodeQL verification with the reflected-XSS alert resolved
