#!/usr/bin/env sh
set -eu
URL="${1:-http://localhost:8000/health}"
COUNT="${2:-100}"
if ! command -v curl >/dev/null 2>&1; then echo "curl is required" >&2; exit 1; fi
i=1
while [ "$i" -le "$COUNT" ]; do
  curl -sS -o /dev/null -w "request $i: %{http_code} %{time_total}s\n" "$URL"
  i=$((i + 1))
done
