---
name: linear-issue-craft
description: Use when creating, drafting, or rewriting Linear issues (epics, stories, hardening tickets, refactor tasks) in any workspace. Trigger when the user says "draft an issue", "open an epic", "file a ticket", "write a Linear issue", or pastes a rough idea or bug report and asks for it to be filed.
---

# Linear Issue Craft

A portable issue-writing style. Every pattern in this skill is grounded in real shipped issues: see `references/06-canonical-examples.md` for verbatim source material.

## When this skill applies

Invoke when the user wants to create or polish a Linear issue and you have any signal that they want this style. Skip when the user explicitly asks for a different style or templates from another team.

## The three issue archetypes

Every issue is one of three shapes. Identify the archetype first: it determines title pattern, body sections, and labels.

| Archetype | When to use | Title shape | Body sections |
|---|---|---|---|
| **Epic** | Strategic surface, 2–8 child stories, shared infra/domain | `Epic: <Domain>` | Goal · Outcomes · Out of scope · Stories under this epic |
| **Story** | One PR, one acceptance test, one service/surface | imperative verb + concrete deliverable, or `<Role> — <Capability>` | (epic backlink) · User Story · Problem · Solution · Requirements · Evaluation |
| **Hardening** | Multiple vulnerabilities/bugs in one file/service | `Harden <file.ts>: <symptom1>, <symptom2>, <symptom3>` | Summary · Issues (numbered, each with **Fix:**) |

If a request doesn't fit one of these three, **stop and decompose** before writing. A "let's also rework X while we're at it" is a sibling story, not a bolted-on requirement.

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

## Golden rules (apply to every issue, every archetype)

1. **Concrete over abstract.** Name the file path, function, endpoint, table, env var. "Improve API performance" is rejected; "Add caching to `/search` endpoint (target p95 < 200ms on 10k events)" is accepted.
2. **Imperative verb first** on stories: Stand up · Wire · Harden · Build · Add · Generate · Refactor · Replace. Never passive ("Performance should be improved").
3. **Diagnose current state before proposing the fix.** Every epic opens with "Today …" or "Currently …" naming the deficiency in concrete terms (missing files, missing headers, missing endpoints). Skip the diagnosis and the issue reads like a press release.
4. **Reference past work explicitly.** Link related tickets by identifier, prior PRs, prior incidents. Use Linear's `<issue id="…">PROJ-XX</issue>` embed in Linear; plain `PROJ-XX` in plaintext.
5. **No em-dashes in prose.** The em-dash (`—`) is allowed in exactly one place: the separator in a role-prefixed story *title* (e.g., `Venue — Demand forecasting`). Everywhere else, including the "Stories under this epic" list (write `Story 1: …`), use a colon, a comma, or rewrite. `scripts/validate_issue.py` enforces this.
6. **Labels are layered, not flat.** Always pick one domain **plus** one or more capabilities (e.g., `ai`, `seo`, `compliance`, `tech-debt`, `ui-ux`). The domain set is whatever the target workspace already uses (`api`/`web`/`mobile`, or `api`/`frontend`, or per-service): run `list_issue_labels` and pick from the real list, never invent one. Don't use urgency or sprint labels.
7. **Priority maps to category, not urgency:** High = security / infra / epics. Medium = features. Low = exploratory / decision-support. No-priority = scoped-out or already done.

## How to use this skill

1. Identify the archetype (epic / story / hardening). When in doubt, ask the user.
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
4. Draft the issue, then run the validator on it (see "Validate before showing the draft"). It must exit 0 before you show the draft. Show it to the user before posting; never file without explicit approval of the final text.
5. If the user approves, file it with your Linear MCP server's `save_issue` tool (e.g. `mcp__linear__save_issue`; the exact prefix depends on how the server is registered in your client).

## Output contract

When this skill is active, every draft you produce must include:

- A **title** that follows one of the patterns in `references/01-title-patterns.md` verbatim.
- A **body** that uses the section headings in `references/02-description-templates.md` for its archetype, in order, with no extra sections.
- A **labels** array (1 domain + ≥1 capability) following `references/04-labels-and-priority.md`.
- A **priority** name (`High` / `Medium` / `Low` / `No priority`) chosen by the category rule.
- A short, conversational note to the user above the draft, summarizing why you chose this archetype and what alternative you considered. Keep it 2 sentences max.

## Validate before showing the draft

Two gates. Gate 1 is mechanical and non-negotiable. Gate 2 is judgment the script cannot make for you.

### Gate 1: run the validator (hard gate)

Run `scripts/validate_issue.py` (relative to this skill's directory) on the draft:

```bash
python3 scripts/validate_issue.py <draft-file>      # or pipe the draft on stdin
```

It must exit 0. It enforces: em-dash in prose, vague verbs ("improve"/"enhance"/"optimize") without a target metric, AI tells and `Co-Authored-By`, section names and order per archetype (catches `Description`/`Acceptance Criteria` drift), hardening `**Fix:**` lines, epic story count (2 to 8), label shape, and trailing-period titles. Fix every ERROR before showing the draft. WARNs do not block, but read them.

This is a gate, not a mental note. Do not show the user a draft you have not run through the validator. If `python3` is unavailable, that is a blocker to resolve (the script is stdlib-only, no install needed), not a reason to skip the gate.

### Gate 2: judgment checks (you, not the script)

- [ ] Title contains a concrete noun (file path, endpoint, component) or a Role-prefix.
- [ ] The diagnosis is accurate: the "Today …" sentence names real, current deficiencies you verified (grep the repo), not assumed ones.
- [ ] The User Story persona is a role the project actually uses, verified against the repo, its docs, or existing issues. Never an invented "operator" or "admin" when the project calls them "users".
- [ ] Labels match the target workspace's real taxonomy (you ran `list_issue_labels`), not a guessed set.
- [ ] If story: exactly one PR's worth of scope. A "while we're at it" is a sibling story, not a bolted-on requirement.
- [ ] The archetype is right: if the request did not fit epic/story/hardening, you decomposed instead of forcing it.

If Gate 1 reports any ERROR or any Gate 2 box is unchecked, fix it before showing the draft.
