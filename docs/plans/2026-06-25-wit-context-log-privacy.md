# Wit Action Context Log Privacy

Status: Completed

## Context

The existing Wit log-privacy hardening removed request parameters and response
JSON from debug output, but the action loop still logged the complete context
dictionary. That context can contain a Messenger user's normalized location,
weather conditions, and conversational state.

## Design

Remove the context payload log entirely. Preserve the response-type trace,
which is sufficient to follow the action state machine without serializing
user or provider data. Do not add recursive redaction or key-only logging;
both create unnecessary privacy and maintenance surface for this sample.

## Verification

- A behavioral regression runs the real Wit action loop with a private location
  in context and proves neither its value nor key appears in debug output.
- The existing response-type diagnostic remains visible.
- The dependency-free contract rejects restoration of the legacy context log
  and requires the behavioral regression to remain present.
- `make check` runs the complete static and runtime suite.
