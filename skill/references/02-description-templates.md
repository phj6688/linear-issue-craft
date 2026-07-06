# Description templates

Each archetype has a fixed body skeleton. The headings appear in the order shown; do not invent new sections. If a section has no content for a given issue, **omit it** rather than writing "N/A".

---

## Epic body

```markdown
## Goal

<2–4 sentences. Open with "Today …" or "Currently …" diagnosing the deficiency in concrete terms (missing files, missing endpoints, missing capabilities). End with a one-line statement of the strategic outcome.>

## Outcomes

* <Bullet 1: a single objective, concrete result. e.g., "The site has a valid `robots.txt` and `sitemap.xml` covering events, public profiles, and marketing routes.">
* <Bullet 2 …>
* <Bullet 3 …>
* <Bullet N. Aim for 3–6 bullets total.>

## Out of scope

* <Bullet 1: a thing a reasonable reader might assume is included, but isn't. Names what NOT to do.>
* <Bullet 2 …>

## Stories under this epic

* Story 1: <story title verbatim>
* Story 2: <story title verbatim>
* Story 3: <story title verbatim>
```

**Why each section:**
- **Goal** = current-state diagnosis + strategic framing. Always opens with the deficiency, never with the solution.
- **Outcomes** = the objective shape of the world after the epic ships. Each bullet should be observable from outside the team.
- **Out of scope** = boundary protection. Prevents scope creep and signals to reviewers that you considered adjacent surfaces.
- **Stories under this epic** = a flat list of child story titles. Children are 2–8 in number.

Canonical example: see Example 1 in `06-canonical-examples.md`.

---

## Story body

Every story follows a four-beat mental model: **User Story**, then **Problem**, then **Solution**, then **Evaluation**. Persona and outcome (User Story). What is broken or missing today (Problem). What we are building and the chosen approach (Solution). How we will know it works (Evaluation). Even when a story is short, this scan-ability is the defining feature of the house style. A reader should be able to skim the section headers alone and answer "who, what's wrong, what's the fix, how do we verify."

```markdown
**Epic:** <parent epic title without the "Epic:" prefix, or `none` for a deliberately standalone story>
**Title:** <verbatim story title, matching the issue title exactly>
**Anchor:** <one machine-resolvable target: file.ext:line | file.ext:symbol | module.function | METHOD /path -> status | playwright:selector>

## User Story

As a <role>, I want <capability>, so that <outcome>.

## Problem

<2–4 sentences. Open with "Today …" or "Currently …" diagnosing the deficiency in concrete terms. Name the file, service, endpoint, or surface. State what is missing, broken, or fragile. End with one sentence on why this matters now.>

## Solution

<2–4 sentences. Name what we are building and the chosen approach. Reference the file/service being touched. End with a simplifying constraint or scope cap (e.g., "This is one config change, no business-logic refactor."). Keep the sketch to ~10 lines; do not paste a design doc or prescribe a library unless it is a hard constraint. Over-specifying pre-commits the implementer.>

## Out of scope

* <One non-goal a reasonable implementer might otherwise pull in. Bounds the scope so the change stays one PR.>

## Requirements

1. <Concrete action 1, with file paths and identifiers. e.g., "Create `api/src/lib/openai-client.ts` exporting `getOpenAIClient()` that returns an OpenAI client configured with `baseURL: https://oai.helicone.ai/v1`.">
2. <Concrete action 2 …>
3. <Concrete action 3 …>
4. <Concrete action N. Aim for 3–6.>

## Evaluation

1. **Validates R<n> [+ R<m>]**: <How to verify, with the exact command or observation. e.g., "`rg \"from 'openai'\"` outside `openai-client.ts` returns zero hits; a unit test asserts the client's baseURL.">
2. **Validates R<n>**: <…>
3. **Validates R<n>**: <…>
4. **Validates all**: <A holistic acceptance check runnable headless against the checkout, e.g., "`pytest api/tests/test_openai_client.py` passes and the wrapper is the only importer of `openai`.">

## Post-ship follow-up

<Optional. Checks that cannot run headless (a 24h soak, a dashboard read, a prod-credential check). These are follow-ups, never the acceptance above.>
```

**Why each section:**
- **Epic** backlink keeps Linear's parent relation visible in PR descriptions, exports, and search; use `none` for a true standalone. **Title** restates the issue title verbatim so the body remains self-identifying when copied out of Linear.
- **Anchor** names the one thing the held-out probe binds to. It must be addressable (a path with a line or symbol, a dotted module.function, an HTTP `METHOD /path -> status`, or a `playwright:` selector), not prose. The probe cannot test what the issue never named.
- **User Story** is the only place where "As X, I want Y, so Z" is allowed. Forces the writer to name the persona and the *so-that* outcome. The persona must be a role the project actually uses: confirm the term against the repo, its docs, or existing issues before writing it. A named-but-invented persona ("operator", "admin") looks concrete and slips past the abstract-noun check, so it is called out explicitly. If the project calls them "users", write "user".
- **Problem** diagnoses current state. Always names the file/service/component being touched. Never leads with the fix.
- **Solution** explains what we are building and the approach. Always ends with a simplifying constraint or scope cap so reviewers can see the boundary.
- **Out of scope** names at least one non-goal. The implementer is an autonomous agent that will gold-plate without an explicit boundary.
- **Requirements** are imperative. Each one is a single concrete action a reviewer can grep for in the diff. This section is the reviewer's rubric downstream, so keep each item checkable against a diff.
- **Evaluation** items are pairings: each one explicitly cites which Requirement(s) it validates. Every item is runnable headless against the checkout; the last item is a holistic acceptance check that exercises the real seam (not a stubbed version of the thing under test). Soaks, dashboards, and staging checks move to **Post-ship follow-up**.

Canonical example: see Example 2 in `06-canonical-examples.md`.

### Bundled-concept variant (multi-primitive stories)

Some stories ship two or more related primitives together because splitting them would let the team forget one (e.g., "every AI feature ships with an eval AND behind a flag"). For these, keep User Story / Requirements / Evaluation at the H2 level, but expand the middle into per-concept sub-blocks:

```markdown
**Epic:** <name>
**Title:** <verbatim title>

