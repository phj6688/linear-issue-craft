# Changelog

## Unreleased

### Added
- `skill/scripts/validate_issue.py`: a stdlib-only validator that mechanically enforces the house-style rules (em-dash in prose, vague verbs without a metric, AI tells, section names and order per archetype, hardening `Fix:` lines, epic story count, label shape, title rules). The skill runs it as a hard gate before any draft is shown. Tests in `skill/scripts/tests/`.
- Validator support for the bundled-concept story variant (`### Concept` blocks replace the `## Solution` H2), so those drafts pass the gate; added a fixture.

### Changed
- `SKILL.md`: replaced the "run these mentally" checklist with a two-gate system (the validator script for mechanical rules, plus judgment-only checks the script cannot make). Trimmed the `description` to triggering conditions only, so the agent reads the body instead of acting on a workflow summary.
- Stories-under-epic lists now use `Story N:` (colon) instead of an em-dash, removing the contradiction with golden rule 5 (the rule banned em-dashes in prose while the examples used them).
- The label rule defers to the target workspace's own domain taxonomy; the agent verifies names via `list_issue_labels` rather than a hardcoded `api`/`web`/`mobile` set.
- The brief-to-epic workflow asks a clarifying question when the scope (platform, v1 feature set, target surface) is unknown, not only when the deficiency sentence cannot be written.
- Hardening issue headers include line numbers only when the source provides them, rather than always.
- Doc typography: converted author-prose em-dashes across the skill docs to ASCII punctuation. Em-dash is kept only in role-prefixed title examples, the deliberate em-dash anti-pattern example, and the lines that define the character. Bundled-concept `### Concept N:` headers use a colon.

### Fixed
- Corrected the Linear MCP tool name to `mcp__linear__save_issue` (was `mcp__linear-server__save_issue`) across `SKILL.md` and the workflow prompts.
- Removed a literal en-dash from the `EM_DASH` code comment (lint / CodeRabbit nitpick).
- Canonical Example 4: "leverages" became "reuses" so the example passes the validator's AI-tell check.
