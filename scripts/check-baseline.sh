#!/usr/bin/env bash
set -euo pipefail

if grep -R "access_token=.*+" -n messenger.py wit.py; then
  echo "access tokens must not be embedded in URL strings" >&2
  exit 1
fi

if grep -R "me/messages?.*access_token" -n messenger.py wit.py; then
  echo "Messenger calls must not place access tokens in the URL" >&2
  exit 1
fi

if grep -R "http://api.openweathermap.org" -n messenger.py wit.py; then
  echo "OpenWeather calls must use HTTPS" >&2
  exit 1
fi

grep -q "debug(env_flag('BOTTLE_DEBUG'))" messenger.py
grep -q "timeout=REQUEST_TIMEOUT" messenger.py
grep -q "timeout=timeout" wit.py
grep -q "resp.raise_for_status()" messenger.py
grep -q "params={'access_token': FB_PAGE_TOKEN}" messenger.py
grep -q "def messenger_messages" messenger.py
grep -q "data.get('entry')" messenger.py
grep -q "message.get('message')" messenger.py

for file in \
  docs/bugs/p2-python-access-token-in-url-query-0053925837fe2bc8.md \
  docs/bugs/p2-python-unvalidated-webhook-json-indexing-5a755ba77f05a8ee.md; do
  if [ -f "$file" ]; then
    echo "resolved bug file remains: $file" >&2
    exit 1
  fi
done

python2 -m py_compile messenger.py wit.py 2>/dev/null || python3 - <<'PY'
from pathlib import Path

for path in ("messenger.py", "wit.py"):
    compile(Path(path).read_text(), path, "exec")
PY
