# Workflow: code-issue list → hardening ticket

Use this when the user gives you a list of issues in a single file or service ("here are 4 bugs in `auth.service.ts`") or when a code review surfaces multiple defects you want to file as one ticket.

## When to use one Hardening ticket vs. multiple stories

- **One Hardening ticket:** 2+ issues, all in one file or service, all of similar archetype (mostly defensive code / log leaks / input validation / fail-open paths).
- **Separate stories:** issues span multiple files or services, OR one of the issues is large enough to need its own User Story + Requirements + AC.

If unsure: if the fix for each issue is ≤ 1 line of code or one config edit, bundle them as Hardening. Otherwise split into stories.

## Step 1 — Catalog the issues

For each defect the user surfaces, capture:

- **Symptom name** (2–5 words, noun phrase): "Fail-open on API errors", "No URL validation on imageUrl", "Error objects may leak content to logs".
- **Location** (file, plus line range when the source provides one): `lines 42-45, 73-76, 111-113`.
- **Plain-language description** (2–4 sentences): what the code does, what's wrong, who could exploit it / what consumer impact.
- **Proposed fix** (1–2 sentences): the concrete change.

If any issue lacks a clear fix proposal, ask the user before drafting.

## Step 2 — Calibrate severity for the Summary

Write one sentence that calibrates how urgent this is **today** vs. how urgent it becomes **soon**. This is the move that separates a hardening ticket from a CVE filing. Example:

> None are currently exploitable at scale (moderation is only called from internal service code, not directly from user input), but they become real bugs as moderation is wired into more surfaces.

If a defect *is* currently exploitable, say so and propose paging:

> Issue #2 is reachable from unauthenticated traffic and should be patched in the next deploy; the others are not currently exposed.

## Step 3 — Compose the title

Pattern: `Harden <file-or-service-stem>: <symptom1>, <symptom2>, <symptom3>`.

- File stem is the short filename, not the full path (`openai-moderation.service.ts`, not `api/src/services/openai-moderation.service.ts`).
- Symptoms are noun phrases, comma-separated, 2–4 items. If you have more than 4, pick the worst 3 and let the body cover the rest.

Real example:
> `Harden openai-moderation.service.ts: fail-open, input validation, log leaks`

## Step 4 — Draft the body

Use the Hardening template from `references/02-description-templates.md`:

```markdown
## Summary

<2–4 sentences. Name the full file path. State how many issues. Optionally cite the work that surfaced them. End with the severity calibration sentence.>

## Issues

### 1\. <Symptom name> (lines <range>)

<2–4 sentences explaining the bug.>

**Fix:** <one-line proposed fix>

### 2\. <Symptom name> (lines <range>)

<…>

**Fix:** <…>

(repeat for each numbered issue)
```

## Step 5 — Labels and priority

- **Labels:** always include the domain label (`api` / `web` / `mobile`). Add `compliance` if any issue is security or privacy related. Add `tech-debt` if all issues are non-security defensive code.
- **Priority:** **High** if any issue is security/privacy. **Medium** if all are non-security defensive code. Never Low (a Low hardening ticket means you should have skipped filing it).

## Step 6 — Show to user before filing

Show the full draft (title + body + labels + priority). Ask for approval before calling `save_issue`.

Skeleton for the user-facing message:

```markdown
Drafted as a single Hardening ticket because all <N> issues live in `<file>` and each fix is small. Alternative was <N> separate stories; rejected because <reason>.

**Title:** Harden <stem>: <symptoms>
**Labels:** <domain>, <compliance/tech-debt>
**Priority:** <High/Medium>

<full body>
```

## Common mistakes to avoid

- **Missing per-issue `**Fix:**` line.** Every numbered issue must end with a Fix callout. Without it the ticket is just a bug list.
- **Mixing security and non-security issues without flagging.** If you bundle both, the Summary's severity calibration must call this out explicitly ("Issues 1–2 are security; issues 3–4 are defensive cleanup.").
- **Generic symptom names.** "Bug in input handling" is rejected. "No upper-bound length check on text input" is accepted.
- **Inventing line numbers.** Include `(lines X-Y)` in the issue header when the source gives them; reviewers scan for them. If the input has no line numbers, omit them rather than fabricating ranges.
