# Messenger Echo Guard

Status: Completed

## Problem

Messenger marks page-generated messages with boolean `message.is_echo`.
Weatherbot currently forwards those events to Wit as user input, which can
create reply loops and consume external API capacity. Echoes can also precede
valid user messages in the same webhook batch.

## Plan

1. Ignore only events whose echo flag is the JSON boolean `true`.
2. Continue scanning the batch so later user messages still reach Wit.
3. Add dependency-free and Bottle/WebTest regression coverage.
4. Preserve existing sender/text normalization and per-message Wit failure
   isolation.

## Verification

- The focused Bottle/WebTest echo route test passed.
- The full `make check` gate passed 36 dependency-free contracts and all 18
  Bottle/WebTest runtime tests under an isolated Python 3.12 environment.
- The same complete gate passed from an external working directory.
- Three hostile mutations were rejected: guard removal, early batch return,
  and arbitrary truthy echo handling.
- Python compilation and `git diff --check` passed.
