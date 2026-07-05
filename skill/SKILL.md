---
name: linear-issue-craft
description: Use when creating, drafting, or rewriting Linear issues (epics, stories, hardening tickets, refactor tasks) in any workspace. Trigger when the user says "draft an issue", "open an epic", "file a ticket", "write a Linear issue", or pastes a rough idea or bug report and asks for it to be filed.
---

# Linear Issue Craft

A portable issue-writing style. Every pattern in this skill is grounded in real shipped issues: see `references/06-canonical-examples.md` for verbatim source material.

**The issue is a compiler input, not an essay.** Downstream, an autonomous pipeline reads this text: a planner, a held-out probe that writes a frozen test from the title plus Requirements plus Evaluation alone (it never sees the repo), an implementer, a reviewer whose rubric is the Requirements section, and a merge gate. Concreteness is the product; prose is not. A named file, endpoint, or selector the probe can target is worth more than a paragraph of intent. When you are tempted to polish a sentence, name a thing instead.

## When this skill applies

Invoke when the user wants to create or polish a Linear issue and you have any signal that they want this style. Skip when the user explicitly asks for a different style or templates from another team.

## The issue archetypes

Every issue is one of these shapes. Identify the archetype first: it determines title pattern, body sections, and labels.

| Archetype | When to use | Title shape | Body sections |
|---|---|---|---|
| **Epic** | Strategic surface, 2–8 child stories, shared infra/domain | `Epic: <Domain>` | Goal · Outcomes · Out of scope · Stories under this epic |
| **Story** | One PR, one acceptance test, one service/surface | imperative verb + concrete deliverable, or `<Role> — <Capability>` | (epic backlink) · Anchor · User Story · Problem · Solution · Out of scope · Requirements · Evaluation |
| **Hardening** | Multiple vulnerabilities/bugs in one file/service | `Harden <file.ts>: <symptom1>, <symptom2>, <symptom3>` | Summary · Issues (numbered, each with **Fix:**) |
| **Task** | One bug, chore, spike, or ops change too small for the full story ceremony | `Bug: …` / `Chore: …` / `Spike: …`, or set `**Type:**` | Anchor · Problem · Verification |

The **Story** and **Task** carry an **Anchor**: one machine-resolvable target (`file.ext:line`, `file.ext:symbol`, `module.function`, `METHOD /path -> status`, or `playwright:selector`). The held-out probe cannot test a thing you never named, so this is the single highest-leverage line in the issue. Epics and hardening tickets are inherently anchored (a domain, a file path in the title) and do not carry a separate Anchor.

If a request doesn't fit one of these shapes, **stop and decompose** before writing. A "let's also rework X while we're at it" is a sibling story, not a bolted-on requirement.

## Decision flow

```
            ┌──────────────────────────────┐
            │  Is the request scoped to one│
            │  PR + one acceptance test?   │
            └──────────────────────────────┘
                  │                  │
                  │ yes              │ no
                  ▼                  ▼
         Is it ONE file w/   Does it cover 2–8 sub-pieces
         a list of bugs?     sharing infra or a domain?
              │  │                │
        yes ──┘  └── no  ──┐    yes        no
              │            │     │          │
              ▼            ▼     ▼          ▼
        Hardening      Story    Epic     Decompose first;
                                          do NOT proceed.
```

A single bug, chore, spike, or ops change that is too small for the full Story ceremony (no persona, no requirement-to-evaluation mapping) is a **Task**: `**Type:** Bug` (or `Chore`/`Spike`/`Ops`), an Anchor, a Problem, and a runnable Verification. Do not inflate a one-line bug into a Story, and do not file it as a one-issue Hardening ticket.

## Golden rules (apply to every issue, every archetype)