## User Story

As a <role>, I want <both primitives>, so that <combined outcome>.

## Problem

<1–2 sentences framing the shared problem the bundle solves. Then one sentence introducing that this work bundles N related primitives.>

### Concept 1: <short name>

**Problem:** <2–4 sentences. The specific gap this primitive closes. Plain English; analogies are welcome.>

**Solution:** <2–5 sentences. What we build, the chosen mechanism, and why it suits this codebase. Side-comments and sentence fragments are fine ("Slow + scary.", "Same mental model as `pnpm test` for normal code, just for AI quality.").>

### Concept 2: <short name>

**Problem:** <…>

**Solution:** <…>

### Why bundled

<2–3 sentences explaining why splitting these into sibling stories would cause cross-cutting drift, and what bundling enforces.>

## Requirements

1. …

## Evaluation

1. …
```

Use this variant only when both of the following are true:
- The work delivers two or more clearly nameable primitives that share a single user story.
- Splitting would create a real risk that one primitive ships without the other.

If either is false, file two sibling stories instead. For a backlog that will be run by the autonomous pipeline, prefer siblings: one issue is one branch and one held-out probe, and a single probe can pass on the finished half of a bundle. If you do bundle, give each concept its own acceptance item in Evaluation so no primitive is left unchecked.

### Epic-level story variant

Epics themselves can also be filed as work items (e.g., an AI Foundation infra epic that you actually want to track in flight). When the epic is the work item, prepend:

```markdown
**Type:** Epic
**Title:** Epic: <Domain>

## Epic-level User Story

As <stakeholder>, we want <capability set>, so that <strategic outcome>.

## Goal

<same as epic body Goal section>
```

Then continue with Outcomes / Out of scope / Stories under this epic.

---

## Hardening body

```markdown
## Summary

<2–4 sentences. Name the file path. State how many issues. Optionally cite the work that surfaced them ("found during the Helicone proxy work <issue id="…">PROJ-XX</issue>"). Calibrate exploitability. Say what *is* and *isn't* currently dangerous.>

## Issues

### 1\. <Symptom name> (lines <range>)

<1–3 sentences describing the bug in plain language. Name the lines, the failure mode, and the consumer impact.>

**Fix:** <One-line proposed fix. Be specific: name the function or branch to change.>

### 2\. <Symptom name> (lines <range>)

<…>

**Fix:** <…>
**Verify:** <One runnable check that proves the fix, with expected output. e.g., "`pytest -k fail_closed` asserts a blocked result when the API errors.">

### 3\. <Symptom name>

<…>

**Fix:** <…>
**Verify:** <…>
```

**Why each section:**
- **Summary** = scope + calibration. The calibration sentence ("None are currently exploitable at scale, but…") is what separates a hardening ticket from a panicked CVE filing. It tells the reader why this matters *now* even though nothing is on fire.
- **Issues** are numbered. Each header includes the symptom and the line range. Each entry ends with a `**Fix:**` line so the reader can scan the whole ticket for proposed fixes in one pass, and a `**Verify:**` line so the downstream reviewer and probe have an observable acceptance per issue (a hardening ticket has no Requirements section, so the `**Verify:**` line is where its testable contract lives).

Canonical example: see Example 3 in `06-canonical-examples.md`.

---

## Task body (bug / chore / spike / ops)

A single bug, chore, spike, or ops change that does not need the full story ceremony. Select it with a `**Type:**` header. No persona, no requirement-to-evaluation mapping, but it still carries an Anchor and a runnable Verification.

```markdown
**Type:** Bug        <!-- or Chore / Spike / Ops -->
**Title:** <imperative deliverable, e.g., "Fix drag reset on pointerup in the 3D graph">
**Anchor:** <file.ext:line | file.ext:symbol | module.function | METHOD /path -> status | playwright:selector>

## Problem

<1–3 sentences. For a bug: the current wrong behavior, named at the anchor (`graph-3d.tsx:657`). For a chore/spike: the concrete task and why now.>

## Verification

<One runnable check with expected output, e.g., "`npx playwright test drag-pin` shows the node stays pinned after release." A spike may instead state the concrete question to answer and where the answer gets recorded.>
```

**Why each section:**
- **Type** selects the lightweight shape so a one-line bug is not inflated into a Story or mis-filed as a one-issue Hardening ticket.
- **Anchor** and **Verification** are the minimum contract: name the seam, and give one command a headless stage can run.

Canonical example: see Example 5 in `06-canonical-examples.md`.

---

## Cross-references

Always link related work. In Linear's editor, use `<issue id="<uuid>">PROJ-XX</issue>` (you can paste the ticket and Linear renders the embed). In plaintext drafts, write `PROJ-XX` and Linear will auto-link on paste.

Always cross-reference:
- The epic that contains a story (use the `**Epic:**` header line)
- The story or PR that surfaced a hardening ticket
- Any blocking/blocked-by relationship. Set it as a real Linear blocked-by relation (the planner builds its execution order from the relation, not from prose), and optionally mention it inside Problem or Solution.
