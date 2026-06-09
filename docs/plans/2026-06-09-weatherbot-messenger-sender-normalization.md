# Weatherbot Messenger Sender Normalization

## Status: Completed

## Context

Messenger text normalization trimmed message text before Wit action handling,
but sender IDs were only checked for truthiness. Whitespace-only, padded, or
non-text sender IDs could still be passed to Wit as session IDs.

## Objectives

- Preserve supported Messenger sender/text routing to Wit actions.
- Ignore missing, blank, or non-text Messenger sender IDs.
- Trim accepted sender IDs before calling `client.run_actions`.
- Keep message text normalization behavior unchanged.
- Cover the behavior in dependency-free route contracts.

## Work Completed

- Added a shared text normalizer for Messenger sender IDs and message text.
- Ignored non-text and blank sender IDs before Wit action handling.
- Trimmed accepted sender IDs before using them as Wit session IDs.
- Added dependency-free tests for invalid and trimmed sender IDs.
- Updated README, SECURITY, VISION, and CHANGES.

## Verification

- `python3 scripts/check_weatherbot_contracts.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
