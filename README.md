# linear-issue-craft

A portable Claude Code skill that captures a tight, repeatable Linear issue writing style, designed to be applied to any Linear workspace.

The issue is treated as a compiler input, not an essay: an autonomous execution pipeline reads it (a planner, a held-out probe that writes a frozen test from a Story's title plus Requirements and Evaluation, or a Task's Problem and Verification, an implementer, a reviewer, a merge gate), so concreteness is the product. Every pattern in this repo is grounded in real shipped issues, not invented. The canonical exemplars are quoted verbatim (with workspace identifiers anonymized) in `skill/references/06-canonical-examples.md`.

## What's in the box

```
skill/
├── SKILL.md                      Main skill entry: decision flow, golden rules, three-gate output contract
├── references/
│   ├── 01-title-patterns.md      6 title shapes with real examples
│   ├── 02-description-templates.md  Body skeletons per archetype
│   ├── 03-tone-guide.md          Voice characteristics, hard "no" list
│   ├── 04-labels-and-priority.md Layered labels + category-driven priority
│   ├── 05-anti-patterns.md       Common AI failures and their fixes
│   └── 06-canonical-examples.md  Five full verbatim exemplars (Epic, Story, Hardening, Bundled, Task)
├── prompts/
│   ├── brief-to-epic.md          Workflow: 1-paragraph brief → epic + N child stories
│   ├── hardening-issue.md        Workflow: list of defects in one file → Hardening ticket
│   └── refactor-story.md         Workflow: code smell → refactor story
├── scripts/
│   └── validate_issue.py         Gate 1: mechanical house-style validator (stdlib-only)
└── review/
    └── issue-reviewer.md         Gate 3: independent reviewer subagent template
```

## Flow diagram

`docs/linear-issue-craft-flow.drawio` is a draw.io flowchart of the skill's core path: classify the archetype (epic / story / hardening / task, or decompose), draft, clear the gates (Gate 1 validator, then Gate 2 and Gate 3 interactively, or the save-hook in headless mode), then file. Light theme, drawio-native palette, with a legend. Open it at [app.diagrams.net](https://app.diagrams.net) or with the draw.io VS Code extension.

## The archetypes

| Archetype | Title shape | Body sections |
|---|---|---|
| **Epic** | `Epic: <Domain>` | Goal · Outcomes · Out of scope · Stories under this epic |
| **Story** | imperative verb + concrete deliverable, or `<Role> — <Capability>` | (epic backlink) · Anchor · User Story · Problem · Solution · Out of scope · Requirements · Evaluation |
| **Hardening** | `Harden <file.ts>: <symptom1>, <symptom2>, <symptom3>` | Summary · Issues (numbered, each with **Fix:** + **Verify:**) |
| **Task** | `Bug:` / `Chore:` / `Spike:` / `Ops:` (or set `**Type:**`) | Anchor · Problem · Verification |

Every **Story** and **Task** carries an **Anchor**: one machine-resolvable target (`file.ext:line`, `file.ext:symbol`, `module.function`, `METHOD /path -> status`, or `playwright:selector`) that the held-out probe binds to.

## How to use it

### As a Claude Code skill (recommended)

Symlink (or copy) the `skill/` directory into `~/.claude/skills/linear-issue-craft/`:

```bash
ln -s "$(pwd)/skill" ~/.claude/skills/linear-issue-craft
```

Then in any Claude Code session, when you ask the assistant to "draft a Linear issue" / "open an epic" / "file a ticket", it will detect the skill, invoke it, and follow the conventions automatically.

### As a prompt-only reference

You can also paste the contents of `skill/SKILL.md` and any relevant `references/` file into a non-Claude-Code chat (web Claude, ChatGPT, etc.) as a system prompt before asking for issue drafts.

### Filing the drafts

Drafts produced under this skill are designed to be fed into the Linear MCP server's `save_issue` tool. In interactive mode, before a draft is shown it clears three gates: a mechanical validator (`scripts/validate_issue.py`), a judgment checklist, and an independent issue-reviewer subagent (`review/issue-reviewer.md`) that re-verifies every claim against the actual code and workspace (file:line references, Anchor existence, "already done" diagnoses, "change everywhere" sweeps, scope, dedup). The skill requires explicit user approval before any `save_issue` call. In headless / pipeline mode (a subagent filing a batch straight to the execution pipeline) the per-issue reviewer and approval step are replaced by a save-hook that runs the validator at the tool boundary, so validation cannot be skipped under load.

## Why this exists

Issue quality in Linear is a function of pattern adherence. A high-signal workspace will converge on a tight, repeatable style: every title diagnoses *where* and *what*; every body starts with a current-state deficiency; every story has grep-able requirements paired to acceptance criteria; every hardening ticket calibrates severity honestly. That style is portable — it works for any project whose stack is structured enough to name files and endpoints.

Without a captured template, an AI assistant defaults to generic SaaS-PM voice ("Improve the search experience", "comprehensive solution", "robust handling"), which makes the issues read like marketing copy and leaves reviewers unsure what to actually build.

This skill is the bridge.

## Source material

The patterns were distilled from real shipped issues across well-structured Linear workspaces. The canonical exemplars in `references/06-canonical-examples.md` are quoted verbatim with the workspace-specific identifiers anonymized to `PROJ-N` (Anchor lines and runnable acceptance closers reflect the current contract; the originals predate both).

## Extensions (not built yet)

The patterns here are intentionally narrow. If you want to extend:

- **Per-project taxonomy overrides** — different domain labels per workspace. Add a `taxonomy.json` next to `SKILL.md`.
- **Multi-agent ideation** — for complex epics, have multiple agents propose decompositions in parallel, then pick the best.
- **Auto-link to PRs** — extend the workflow prompts to also draft the PR title + body in matching style.

## License

MIT. See `LICENSE`.
