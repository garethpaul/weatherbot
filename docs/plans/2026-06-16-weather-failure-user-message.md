# Weather Failure User Message

## Status: Planned

## Context

`get_forecast` already distinguishes a missing location from a known location
whose OpenWeather lookup failed by setting `missingLocation` or
`missingForecast`. The `send` action ignores that state and forwards Wit.ai's
response text unchanged. A provider failure can therefore return stale or
misleading forecast copy instead of a stable repository-controlled fallback.

## Requirements

- Define a concise user-facing message for known-location weather lookup
  failures.
- Use that fallback only when the action request context explicitly carries
  `missingForecast` as the boolean `True`; malformed truthy values must not
  broaden the override.
- Preserve normal Wit response text for successful forecasts, missing-location
  prompts, and requests with absent or malformed context.
- Keep Messenger provider HTTP errors visible to the webhook retry path.
- Add executable and static mutation-sensitive coverage for the override and
  its non-overriding branches.
- Update the roadmap, maintenance documentation, changelog, and completed plan
  evidence without changing provider credentials or live API behavior.

## Key Decision

Apply the fallback in `send`, immediately before `fb_message`, because that is
the final repository-owned boundary between Wit action state and Messenger
reply text. Do not overload `forecast` with an error string or require external
Wit configuration changes; successful weather context remains structured and
the missing-location response remains owned by the existing Wit conversation.

## Verification Plan

- Run focused action tests for failed, successful, missing-location, absent,
  and malformed context.
- Run isolated hostile mutations that remove the override, broaden it to
  missing-location state, or allow Wit text to replace the fallback.
- Run bounded repository and external-directory `make check` gates.
- Audit the exact diff, generated artifacts, whitespace, file modes, and
  changed lines for credential material.

## Scope Boundaries

- Do not call live Messenger, Wit.ai, or OpenWeather services.
- Do not add retry, localization, or conversational-state infrastructure.
- Do not merge or close stacked pull requests without explicit authorization.
