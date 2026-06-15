# Changelog

## Unreleased

### Added
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
