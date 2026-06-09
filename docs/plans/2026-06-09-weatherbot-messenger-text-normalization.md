# Weatherbot Messenger Text Normalization

## Status: Completed

## Context

The Messenger webhook extractor guarded malformed event shapes, but any truthy
message text was forwarded to Wit.ai. Whitespace-only messages could still
exercise Wit actions, and padded text was sent without normalization.

## Objectives

- Preserve supported Messenger text routing to Wit actions.
- Ignore blank or whitespace-only Messenger message text.
- Trim accepted Messenger text before `client.run_actions`.
- Keep malformed non-text message values ignored.
- Cover the behavior in dependency-free route contracts.

## Work Completed

- Normalized `message.text` with `.strip()` inside `messenger_text_messages`.
- Ignored non-text values that do not support stripping.
- Skipped whitespace-only text without calling Wit actions.
- Added dependency-free tests for blank and trimmed Messenger message text.
- Updated README, VISION, and CHANGES.

## Verification

- Negative check: `python3 scripts/check_weatherbot_contracts.py` failed before
  Messenger text normalization was added.
- `python3 scripts/check_weatherbot_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add user-facing fallback text for weather lookup failures.
- Avoid debug logging of user messages by default.
