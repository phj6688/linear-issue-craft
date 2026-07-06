# Anti-patterns

The most common ways AI-drafted Linear issues drift away from this style. Each row pairs a generic-AI failure with the specific in-style fix.

## Title-level

| AI default | In-style fix |
|---|---|
| "Improve search performance" | "Add LRU cache to `/search`; target p95 < 200ms on 10k-event corpus" |
| "Refactor moderation service" | "Harden `openai-moderation.service.ts`: fail-open, input validation, log leaks" |
| "Implement SEO best practices" | "SEO foundations: robots.ts, sitemap.ts, metadataBase, canonicals, Organization JSON-LD" |
| "Set up async job processing" | "Stand up Trigger.dev v3 in `api/` with first reference job + CI deploy" |
| "Improve dynamic pricing logic for venues" | "Venue — Demand forecasting + AI-suggested dynamic ticket pricing (highest-leverage)" |
| "Various UX improvements" | (Decompose into one issue per surface; do not file the bundled version.) |

## Body-level

### Collapsed Problem and Solution
**AI default:** A single `## Description` blob that mixes "today the system has no X" with "we will build Y" in one paragraph.

**In-style fix:** Split into `## Problem` (current-state diagnosis only) and `## Solution` (what we are building, ending with a simplifying constraint). A reader skimming the headers should be able to answer "what's broken" and "what's the fix" without reading the prose.

### "Press release" opening in Problem
**AI default:** "This issue adds a hardened security header layer to the web app, providing defense in depth against XSS, clickjacking, and information disclosure attacks."

**In-style fix:** Open `## Problem` with the current-state deficiency, not the future state.
> `web/next.config.ts` only sets `Content-Type` headers for app-link well-knowns. There is no Content-Security-Policy, no HSTS, no X-Frame-Options, no Referrer-Policy, no Permissions-Policy. These are baseline expectations for a 2026 production web app.

### Vague requirements
**AI default:**
> 1. Implement caching layer
> 2. Add monitoring
> 3. Document the change

**In-style fix:** every requirement is one grep-able action with a file path.
> 1. Create `api/src/lib/openai-client.ts` exporting `getOpenAIClient()` that returns an OpenAI client configured with `baseURL: https://oai.helicone.ai/v1` and the Helicone auth header set from `HELICONE_API_KEY`.
> 2. Refactor every OpenAI import in `api/src/` to use the new wrapper; verify with `rg "from 'openai'"` returning hits only in `openai-client.ts`.

### Decoupled Evaluation
**AI default:** A separate list of "tests should pass" with no mapping back to requirements.

**In-style fix:** every Evaluation item names which Requirements it validates.
> 1. **Validates R1 + R2**: A test call from `api/` shows up in the Helicone dashboard within 10s with model, tokens, and cost; `rg "from 'openai'"` outside `openai-client.ts` returns zero hits.

### Unobservable acceptance closer
**AI default:** The last Evaluation item leans on something no headless stage can run: `A 24h soak in staging shows zero "fallback to direct OpenAI" log lines.`

**In-style fix:** the last item is a holistic check runnable headless against the checkout, exercising the real seam (not a stub of the thing under test). Push the soak to a `## Post-ship follow-up` line.
> 4. **Validates all**: `pytest api/tests/test_openai_client.py` passes and `rg "from 'openai'"` outside `openai-client.ts` returns zero hits.

### Section name drift ("Acceptance Criteria" instead of "Evaluation")
**Signal:** Story ends with `## Acceptance Criteria` instead of `## Evaluation`.
**Fix:** Rename to `## Evaluation`. The shape is identical (each item still cites which Requirement it validates), but the house-style header is `Evaluation`.

## Voice-level

### Em-dashes in prose
**AI default:** "The proxy adds an observability layer — including cost, latency, and error rates per feature — without changing business logic."

**In-style fix:** rewrite without the em-dash.
> The proxy adds an observability layer (cost, latency, and error rates per feature) without changing business logic.

### Apology / hedge
**AI default:** "It's worth noting that there might be some edge cases around rate limiting that we should probably handle."

**In-style fix:** state the issue directly.
> The retry path doesn't distinguish 429s from 5xx; both currently fail open.

### Self-congratulation
**AI default:** "This comprehensive, production-ready implementation provides robust handling of all edge cases."

**In-style fix:** delete the entire sentence. Show, don't tell.

### Generic outcomes
**AI default:**
> ## Outcomes
> * Improved security
> * Better performance
> * Cleaner code

**In-style fix:** every outcome is observable from outside the team.
> ## Outcomes
> * The site has a valid `robots.txt` and `sitemap.xml` covering events, public profiles, and marketing routes.
> * Every page has a canonical URL; filterable surfaces (`/events?genre=…`) don't create duplicate-content problems.

## Structural

### Bundled scope (wrong)
**Signal:** Story body has more than 6 requirements, or two distinct surfaces (`api/` and `web/`).
**Fix:** split into siblings. Reference the new sibling in the original Problem section.

### Bundled scope (right, but uncategorized)
**Signal:** Two related primitives ship together because splitting would let the team forget one, but the body is one undifferentiated `## Description` paragraph.
**Fix:** use the bundled-concept variant from `02-description-templates.md`. Frame the shared problem in `## Problem`, then break the body into `### Concept 1` / `### Concept 2` blocks (each with bolded `**Problem:**` and `**Solution:**`), then `### Why bundled`.

### Missing Out-of-scope on epics
**Signal:** Epic doesn't say what it isn't.
**Fix:** Add 1–3 "Out of scope" bullets naming the adjacent surfaces a reader might assume are included.

### Hardening ticket without per-issue Fix line
**Signal:** Issues are listed but no `**Fix:**` callouts.
**Fix:** every numbered issue ends with `**Fix:** <one-line proposed change>`. This lets a reviewer scan and triage in one pass.

### Story without "Epic:" backlink
**Signal:** The story stands alone with no parent reference.
**Fix:** Add `**Epic:** <Epic name>` as the first line of the body (Linear's parent relation alone is not enough: PR descriptions and exports lose it). If the story is genuinely standalone, write `**Epic:** none` so the omission is deliberate, not an oversight. The validator warns on a missing backlink; it does not block.

### Missing Anchor
**Signal:** A story or task has no `**Anchor:**` line, or the anchor is prose ("the auth flow").
**Fix:** Name one machine-resolvable target: `file.ext:line`, `file.ext:symbol`, `module.function`, `METHOD /path -> status`, or `playwright:selector`. The held-out probe binds to this; a probe cannot test a thing the issue never named.

### Story with no Out-of-scope
**Signal:** A story lists Requirements but never says what it is *not* doing.
**Fix:** Add a `## Out of scope` bullet naming one non-goal. The implementer is an autonomous agent and will gold-plate past the intended scope without an explicit boundary.

## Labels / priority

| AI default | In-style fix |
|---|---|
| Labels: `frontend`, `backend`, `urgent` | Labels: `web`, `api`, plus capabilities (`compliance`, `ai`, …) |
| Priority: Urgent (because user mentioned it twice) | Priority: High if security/infra/epic; otherwise Medium. |
| Priority: High (because it's a big feature) | Priority: Medium if user-facing feature; only High if it gates compliance/security. |

## When in doubt

If a draft feels generic or sycophantic when you read it back, the easiest fixes are:

1. Add 2–3 file paths in the Problem section.
2. Replace any "improve / enhance / optimize" verb with a metric-named action.
3. Add the current-state diagnosis sentence to the top.
4. Remove every adjective that describes the change itself ("comprehensive", "robust", "thoughtful").
