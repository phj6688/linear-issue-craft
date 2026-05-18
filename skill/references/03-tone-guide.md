# Tone guide

The voice is concise, technical, current-state-aware, and never apologetic. Below is a side-by-side of what to write vs. what to reject.

## Concrete > abstract

Every claim is anchored to a file path, function, endpoint, env var, or tool name. Generic nouns ("the backend", "the user flow", "performance") are placeholders, never finished prose.

| Reject | Write |
|---|---|
| The API is slow under load. | The `/search` endpoint p95 is 1.4s on a 10k-event corpus (target: <200ms). |
| There's no SEO setup. | There is no `robots.ts`, no `sitemap.ts`, no `metadataBase`, no canonical URLs, and no structured data. |
| We should add observability. | Add Helicone as a transparent proxy in front of OpenAI; existing `api/src/services/openai-moderation.service.ts` imports a small `getOpenAIClient()` wrapper. |

## Diagnose, then propose

The opening paragraph of every epic and most stories starts with current-state diagnosis. Never lead with the solution.

| Reject | Write |
|---|---|
| Add a sitemap.xml so the site is crawlable. | Today the public web app is effectively invisible to search engines: there is no `robots.ts`, no `sitemap.ts`, no `metadataBase`. … For an events platform, this is the single highest-leverage gap. |
| Build a hardened headers middleware. | `web/next.config.ts` only sets `Content-Type` headers for app-link well-knowns. There is no Content-Security-Policy, no HSTS, no X-Frame-Options. … These are baseline expectations for a 2026 production web app. |

## Calibrate severity honestly

Hardening tickets and security work always say *out loud* whether something is exploitable today, and why it still matters.

> Four vulnerabilities in `api/src/services/openai-moderation.service.ts` found during the Helicone proxy work. None are currently exploitable at scale (moderation is only called from internal service code, not directly from user input), but they become real bugs as moderation is wired into more surfaces. (Example 3 — Hardening)

This single sentence does three jobs: scopes the work, calibrates urgency, and justifies prioritization. Imitate it.

## Imperative verbs, first position

Stories open with action verbs. Even in body prose:

> **Add** Helicone as a transparent proxy in front of OpenAI. The existing `api/src/services/openai-moderation.service.ts` and any future LLM caller **imports** a small `getOpenAIClient()` wrapper that **points** `baseURL` at Helicone. **This is one config change**, no business-logic refactor. (Example 2 — Story)

## No filler, no hedging, no apology

| Reject | Write |
|---|---|
| It might be worth considering adding caching. | Add an in-memory LRU cache to `/search` keyed on the normalized query string. |
| We should probably look into improving the build. | Replace the `tsc && next build` invocation in `web/package.json` with `next build` (Next handles type-checking via its plugin since 14.x). |
| There are some concerns around the auth flow. | The auth flow has three defects: <list>. |

## Constraint clauses

Long sentences are fine when they enumerate constraints. The hallmark move: one comma-separated list of must-haves.

> The banner must default to deny, expose granular categories (necessary, analytics, marketing/ads, functional), persist the user's choice durably, and gate any non-essential script from firing until consent is granted. (Story — GDPR cookie consent banner)

Imitate the rhythm: subject + must + comma-list of obligations.

## Hard "no" list

- **Em-dashes (`—`, `–`) in body prose.** Outside the Role-prefix in titles, never use them. Substitute period, comma, or rewrite.
- **AI tells:** "Let me", "I'll go ahead and", "It's worth noting that", "Confirmed empirically", "Belt-and-suspenders", "Non-optional per the type".
- **Mathematical notation:** ∈, ∀, →. Write English.
- **Self-congratulation:** "comprehensive", "robust", "production-ready", "elegant".
- **Apologies on behalf of the project:** "Unfortunately we don't have …", "Sorry for the rough edge here".
- **Co-Authored-By trailers** in commit messages (per project CLAUDE.md). Issue bodies don't get them either.
- **Emoji.** None, anywhere.

## Length calibration

| Issue type | Body length | Sections |
|---|---|---|
| Epic | 200–500 words | Goal · Outcomes · Out of scope · Stories under this epic |
| Story (simple) | 100–250 words | Epic backlink · User Story · Description · Requirements (3–4) · Acceptance Criteria (3–4) |
| Story (complex infra) | 250–500 words | Same sections, denser Requirements (5–6) |
| Hardening | 200–400 words | Summary · Issues (3–5 numbered items) |

Going past 500 words is a code smell — you're probably bundling two issues.

## Reading test

After drafting, read the title + Goal/Description paragraph out loud. Can a reviewer who has never seen the code:

1. Tell you the file or surface being changed?
2. Tell you the deficiency being fixed?
3. Tell you what a successful PR diff would look like?

If any answer is "I'd have to ask you," rewrite.
