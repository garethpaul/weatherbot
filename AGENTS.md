# AGENTS.md

## Repository purpose

`garethpaul/weatherbot` is a Python web API or service project. A chat bot for the weather

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `requirements.txt` - Python runtime dependencies
- `screenshots` - repository source or sample assets

## Development commands

- Install dependencies: `python3 -m pip install -r requirements.txt`
- Full baseline: `make check`
- Combined verification: `make verify`
- Lint/static checks: `make lint`
- Tests: `make test`
- Build: `make build`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: Python (3).
- Prefer dependency-free tests or stdlib checks when legacy packages are unavailable.

## Testing guidance

- Test-related files detected: `test_messenger.py`
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- `WIT_TOKEN` configures Wit.ai access.
- `FB_PAGE_TOKEN` configures Facebook Messenger replies.
- `FB_VERIFY_TOKEN` configures Messenger webhook verification.
- `OPEN_WEATHER_TOKEN` configures OpenWeather lookup.
- `REQUEST_TIMEOUT` optionally overrides outbound request timeout seconds; invalid, non-finite, or non-positive values fall back to `5.0`.
- `WEATHERBOT_DEBUG=1` enables Bottle debug mode for local development; it is disabled by default.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