1. **Concrete over abstract.** Name the file path, function, endpoint, table, env var. "Improve API performance" is rejected; "Add caching to `/search` endpoint (target p95 < 200ms on 10k events)" is accepted.
2. **Anchor every story and task.** State one machine-resolvable target as `**Anchor:**` (`file.ext:line`, `file.ext:symbol`, `module.function`, `METHOD /path -> status`, or `playwright:selector`). This is the interface the held-out probe binds to; a prose anchor ("the auth flow") is not addressable and gets flagged. Name the seam the change actually lands on.
3. **Imperative verb first** on stories: Stand up · Wire · Harden · Build · Add · Generate · Refactor · Replace. Never passive ("Performance should be improved").
4. **Diagnose current state before proposing the fix.** Every epic opens with "Today …" or "Currently …" naming the deficiency in concrete terms (missing files, missing headers, missing endpoints). Skip the diagnosis and the issue reads like a press release.
5. **Acceptance must be runnable headless.** Every Evaluation item is a command or observation a headless stage can run against the repo checkout, with its expected output. No item may assert on a stubbed version of the thing under test. A soak, a dashboard read, or a staging check that needs prod credentials is a **Post-ship follow-up** line, never the acceptance.
6. **Reference past work explicitly.** Link related tickets by identifier, prior PRs, prior incidents. Use Linear's `<issue id="…">PROJ-XX</issue>` embed in Linear; plain `PROJ-XX` in plaintext. Encode a hard ordering as a real Linear blocked-by relation, not only prose, so the planner's wave DAG is correct.
7. **No em-dashes in prose.** The em-dash (`—`) is allowed in exactly one place: the separator in a role-prefixed story *title* (e.g., `Venue — Demand forecasting`), including where that title is listed verbatim under "Stories under this epic". Everywhere else in prose, use a colon, a comma, or rewrite. `scripts/validate_issue.py` enforces this.
8. **Labels are layered, not flat.** Always pick one domain **plus** one or more capabilities (e.g., `ai`, `seo`, `compliance`, `tech-debt`, `ui-ux`). The domain set is whatever the target workspace already uses (`api`/`web`/`mobile`, or `api`/`frontend`, or per-service): run `list_issue_labels` and pick from the real list, never invent one. Don't use sprint labels.
9. **Priority maps to category, not urgency:** High = security / infra / epics. Medium = features. Low = exploratory / decision-support. No priority = scoped-out or already done. Urgent is reserved for an active incident (prod down, live regression), not for a feature the requester feels strongly about.

## How to use this skill

1. Identify the archetype (epic / story / hardening / task). When in doubt, ask the user.
2. Open the matching workflow prompt in `prompts/`:
   - `prompts/brief-to-epic.md`: converts a one-paragraph brief into an epic + its child stories.
   - `prompts/hardening-issue.md`: converts a list of code issues in one file into a hardening ticket.
   - `prompts/refactor-story.md`: converts a code smell or tech-debt note into a single refactor story.
3. Pull patterns from `references/`:
   - `01-title-patterns.md`: every title shape with real examples.
   - `02-description-templates.md`: section-by-section body skeletons.
   - `03-tone-guide.md`: voice characteristics, what to avoid.
   - `04-labels-and-priority.md`: the layering rule and the priority-by-category mapping.
   - `05-anti-patterns.md`: common AI-style mistakes this skill rejects.
   - `06-canonical-examples.md`: three verbatim exemplars to imitate.
4. Draft the issue, then clear all three gates in "Validate before showing the draft": the mechanical validator (Gate 1), your own judgment checks (Gate 2), and an independent issue-reviewer subagent (Gate 3). Only show the user a draft that has cleared all three, and never file without explicit approval of the final text.
5. If the user approves, file it with your Linear MCP server's `save_issue` tool (e.g. `mcp__linear__save_issue`; the exact prefix depends on how the server is registered in your client).

## Output contract

When this skill is active, every draft you produce must include:

- A **title** that follows one of the patterns in `references/01-title-patterns.md` verbatim.
- A **body** that uses the section headings in `references/02-description-templates.md` for its archetype, in order. A story may add an `## Out of scope` non-goals section; do not invent other sections.
- An **Anchor** on every story and task: one machine-resolvable target (see golden rule 2).
- A **labels** array (1 domain + ≥1 capability) following `references/04-labels-and-priority.md`.
- A **priority** name (`Urgent` / `High` / `Medium` / `Low` / `No priority`) chosen by the category rule. Priority is category, not status: never use `No priority` to mean "deferred" or "verify-only", and reserve `Urgent` for an active incident.
- An **estimate**, set as the Linear estimate field at `save_issue` time (not a body line). No execution stage reads it; it is planner-facing, so set it when the workspace uses estimates and omit it silently when it does not.
- A short, conversational note to the user above the draft, summarizing why you chose this archetype, what alternative you considered, and any Critical or Important findings review raised and how you resolved them. Keep it to 3 sentences max.

## Two modes: interactive and headless

How this skill runs depends on who is downstream. Detect the mode from the invocation, not the mood of the request.

- **Interactive mode** (a human is reading each draft): you draft one or a few issues, run the gates, and show the human a note plus the draft for approval before filing. All three gates apply, including the independent Gate 3 reviewer per issue. This is the writing-aid path.
- **Headless / pipeline mode** (default when this skill is invoked from inside a subagent, or when filing more than one issue in a batch to hand straight to the execution pipeline): there is no human reading each draft, so the per-issue draft-approval ceremony and the per-issue Gate 3 reviewer are **dropped**. What replaces them is enforcement that cannot be skipped under load: **Gate 1 must pass on every block before every `save_issue` call** (a PreToolUse save-hook enforces this at the tool boundary, and it fires for subagent tool calls too; see `hooks/validate-issue-on-save.sh` and `hooks/README.md`), and the batch as a whole may get one review pass, not one reviewer per issue. The failure this fixes is real: the headless path is where per-issue ceremony silently evaporated (one run filed 80 issues with the validator never executed).

