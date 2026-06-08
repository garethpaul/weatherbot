# [P2] Send API access tokens outside URL query strings

## Severity

P2 - security/credential-exposure

## Evidence

- `messenger.py:94`: `qs = 'access_token=' + FB_PAGE_TOKEN`
- `messenger.py:96`: `resp = requests.post('https://graph.facebook.com/me/messages?' + qs,`

## Problem

The code builds API request URLs with `access_token` in the query string. Query strings are commonly captured by server logs, proxy logs, analytics, crash reports, and referrer headers, so bearer-style tokens can leak outside the process that needs them.

## Suggested fix

Pass tokens in an `Authorization` header or the provider SDK's credential field when supported. If the provider requires query parameters, keep the token scoped and short-lived, redact URLs before logging, and avoid storing the full tokenized URL in module-level constants.

## Review metadata

- Repository: `garethpaul/weatherbot`
- Reviewed commit: `cf76ed811f03b3604ed2fdef88b2f4d12f868e92`
- Labels: `bug`, `codex-review`, `severity:P2`
- Codex review fingerprint: `0053925837fe2bc8`
