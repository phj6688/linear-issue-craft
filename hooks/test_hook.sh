#!/usr/bin/env bash
# Tests for validate-issue-on-save.sh. Feeds PreToolUse stdin payloads and asserts
# the allow/deny decision. Run: bash hooks/test_hook.sh
set -uo pipefail
HOOK="$(cd "$(dirname "$0")" && pwd)/validate-issue-on-save.sh"
LOG="$(mktemp)"
export LINEAR_ISSUE_GATE_LOG="$LOG"
pass=0; fail=0
ok()   { pass=$((pass+1)); }
bad()  { fail=$((fail+1)); printf '  FAIL: %s\n' "$1"; }

# Returns "deny" if the hook emitted a deny decision, else "allow".
decide() { # $1 = mode, stdin = payload
  local mode="$1" out
  out=$(LINEAR_ISSUE_GATE_MODE="$mode" bash "$HOOK")
  if printf '%s' "$out" | grep -q '"permissionDecision": *"deny"'; then
    echo deny
  else
    echo allow
  fi
}

# Bodies with REAL newlines; jq --arg escapes them into valid JSON.
GOOD_BODY=$'**Epic:** none\n**Title:** Add an LRU cache to the search endpoint\n**Anchor:** api/src/search.ts:handleSearch\n\n## User Story\n\nAs a user, I want fast search, so results feel instant.\n\n## Problem\n\nToday /search recomputes each call.\n\n## Solution\n\nAdd an LRU cache. One module.\n\n## Out of scope\n\n* Query syntax.\n\n## Requirements\n\n1. Add cache to handleSearch.\n\n## Evaluation\n\n1. **Validates R1**: pytest -k search asserts p95 < 200ms.'
BAD_BODY=$'**Title:** Improve search performance\n\n## User Story\n\nbad'
NOANCHOR_BODY=$'## User Story\n\nAs an op, I want logs, so I can query.\n\n## Problem\n\nToday text logs.\n\n## Solution\n\nAdd pino. One module.\n\n## Out of scope\n\n* rotation\n\n## Requirements\n\n1. Add api/src/log.ts.\n\n## Evaluation\n\n1. **Validates R1**: pytest -k log passes.'

good_create()    { jq -nc --arg d "$GOOD_BODY"     '{tool_name:"mcp__linear__save_issue",tool_input:{title:"Add an LRU cache to the search endpoint",description:$d,labels:["api","tech-debt"],priority:3}}'; }
bad_create()     { jq -nc --arg d "$BAD_BODY"      '{tool_name:"mcp__linear__save_issue",tool_input:{title:"Improve search performance",description:$d,labels:["api","tech-debt"],priority:3}}'; }
bad_update()     { jq -nc --arg d "$BAD_BODY"      '{tool_name:"mcp__linear__save_issue",tool_input:{id:"ISS-1",title:"Improve search performance",description:$d,labels:["api","tech-debt"]}}'; }
missing_anchor() { jq -nc --arg d "$NOANCHOR_BODY" '{tool_name:"mcp__linear__save_issue",tool_input:{title:"Wire structured logging into the api",description:$d,labels:["api","tech-debt"],priority:3}}'; }
governance()     { jq -nc --arg d "$BAD_BODY"      '{tool_name:"mcp__linear__save_issue",tool_input:{title:"Decide bourse: wire or decommission",description:$d,labels:["human","eval"]}}'; }

[ "$(bad_create | decide observe)" = "allow" ]     && ok || bad "observe allows bad create"
[ "$(bad_create | decide enforce)" = "deny" ]      && ok || bad "enforce denies bad create"
[ "$(good_create | decide enforce)" = "allow" ]    && ok || bad "enforce allows good create"
[ "$(bad_update | decide enforce)" = "allow" ]     && ok || bad "enforce ignores updates"
[ "$(missing_anchor | decide enforce)" = "deny" ]  && ok || bad "enforce blocks missing anchor on create"
[ "$(governance | decide enforce)" = "allow" ]     && ok || bad "enforce exempts governance labels"

bad_create | LINEAR_ISSUE_GATE_MODE=observe bash "$HOOK" >/dev/null
grep -q 'would-block(observe)' "$LOG" && ok || bad "observe logs would-block"

printf '\n%d passed, %d failed\n' "$pass" "$fail"
rm -f "$LOG"
[ "$fail" -eq 0 ]
