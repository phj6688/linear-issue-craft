# Description templates

Each archetype has a fixed body skeleton. The headings appear in the order shown; do not invent new sections. If a section has no content for a given issue, **omit it** rather than writing "N/A".

---

## Epic body

```markdown
## Goal

<2–4 sentences. Open with "Today …" or "Currently …" diagnosing the deficiency in concrete terms (missing files, missing endpoints, missing capabilities). End with a one-line statement of the strategic outcome.>

## Outcomes

* <Bullet 1 — a single objective, concrete result. e.g., "The site has a valid `robots.txt` and `sitemap.xml` covering events, public profiles, and marketing routes.">
* <Bullet 2 …>
* <Bullet 3 …>
* <Bullet N. Aim for 3–6 bullets total.>

## Out of scope

* <Bullet 1 — a thing a reasonable reader might assume is included, but isn't. Names what NOT to do.>
* <Bullet 2 …>

## Stories under this epic

* Story 1 — <story title verbatim>
* Story 2 — <story title verbatim>
* Story 3 — <story title verbatim>
```

**Why each section:**
- **Goal** = current-state diagnosis + strategic framing. Always opens with the deficiency, never with the solution.
- **Outcomes** = the objective shape of the world after the epic ships. Each bullet should be observable from outside the team.
- **Out of scope** = boundary protection. Prevents scope creep and signals to reviewers that you considered adjacent surfaces.
- **Stories under this epic** = a flat list of child story titles. Children are 2–8 in number.

Canonical example: see Example 1 in `06-canonical-examples.md`.

---

## Story body

```markdown
**Epic:** <parent epic title without the "Epic:" prefix>

## User Story

As a <role>, I want <capability>, so that <outcome>.

## Description

<3–6 sentences. Open with the technical context (current state of the relevant file/service/component). Explain the approach in 1–2 sentences. Call out any constraint or simplifying decision (e.g., "This is one config change, no business-logic refactor.").>

## Requirements

1. <Concrete action 1, with file paths and identifiers. e.g., "Create `api/src/lib/openai-client.ts` exporting `getOpenAIClient()` that returns an OpenAI client configured with `baseURL: https://oai.helicone.ai/v1`.">
2. <Concrete action 2 …>
3. <Concrete action 3 …>
4. <Concrete action N. Aim for 3–6.>

## Acceptance Criteria

1. **Validates R<n> [+ R<m>]**: <How to verify, with the exact command or observation. e.g., "A test call from `api/` shows up in the Helicone dashboard within 10s with model, tokens, and cost; `rg \"from 'openai'\"` outside `openai-client.ts` returns zero hits.">
2. **Validates R<n>**: <…>
3. **Validates R<n>**: <…>
4. **Validates all**: <A holistic acceptance check that exercises the whole feature, e.g., "A 24h soak in staging shows zero 'fallback to direct OpenAI' log lines.">
```

**Why each section:**
- **Epic** backlink keeps Linear's parent relation visible even in PR descriptions, exports, and search.
- **User Story** is the only place where "As X, I want Y, so Z" is allowed. Forces the writer to name the persona and the *so-that* outcome.
- **Description** sets the technical context. Always names the file/service/component being touched. Always ends with a simplifying constraint or scope cap.
- **Requirements** are imperative. Each one is a single concrete action a reviewer can grep for in the diff.
- **Acceptance Criteria** are pairings: each AC explicitly cites which Requirement(s) it validates. The last AC is always a soak / integration check.

Canonical example: see Example 2 in `06-canonical-examples.md`.

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

**Fix:** <One-line proposed fix. Be specific — name the function or branch to change.>

### 2\. <Symptom name> (lines <range>)

<…>

**Fix:** <…>

### 3\. <Symptom name>

<…>

**Fix:** <…>
```

**Why each section:**
- **Summary** = scope + calibration. The calibration sentence ("None are currently exploitable at scale, but…") is what separates a hardening ticket from a panicked CVE filing. It tells the reader why this matters *now* even though nothing is on fire.
- **Issues** are numbered. Each header includes the symptom and the line range. Each entry ends with a `**Fix:**` line so the reader can scan the whole ticket for proposed fixes in one pass.

Canonical example: see Example 3 in `06-canonical-examples.md`.

---

## Cross-references

Always link related work. In Linear's editor, use `<issue id="<uuid>">PROJ-XX</issue>` (you can paste the ticket and Linear renders the embed). In plaintext drafts, write `PROJ-XX` and Linear will auto-link on paste.

Always cross-reference:
- The epic that contains a story (use the `**Epic:**` header line)
- The story or PR that surfaced a hardening ticket
- Any blocking/blocked-by relationship (mention it in the Description, not as a section)