The rule that never relaxes in either mode: no `save_issue` without a clean Gate 1 on that issue's body. Everything else (the human note, the per-issue independent review) is interactive-mode ceremony that a batch handoff replaces with a boundary gate, not with trust.

## Validate before showing the draft

The gates below are the **interactive-mode** flow. Gate 1 is mechanical and non-negotiable in both modes. Gate 2 is judgment the script cannot make for you. Gate 3 is an independent reviewer that re-verifies your claims against the real code, because Gate 2 is you checking work you are biased to believe; in headless mode it is replaced by the save-hook plus an optional single batch review.

### Gate 1: run the validator (hard gate)

Run the validator on the draft. Resolve the path from this skill's own directory so it works from any working directory (the skill lives in a hashed plugin-cache dir, so a bare relative path can miss):

```bash
python3 "$(dirname "$0")/scripts/validate_issue.py" <draft-file>   # or pipe the draft on stdin
# from the skill root: python3 scripts/validate_issue.py <draft-file>
```

It must exit 0. It enforces (ERROR): em-dash in prose (fenced code and role-titled child bullets exempt), vague verbs ("improve"/"enhance"/"optimize") with no adjacent target metric, AI tells and `Co-Authored-By`, section names and order per archetype (catches `Description`/`Acceptance Criteria` drift), hardening `**Fix:**` lines, epic story count (2 to 8), and label shape. It WARNs (does not block) on a missing or prose-shaped Anchor, a missing story non-goal, an unobservable acceptance closer, and an off-enum priority; read every WARN. Fix every ERROR before showing the draft.

This is a gate, not a mental note. Do not show the user a draft you have not run through the validator. Time pressure and "this draft is too trivial to check" are not exemptions: the run is sub-second and the bulk/headless path is exactly where skipped validation shipped 80 unchecked issues. If `python3` is unavailable, that is a blocker to resolve (the script is stdlib-only, no install needed), not a reason to skip the gate.

### Gate 2: judgment checks (you, not the script)

- [ ] Title contains a concrete noun (file path, endpoint, component) or a Role-prefix.
- [ ] The diagnosis is accurate: the "Today …" sentence names real, current deficiencies you verified (grep the repo), not assumed ones.
- [ ] The User Story persona is a role the project actually uses, verified against the repo, its docs, or existing issues. Never an invented "operator" or "admin" when the project calls them "users".
- [ ] Labels match the target workspace's real taxonomy (you ran `list_issue_labels`), not a guessed set.
- [ ] If story: exactly one PR's worth of scope. A "while we're at it" is a sibling story, not a bolted-on requirement.
- [ ] The archetype is right: if the request did not fit epic/story/hardening, you decomposed instead of forcing it.

If Gate 1 reports any ERROR or any Gate 2 box is unchecked, fix it before moving on.

### Gate 3: independent review (issue-reviewer subagent)

Gate 2 is you checking your own work, and the context that wrote the issue is biased toward believing its own diagnosis. Gate 3 hands the draft to a fresh agent that re-verifies every claim against the actual code and workspace. This is the gate that catches the false "already done", the wrong `file:line`, and the half-done "change everywhere" sweep.

Dispatch an issue-reviewer subagent (Task tool, `general-purpose`) filling the template at `review/issue-reviewer.md`:

- `{ORIGINAL_REQUEST}`: what the user asked for, including whether they asked to file or only to investigate
- `{ISSUE_DRAFTS}`: the full draft(s)
- `{REPO_PATH}`: the repo the issues reference (or `none`)
- `{WORKSPACE_CONTEXT}`: target team/project plus your Linear MCP prefix
- `{FILED_IDS}`: `not yet filed (draft)` in the normal flow

Act on the verdict:

- **Fix before filing** or **Decompose first**: fix every Critical and Important finding, then re-run Gate 1 and put the revised draft back through Gate 3 before showing the user.
- **File as-is**: proceed to show the user, noting in your draft note what the review checked.
- Push back if the reviewer is wrong, with the evidence (the `file:line` that proves the claim), the same way you would with a code reviewer.

This is an interactive-mode gate. In interactive mode, do not show the user a draft you have not had independently reviewed: the defects Gate 3 catches are exactly the ones that look correct to the author, so "I am confident" is not a reason to skip it. In headless / pipeline mode there is no per-issue reviewer; the save-hook (Gate 1 at the tool boundary) plus at most one batch review over the whole set stands in for it. The cases that never need Gate 3: a pure title or label tweak on an already-filed issue, and any issue filed in headless mode.
