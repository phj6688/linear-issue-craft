# Save-hook: validate a Linear issue at the tool boundary

`validate-issue-on-save.sh` is a Claude Code **PreToolUse** hook for `mcp__linear__save_issue`. It runs the same validator as the skill's Gate 1, but at the point of creation, so the check cannot be skipped: a PreToolUse hook fires for tool calls made inside subagents too, which is exactly the headless batch-filing path where the interactive gates get bypassed.

## What it does

- Fires only on **create** calls (`save_issue` with no `id`). An update is left alone, so the existing corpus of pre-Anchor issues is never re-validated or orphaned. The Anchor requirement is therefore create-only.
- Reconstructs a validator-shaped document from the create payload (synthesizes the `**Title:**` / `**Labels:**` / `**Priority:**` header lines from the Linear fields when the description does not already carry them), then runs `skill/scripts/validate_issue.py`.
- Scopes to the **build lane**: an issue whose only labels are governance labels (default `human`, `eval`) is exempt. Decision and adjudication issues are not code and do not go through the build pipeline.
- Two modes:
  - `observe` (default): logs a would-block on any validator ERROR (or, on a create, a missing/prose Anchor) and **allows**. This measures the gap without blocking filing.
  - `enforce`: **denies** the create with the validator's re-fileable output as the reason (`permissionDecision: deny`).
- Fails **open** on anything unexpected (no `jq`/`python3`, unparseable payload, unreadable validator). A validation gate must never brick a session on its own bug.

## Install (observe mode)

Wire it into `~/.claude/settings.json` under `hooks.PreToolUse`, matched to the save tool by name:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__linear__save_issue",
        "hooks": [
          { "type": "command",
            "command": "/ABSOLUTE/PATH/TO/linear-issue-craft/hooks/validate-issue-on-save.sh",
            "timeout": 20 }
        ]
      }
    ]
  }
}
```

Config is env-only, so the script stays portable:

| Env var | Default | Meaning |
|---|---|---|
| `LINEAR_ISSUE_GATE_MODE` | `observe` | `observe` or `enforce` |
| `LINEAR_ISSUE_GATE_VALIDATOR` | sibling `../skill/scripts/validate_issue.py` | validator path |
| `LINEAR_ISSUE_GATE_EXEMPT` | `human,eval` | governance labels that are never gated |
| `LINEAR_ISSUE_GATE_LOG` | `$TMPDIR/linear-issue-gate.log` | would-block / decision log |

## Flipping to enforce (operator-owned)

Do **not** flip to enforce on faith. The gate blocks real creates, so first prove the validator does not false-fail the workspace's existing issues:

1. **Replay precondition.** Run the current validator over a representative sample of the workspace's existing issues, rendered in create-payload shape, and confirm **zero** create-blocking false-fails (a false-fail = a validator bug, not a genuine style violation). Only then is blocking safe.
2. Run `bash hooks/test_hook.sh` and confirm it passes.
3. Set `LINEAR_ISSUE_GATE_MODE=enforce` (e.g. in the hook's environment, or a wrapper) for **one** workspace first, watch the log for a week, and confirm `filed-count == intended-count` on a bulk run (a gap means a subagent got a `deny` and did not re-draft, the one blind spot this gate has).
4. Fan out only after the single-workspace bake is clean.

The agent that authors issues does not flip this itself; the flip is a human step, the same stance as the held-out merge gate.

## Test

```bash
bash hooks/test_hook.sh
```

Covers: observe never denies, enforce denies a bad create, enforce allows a good create, updates are ignored, a create with no Anchor is blocked in enforce, governance-only labels are exempt, and observe logs the would-block.
