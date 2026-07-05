# Title patterns

Every issue title follows one of the patterns below. Pick the matching pattern; never invent a new one.

## 1. Epic: `Epic: <Domain>`

Use Title Case for the domain. Keep it to 2–5 words. The domain should map to a real business area, not an implementation detail.

Real examples:
- `Epic: SEO & Discoverability`
- `Epic: Security & Compliance`
- `Epic: Quality baseline`
- `Epic: AI Foundation / Platform infra`
- `Epic: Public-facing UX`
- `Epic: Role-specific AI Insights & Decision Support`

Avoid:
- `Epic: Backend stuff` (too vague)
- `Epic: Q3 work` (timeline, not domain)
- `Epic: Misc improvements` (no domain)

## 2. Story: imperative verb + concrete deliverable

Start with one of: `Stand up`, `Wire`, `Add`, `Build`, `Harden`, `Generate`, `Replace`, `Refactor`, `Implement`, `Migrate`. Then name the concrete thing being delivered, with a file path, endpoint, or component name.

Real examples:
- `Stand up Trigger.dev v3 in api/ with first reference job + CI deploy`
- `Add Helicone proxy for all OpenAI calls with cost + latency dashboard`
- `Build guest landing page at /`
- `Schema.org Event JSON-LD on event detail pages`
- `Dynamic Open Graph image generation per event`
- `Full public-artist coverage in sitemap`
- `Hardened security headers (CSP, HSTS, X-Frame-Options, etc.)`

Avoid:
- `Improve authentication` (no path, no specific deliverable)
- `Performance work` (no verb of action, no scope)
- `Various UX tweaks` (plural, no target)

## 3. Story (role-prefixed): `<Role> — <Capability>`

The em-dash is mandatory here. The role names a primary user persona (Artist / Venue / Promoter / Operator / All roles). The capability is one concrete decision-support or feature surface.

Real examples:
- `Artist — Per-show performance analytics narrative + setlist suggestions`
- `Venue — Demand forecasting + AI-suggested dynamic ticket pricing (highest-leverage)`
- `All roles — Weekly/monthly AI-summarized performance digest`

Use an optional trailing parenthetical to flag leverage or risk: `(highest-leverage)`, `(blocks EU traffic)`, `(requires DB migration)`.

## 4. Hardening: `Harden <file.ts>: <symptom1>, <symptom2>, <symptom3>`

Use when **multiple distinct issues** live in **one file or service**. The filename (or file path stem) comes immediately after `Harden`, then a colon, then a comma-separated symptom list of 2–4 items. Each symptom should be a noun phrase, not a sentence.

Real example:
- `Harden openai-moderation.service.ts: fail-open, input validation, log leaks` (see Example 3 in canonical examples)

Variant for system-wide hardening of headers/policies (not file-specific):
- `Hardened security headers (CSP, HSTS, X-Frame-Options, etc.)`
- `GDPR cookie consent banner with granular categories`

## 5. Setup / foundation: `<Capability> foundations: <comma-separated artifacts>`

Used when bootstrapping a multi-artifact infrastructure layer in one shot.

Real example:
- `SEO foundations: robots.ts, sitemap.ts, metadataBase, canonicals, Organization JSON-LD`

## 6. Task: imperative deliverable (Bug / Chore / Spike / Ops)

A single small bug, chore, spike, or ops change uses a plain imperative title, with the kind set in the body's `**Type:**` header (or an optional `Bug:` / `Chore:` / `Spike:` prefix). Same concreteness rules as a story title.

Real examples:
- `Fix drag reset on pointerup in the 3D graph`
- `Bump Node to 20 in the api Dockerfile and CI`
- `Spike: is the --strict-mcp-config envelope honored by the runner?`

Avoid:
- `Fix the bug` (no target)
- `Cleanup` (no verb of action, no scope)

## House rules for all titles

- **Capitalization:** Title Case for the leading noun (`Epic`, `SEO`) and for trademarked tool names (`Schema.org`, `Trigger.dev`, `Helicone`); sentence case for the rest.
- **No trailing period.**
- **Backticks** for file paths, env var names, and code identifiers: `` `robots.ts` ``, `` `api/` ``.
- **No emoji.**
- **No em-dash** anywhere except the Role-prefix separator (pattern 3).
- **Length:** 6–14 words. If you go longer, you're probably bundling two stories.

## Title quality test

Read your candidate title out loud. Can a reviewer who has never seen the issue answer all three questions?

1. **What** is being built/fixed?
2. **Where** in the codebase or user surface?
3. **Why** is it distinct from neighboring work?

If any answer is "I'd have to open the description," rewrite the title.
