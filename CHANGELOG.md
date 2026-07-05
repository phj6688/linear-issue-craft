# Changelog

## Unreleased

### Added (save-hook: weld the boundary)
- `hooks/validate-issue-on-save.sh`: a Claude Code PreToolUse hook for `mcp__linear__save_issue` that runs the Gate-1 validator at the tool boundary, so the check cannot be skipped on the headless batch-filing path (a PreToolUse hook fires for subagent tool calls too). Create-only (an update with an `id` is left alone, so the pre-Anchor corpus is never orphaned); build-lane scoped (governance labels `human`/`eval` exempt); `observe` by default (logs would-blocks, allows) and `enforce` on an operator flip (denies with the validator's re-fileable output via `permissionDecision: deny`). Fails open on any unexpected input. On a create, a missing or prose-shaped Anchor is promoted from WARN to a block. `hooks/README.md` documents install + the operator-owned enforce flip (gated on a clean corpus replay); `hooks/test_hook.sh` covers the decision matrix (7 cases).

### Added (Anchor + validator hygiene)
- **Anchor field.** Every story and task now carries a `**Anchor:**` line: one machine-resolvable target (`file.ext:line`, `file.ext:symbol`, `module.function`, `METHOD /path -> status`, or `playwright:selector`). It is the interface the downstream held-out probe binds to; a probe cannot test a thing the issue never named. The validator WARNs on a missing or prose-shaped anchor; a save-hook (separate increment) promotes it to a create-only ERROR.
- **Task archetype** for a single bug, chore, spike, or ops change too small for the full story ceremony. Selected with `**Type:** Bug|Chore|Spike|Ops` (or a title prefix); shape is Anchor / Problem / Verification. Fixes the coverage gap where a one-line bug had to be inflated into a Story or mis-filed as a one-issue Hardening ticket. New title pattern (6) and canonical Example 5.
- **Compiler-input framing** in `SKILL.md` and README: the issue is read by an autonomous pipeline (planner, held-out probe, implementer, reviewer, merge gate), so concreteness is the product and prose is not.
- **Two-mode operation.** Interactive mode keeps the three gates and human approval. Headless / pipeline mode (a subagent filing a batch to the execution pipeline) drops the per-issue Gate 3 reviewer and the draft-approval ceremony, and relies on Gate 1 passing before every `save_issue` (enforced at the tool boundary by a save-hook). This is the path where 80 issues once shipped with the validator never run.
- Story template gains an `## Out of scope` non-goals section (the implementer agent gold-plates without a boundary) and a `## Post-ship follow-up` line for soak/dashboard checks that cannot run headless. Hardening issues gain a per-issue `**Verify:**` line (their only testable contract, since they have no Requirements section).
- New validator tests: fenced-code blindness, the `---` tail-drop split, a standalone story, an adjacent-metric false-negative, and the Anchor shape check.

### Changed (validator correctness)
- **`epic-backlink` demoted to WARN.** A standalone or refactor story with no parent no longer hard-fails; write `**Epic:** none` to mark the omission deliberate. This was the single most common self-inflicted validator failure.
- **`labels-verify` WARN deleted.** It fired on every block every run and could never be discharged by the script, pure noise.
- **Vague-verb check now requires an adjacent metric.** The metric must sit within a few words of `improve`/`enhance`/`optimize`; a bare integer elsewhere on the line (a version, issue id, or port) no longer launders the verb.
- **Code-fence and inline-code awareness.** The em-dash, AI-tell, vague-verb, and section scans skip fenced code and inline-code spans, so a quoted `## Description`, `robust-parser.ts`, or a code sample no longer false-trips.
- **`---` splitting is fence-aware and merges title-less tails.** A `---` inside a code block, or one that only splits body prose, is content; it can no longer silently drop the tail of an issue (and everything after it) from validation.
- **`epic-story-count` counts any bullet** under "Stories under this epic" (verbatim child titles and ordered lists included), and role-prefixed child titles are exempt from the em-dash check, resolving the contradiction with "list child titles verbatim".
- **Estimate** is set as the Linear field at `save_issue` time, not mandated as a body line (no execution stage reads it); the reviewer treats a missing estimate as at most Minor. Priority enum reconciled to `Urgent / High / Medium / Low / No priority` with a validator WARN on off-enum values; `Urgent` is reserved for an active incident.
- The canonical examples carry Anchor lines and runnable acceptance closers; the 24h-soak closers moved to Post-ship follow-up, and Example 2's "operator" persona is annotated as a real workspace role (not the invented-persona anti-pattern).
- Portable validator invocation in `SKILL.md` (resolve from the skill dir), and the Gate-1 loophole is closed: time pressure and "too trivial to check" are not exemptions.

### Added (original three-gate work)
- `skill/review/issue-reviewer.md`: Gate 3, an independent issue-reviewer subagent template adapted from the code-review pattern. A fresh-context agent re-verifies every claim in a draft against the real repo and Linear workspace (file:line references, "already done" diagnoses, "change everywhere" sweeps, scope bundling, missing estimates, data-vs-code gaps, dedup and epic/child linkage) and returns graded findings with a File-as-is / Fix-before-filing / Decompose-first verdict. Grounded in real issue-creation failures (a false "there is no middleware.ts" diagnosis that would have shipped the wrong locale; a partial copy sweep that left the storefront and checkout disagreeing).
- `skill/scripts/validate_issue.py`: a stdlib-only validator that mechanically enforces the house-style rules (em-dash in prose, vague verbs without a metric, AI tells, section names and order per archetype, hardening `Fix:` lines, epic story count, label shape, title rules). The skill runs it as a hard gate before any draft is shown. Tests in `skill/scripts/tests/`.
- Validator support for the bundled-concept story variant (`### Concept` blocks replace the `## Solution` H2), so those drafts pass the gate; added a fixture.

### Changed
- `SKILL.md`: the validate-before-showing flow is now three gates. Gate 3 dispatches the issue-reviewer subagent before any draft is shown, because the context that wrote an issue is biased toward believing its own diagnosis: a self-checklist passes while the claim stays false, but a separate agent re-runs the grep and finds the truth. Added an `Estimate` field to the output contract (stories were shipping with none) and a rule that priority is category, not a status or "deferred" marker.
- `SKILL.md`: replaced the "run these mentally" checklist with a three-gate flow (the validator script for mechanical rules, judgment-only checks the script cannot make, and Gate 3 independent review). Trimmed the `description` to triggering conditions only, so the agent reads the body instead of acting on a workflow summary.
- Stories-under-epic lists now use `Story N:` (colon) instead of an em-dash, removing the contradiction with golden rule 5 (the rule banned em-dashes in prose while the examples used them).
- The label rule defers to the target workspace's own domain taxonomy; the agent verifies names via `list_issue_labels` rather than a hardcoded `api`/`web`/`mobile` set.
- The brief-to-epic workflow asks a clarifying question when the scope (platform, v1 feature set, target surface) is unknown, not only when the deficiency sentence cannot be written.
- Hardening issue headers include line numbers only when the source provides them, rather than always.
- Doc typography: converted author-prose em-dashes across the skill docs to ASCII punctuation. Em-dash is kept only in role-prefixed title examples, the deliberate em-dash anti-pattern example, and the lines that define the character. Bundled-concept `### Concept N:` headers use a colon.

### Fixed
- Corrected the Linear MCP tool name to `mcp__linear__save_issue` (was `mcp__linear-server__save_issue`) across `SKILL.md` and the workflow prompts.
- Removed a literal en-dash from the `EM_DASH` code comment (lint / CodeRabbit nitpick).
- Canonical Example 4: "leverages" became "reuses" so the example passes the validator's AI-tell check.
