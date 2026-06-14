# Weatherbot Provider Setup Guide

## Status: Completed

## Context

The README lists Weatherbot environment variables but does not connect each
secret to its provider, explain the shared Messenger webhook endpoint, or
define a safe setup and verification sequence.

## Requirements

- Document ownership and purpose for Wit.ai, Messenger page, Messenger verify,
  Messenger app-secret, and OpenWeather credentials.
- Document `GET /webhook` verification and signed JSON `POST /webhook` delivery
  on the same public HTTPS callback URL.
- Explain optional timeout, debug, Wit host/version, and port settings.
- Require secret-safe handling without checked-in values, inline examples,
  private payloads, page IDs, or conversation logs.
- Provide an ordered setup and redacted verification checklist that separates
  local offline tests from optional live provider checks.
- Link the guide from the README and roadmap and protect it with static
  contracts and hostile mutations.

## Verification Plan

- focused provider-guide and completed-plan contracts
- repository and external-directory `make check`
- hostile token-purpose, endpoint, HTTPS, GET verification, POST signature,
  media-type, privacy, optional-setting, verification, roadmap, suite, and
  plan-status mutations
- final artifact, credential, exact-diff, and hosted verification audits

## Scope Boundary

- Do not change runtime behavior, routes, tokens, provider origins,
  dependencies, workflows, or deployment configuration.
- Do not make live Wit.ai, Messenger, or OpenWeather calls.
- Do not merge or close stacked pull requests without owner authorization.

## Work Completed

- Added provider ownership, credential-purpose, HTTPS callback, GET verification,
  signed JSON POST, optional-setting, setup-order, and evidence guidance.
- Linked the guide from repository documentation and made its requirements,
  roadmap priority, suite registration, and completed plan mutation-sensitive.

## Verification

- Focused provider-guide and completed-plan contracts passed.
- Repository and external-directory `make check` passed.
- Thirteen hostile provider-guide mutations were rejected across credential
  purposes, endpoints, HTTPS, GET verification, POST signatures, media types,
  privacy, optional settings, evidence, roadmap, suite registration, and plan
  status.
- Dependency integrity, artifact, credential, and exact-diff audits passed.
  Hosted verification is recorded against the exact pull-request head after
  push.
