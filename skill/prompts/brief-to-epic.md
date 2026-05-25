# Workflow: brief → epic + child stories

Use this when the user gives you a one-paragraph idea ("I want to add a referrals system", "we need to harden the auth layer", "let's bootstrap analytics") and wants a filed epic plus its child stories.

## Step 1 — Restate as a deficiency

Before writing anything, rephrase the user's brief as a current-state deficiency. The first sentence of the future epic's Goal must read like: "Today, <surface> has no <capability>. <Concrete missing artifacts>." If you can't write that sentence, you don't understand the brief yet — ask the user one clarifying question.

Test cases:

- Brief: "Add referrals." → "Today, the web app has no referrer attribution; we don't capture `?ref=` query params, don't persist a referrer cookie, and don't surface referrer in any user record."
- Brief: "Improve onboarding." → ask: "Which surface — `/register`, the mobile first-run flow, or the venue/promoter operator wizards?"

## Step 2 — Identify the domain and scope

Pick ONE domain label (`api` / `web` / `mobile`) for the epic. If the brief crosses domains, the epic is cross-cutting and its child stories will be split per-domain (one child per domain at most).

Decide which capability labels apply (`ai` / `seo` / `compliance` / `tech-debt` / `ui-ux`). The epic always carries `epic`.

## Step 3 — Decompose into 2–8 child stories

Each child must satisfy:

- One PR's worth of scope.
- One service or surface.
- One acceptance test that ties it back to the epic's outcomes.

Common decomposition patterns:

- **Layered foundation:** infra → first integration → first user-visible surface. (e.g., SEO epic: foundations → structured data → OG images.)
- **Per-role / per-surface:** one story per persona or per CRUD surface. (e.g., role-specific AI epic: artist → venue → promoter → operator → all roles.)
- **Sequential dependencies:** queue → observability → first job. (e.g., AI Foundation epic.)

If the decomposition produces more than 8 stories, the epic is too big — propose splitting it into two epics. If it produces fewer than 2, it's a story, not an epic.

## Step 4 — Draft the epic body

Use the Epic template from `references/02-description-templates.md`. Fill in:

```markdown
## Goal

<Today, <surface> has no <capability>. Three concrete deficiencies: <list>. <One-line strategic outcome.>>

## Outcomes

* <Externally observable outcome 1 — name the file/endpoint/page that will exist after.>
* <Externally observable outcome 2.>
* <Externally observable outcome 3.>
* <… up to 6.>

## Out of scope

* <Adjacent surface a reader might assume is included.>
* <Another, optional.>

## Stories under this epic

* Story 1 — <full child story title>
* Story 2 — <full child story title>
* Story 3 — <full child story title>
```

## Step 5 — Draft each child story body

Use the Story template from `references/02-description-templates.md` for each child. Confirm:

- Each story has a `**Epic:** <Epic name>` backlink and a `**Title:** <verbatim title>` line below it.
- The body is shaped as **User Story / Problem / Solution / Requirements / Evaluation** (or the bundled-concept variant if two primitives ship together).
- Requirements list 3–6 grep-able actions with file paths.
- Evaluation items map back to requirements with `**Validates R<n>**:` prefixes.
- The last Evaluation item is a soak/integration check.

## Step 6 — Show to user before filing

Output one consolidated draft showing:

1. The epic title + body + labels + priority.
2. Each child story title + body + labels + priority + parent.

Use this skeleton:

```markdown
# Proposed: <epic title>

I'm proposing **<N> child stories** under this epic. Archetype is **<epic vs. per-role epic vs. infra epic>**; the alternative was **<other shape considered>**, but **<reason>**.

---

## Epic

**Title:** Epic: <Domain>
**Labels:** epic, <domain>, <capability(ies)>
**Priority:** High

<full epic body>

---

## Story 1 of N

**Title:** <story title>
**Parent:** <Epic name>
**Labels:** <domain>, <capability(ies)>
**Priority:** <High/Medium/Low>

<full story body>

---

(repeat for each story)
```

Wait for explicit user approval. Then — and only then — call `mcp__linear-server__save_issue` per item. Set `parentId` to the epic's ID on each child.

## Step 7 — File and report

After filing, report back with:

- Epic identifier and URL.
- Each child identifier and URL.
- Any labels/priorities you couldn't set automatically (e.g., a new label that needs to be created first).

Do not post any external content (PR comments, Slack messages, etc.) about the filing without separate approval.
