# Weatherbot Wit Entity Normalization

Status: Completed

## Context

Wit location entities may expose a flat value or a nested value object. The
nested path used unchecked dictionary indexing, so malformed objects could
raise `KeyError`, while non-text values could reach the weather query.

## Changes

- Safely unwrap the supported nested entity shape.
- Route flat and nested values through the existing text normalizer.
- Reject blank, mapping, sequence, and numeric location values.
- Trim accepted location text before OpenWeather lookup.
- Add dependency-free and unittest coverage for malformed and valid shapes.

## Verification

- `make check`
- Replace normalized access with unchecked nested indexing and confirm the
  contract checker fails before restoring it.
