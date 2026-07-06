#!/usr/bin/env bash
# PreToolUse(mcp__linear__save_issue): validate a Linear issue at the tool
# boundary, before it is created. This is the "weld the boundary" gate: the skill
# runs the same validator as Gate 1, but a headless subagent filing a batch can
# skip Gate 1, so this hook makes the check unskippable by construction (a
# PreToolUse hook fires for tool calls made inside subagents too).
#
# Scope: CREATE calls only (save_issue with no `id`). An UPDATE (id present) is
# left alone, so the existing corpus of pre-Anchor issues is never orphaned and
# routine edits are never blocked. The Anchor requirement is therefore create-only.
#
# Modes (env LINEAR_ISSUE_GATE_MODE, default observe):
#   observe  : run the validator, LOG a would-block on ERRORs (or, on create, a
#              missing/prose Anchor), but ALLOW. Measures the gap without bricking
#              filing before the validator is proven clean on the workspace corpus.
#   enforce  : DENY the create (permissionDecision: deny) with the validator's
#              re-fileable output as the reason. Flip to this per workspace only
#              after replaying the validator over the existing corpus shows zero
#              false-fails. Operator-owned; the agent does not self-flip.
#
# Fail OPEN on anything unexpected (no jq, no python, unparseable payload, missing
# validator): allow. A validation gate must not brick a session on its own bug.
#
# Config (all optional, env-overridable so the script stays portable):
#   LINEAR_ISSUE_GATE_MODE       observe | enforce            (default observe)
#   LINEAR_ISSUE_GATE_VALIDATOR  path to validate_issue.py    (default: sibling skill copy)
#   LINEAR_ISSUE_GATE_EXEMPT     comma list of governance labels that are NOT
#                                build-lane and are never gated (default: human,eval)
#   LINEAR_ISSUE_GATE_LOG        would-block log file         (default: $TMPDIR/linear-issue-gate.log)
set -uo pipefail

allow() { exit 0; }
deny() {
  # permissionDecision JSON on stdout, exit 0 (the documented deny path for a
  # PreToolUse hook on an MCP tool; exit-2 is unreliable for non-Bash tools).
  python3 - "$1" <<'PY' 2>/dev/null || { printf '%s\n' "$1" >&2; exit 2; }
import json, sys
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": sys.argv[1],
}}))
PY
  exit 0
}

command -v jq >/dev/null 2>&1 || allow
command -v python3 >/dev/null 2>&1 || allow

input=$(cat 2>/dev/null) || allow
[ -n "$input" ] || allow

tool=$(printf '%s' "$input" | jq -r '.tool_name // ""' 2>/dev/null)
case "$tool" in
  *save_issue) : ;;                 # matcher should already scope this; double-check
  *) allow ;;
esac

# CREATE vs UPDATE: an update carries an id/issueId. Only gate creates.
iid=$(printf '%s' "$input" | jq -r '.tool_input.id // .tool_input.issueId // ""' 2>/dev/null)
[ -z "$iid" ] || allow

MODE="${LINEAR_ISSUE_GATE_MODE:-observe}"
HOOK_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-$0}")" && pwd)
VALIDATOR="${LINEAR_ISSUE_GATE_VALIDATOR:-$HOOK_DIR/../skill/scripts/validate_issue.py}"
[ -r "$VALIDATOR" ] || allow
# Lowercased so a mixed-case override (e.g. "Human,Eval") still matches the
# label names, which are compared in lowercase.
EXEMPT=$(printf '%s' "${LINEAR_ISSUE_GATE_EXEMPT:-human,eval}" | tr '[:upper:]' '[:lower:]')
LOG="${LINEAR_ISSUE_GATE_LOG:-${TMPDIR:-/tmp}/linear-issue-gate.log}"

