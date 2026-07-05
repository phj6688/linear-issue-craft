# Workflow: code smell / tech-debt note → refactor story

Use this when the user identifies a piece of code that works but is fragile, duplicated, or blocks future work, and wants a single story filed against it.

## When this is the right archetype

A refactor story is **not** a hardening ticket. Distinctions:

| Refactor story | Hardening ticket |
|---|---|
| One coherent change to one surface | Multiple distinct defects in one file |
| Behavior preserved by design | Behavior changes (e.g., fail-closed) |
| No security implication | Often security/privacy-adjacent |
| Has User Story + Problem + Solution + Requirements + Evaluation | Has Summary + Issues + Fixes |
| Labels: domain + `tech-debt` | Labels: domain + `compliance` |

A refactor story is **not** an epic. If the refactor touches more than one surface, split it into sibling stories and file an epic over them.

## Step 1: Name the current state and the constraint

Open with one sentence diagnosing the current shape, and one sentence stating the constraint that makes it a problem. Test cases:

- Current: "`web/lib/api-client.ts` has 14 endpoint-specific helper functions, each a near-duplicate of the others."
- Constraint: "Adding a new endpoint requires copy-pasting the boilerplate, and a recent change to error handling had to be applied in 14 places (3 were missed)."

Do not propose the fix yet. That comes in the Solution section.

## Step 2: Compose the title

Refactor stories use a regular Story title (imperative verb + concrete deliverable). Common verbs:

- `Replace`: when swapping one implementation for another. e.g., `Replace per-endpoint api-client helpers with a single typed request builder`.
- `Consolidate`: when merging duplicated code paths. e.g., `Consolidate event-card rendering into one component (currently 3 forks)`.
- `Extract`: when pulling shared logic out. e.g., `Extract shared validation logic from {user,event,venue}.controller.ts into a middleware`.
- `Migrate`: when moving to a different library/pattern. e.g., `Migrate auth middleware from express-jwt to in-house jwt.service.ts`.
- `Drop`: when removing dead code. e.g., `Drop unused supabase.auth.resetPasswordForEmail call from /forgot-password handler`.

If the title sounds like a story to add a *feature*, you're not writing a refactor story: you're writing a feature story that happens to include refactoring.

## Step 3: Draft the body

Use the Story template. The shape is the same as a feature story, but the User Story has a particular flavor:

```markdown
**Epic:** <parent epic, or `none` for a deliberately standalone refactor>
**Title:** <verbatim story title>
**Anchor:** <the new file/function being introduced, e.g. web/lib/request.ts:buildRequest>

## User Story

As an engineer working on <surface>, I want <unified pattern>, so that <future change is one-place, not N-places>.

## Problem

<Open with "Today …" or "Currently …". State the current shape in 1–2 sentences: file paths and the count of duplicated sites. State the constraint that makes it a problem in one sentence (e.g., a recent change had to be applied in 14 places and 3 were missed).>

## Solution

<Name the proposed shape in 1–2 sentences. Reference the file/function being introduced. End with a simplifying constraint or scope boundary (e.g., "Behavior is preserved by design; the existing integration test suite covers the diff with no edits.").>

## Out of scope

* <One adjacent cleanup a reader might assume is bundled but isn't. Keeps the refactor one PR.>

## Requirements

1. <Concrete action 1, name the new file/function being introduced.>
2. <Concrete action 2, name the call sites being updated.>
3. <Concrete action 3, verification command, e.g., `rg "<old pattern>"` returning zero hits.>
4. <Concrete action 4, tests added/updated.>

## Evaluation

1. **Validates R1 + R2**: <observation, e.g., "All `<surface>` consumers import from the new module; `rg \"<old pattern>\"` returns zero hits.">
2. **Validates R3**: <test results / build output.>
3. **Validates all**: **No behavior change.** <how to verify externally headless, e.g., "the existing integration test suite passes with no edits.">
```

## Step 4: Labels and priority

- **Labels:** domain (`api` / `web` / `mobile`) + `tech-debt`. Add `ai` if the surface is AI infrastructure, `ui-ux` if the surface is presentational, etc.
- **Priority:** Default **Low**. Raise to **Medium** only if the debt is actively blocking another epic or causing repeated bugs. Never **High** for a pure refactor.

## Step 5: The "no behavior change" gate

Every refactor story's last Evaluation item must read: **No behavior change.** This is the bright line that distinguishes a refactor from a redesign. If the user's brief implies a behavior change (e.g., "while we're at it, let's also add caching"), split the caching into a sibling story. Don't pollute the refactor.

If you can't honestly write "No behavior change" as the last Evaluation item, it's not a refactor story; revisit the archetype.

## Step 6: Show to user before filing

Skeleton:

```markdown
Drafted as a refactor story because the change preserves behavior and touches a single surface. Alternative was a hardening ticket; rejected because the issues here aren't defects in the current code: it just doesn't scale.

**Title:** <title>
**Anchor:** <the new file/function being introduced>
**Labels:** <domain>, tech-debt
**Priority:** Low

<full body>
```

Wait for explicit approval, and run the validator (Gate 1) on the draft first. Then file with your Linear MCP `save_issue` tool (e.g. `mcp__linear__save_issue`). Do not silently bundle in any unrelated cleanup.

## Common mistakes to avoid

- **Smuggling a feature into a refactor.** If the user mentions "and while we're at it, …", flag it and propose a separate story.
- **Vague "improve maintainability" framing.** Replace with the specific number of duplicated sites or the specific upcoming change that's blocked.
- **Missing the no-behavior-change Evaluation item.** That's the contract that lets the reviewer approve the diff quickly.
- **Priority creep.** A refactor with no upstream consumer pressure should stay Low. If it's blocking work, the blocking work is the story, not the refactor.
