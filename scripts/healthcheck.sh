#!/usr/bin/env bash
set -euo pipefail
BASE_URL="${1:-http://127.0.0.1:8000}"
TOKEN="${2:-change-me}"
curl -s "$BASE_URL/healthz"; echo
curl -s "$BASE_URL/readyz"; echo
curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/mcp/tools"; echo