# Reconstruct a validator-shaped document from the create payload. Linear stores
# title/labels/priority as fields, not body lines, so synthesize the header lines
# the validator expects only when the description does not already carry them.
# The payload is passed as argv (a heredoc would capture python's stdin and shadow
# a piped payload).
doc=$(python3 - "$input" <<'PY' 2>/dev/null
import json, sys
try:
    d = json.loads(sys.argv[1])
except Exception:
    sys.exit(0)
ti = d.get("tool_input") or {}
desc = ti.get("description") or ti.get("body") or ""
title = (ti.get("title") or "").strip()

# Labels may arrive as names, as {name} objects, or as opaque ids. The validator
# only counts them (>=2), so any tokens preserve the shape.
labels = ti.get("labels") or ti.get("labelIds") or ti.get("labelNames") or []
names = []
for l in labels if isinstance(labels, list) else []:
    if isinstance(l, str):
        names.append(l)
    elif isinstance(l, dict):
        names.append(str(l.get("name") or l.get("id") or "label"))
    else:
        names.append("label")

PRI = {0: "No priority", 1: "Urgent", 2: "High", 3: "Medium", 4: "Low"}
pri = ti.get("priority")
pri_name = ti.get("priorityLabel") or (PRI.get(pri) if isinstance(pri, int) else (pri or ""))

head = []
if title and "**Title:**" not in desc:
    head.append(f"**Title:** {title}")
if names and "**Labels:**" not in desc:
    head.append("**Labels:** " + ", ".join(f"`{n}`" for n in names))
if pri_name and "**Priority:**" not in desc:
    head.append(f"**Priority:** {pri_name}")

# Emit the labels (comma-joined) on the first line for the shell's scope check.
low = ",".join(names).lower()
print("GATELABELS:" + low)
print("\n".join(head) + ("\n\n" if head else "") + desc)
PY
)
[ -n "$doc" ] || allow

# Peel the label signal line, then the reconstructed document.
labels_line=$(printf '%s' "$doc" | sed -n '1p')
labels_low=${labels_line#GATELABELS:}
body=$(printf '%s' "$doc" | sed '1d')

# Build-lane scoping: if the issue carries only governance labels (human/eval,
# decision/adjudication), it is out of scope for the build-lane gate. A build
# issue (api/web/build/infra/... or no governance label) is in scope.
in_scope=1
if [ -n "$labels_low" ]; then
  only_governance=1
  IFS=',' read -r -a _labels <<< "$labels_low"
  for l in "${_labels[@]}"; do
    l=$(printf '%s' "$l" | tr -d '[:space:]')
    [ -n "$l" ] || continue
    case ",$EXEMPT," in
      *",$l,"*) : ;;                 # a governance label
      *) only_governance=0 ;;        # a real build/domain label -> in scope
    esac
  done
  [ "$only_governance" = "1" ] && in_scope=0
fi

now=$(date -u +%FT%TZ 2>/dev/null || echo "?")
logline() { printf '%s\tmode=%s\t%s\n' "$now" "$MODE" "$1" >> "$LOG" 2>/dev/null || true; }

[ "$in_scope" = "1" ] || { logline "governance-exempt labels=[$labels_low] ALLOW"; allow; }

# Run the validator. Exit 1 means blocking ERRORs; capture the report for the reason.
report=$(printf '%s' "$body" | python3 "$VALIDATOR" - 2>/dev/null)
vstatus=$?

# On a create, a missing or prose-shaped Anchor is promoted from WARN to a block.
anchor_block=""
printf '%s' "$report" | grep -Eq '\[anchor-(missing|shape)\]' && anchor_block=1

if [ "$vstatus" = "0" ] && [ -z "$anchor_block" ]; then
  logline "clean title=$(printf '%s' "$body" | grep -m1 '\*\*Title:\*\*' | cut -c1-80) ALLOW"
  allow
fi

# Non-conforming create.
errs=$(printf '%s' "$report" | grep -E '^[[:space:]]+ERROR' | sed 's/^[[:space:]]*//' | head -12)
[ -n "$anchor_block" ] && errs=$(printf '%s\n%s' "$errs" "  ANCHOR required on create: name a file.ext:line / file.ext:symbol / module.function / METHOD /path -> status / playwright:selector")
reason="linear-issue-craft gate: this create does not pass the house-style validator. Fix these, then re-file:
$errs

(Run the validator locally: python3 $VALIDATOR <draft>. This gate is CREATE-only and build-lane scoped; governance issues (labels: $EXEMPT) are exempt.)"

if [ "$MODE" = "enforce" ]; then
  logline "BLOCK errs=$(printf '%s' "$errs" | tr '\n' ';' | cut -c1-160)"
  deny "$reason"
fi

logline "would-block(observe) errs=$(printf '%s' "$errs" | tr '\n' ';' | cut -c1-160)"
allow
