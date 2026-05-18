# Canonical examples

Three verbatim shipped issues. Treat these as the gold standard — when in doubt, structure your draft to match the example whose archetype you're writing.

Workspace-specific identifiers have been anonymized to `PROJ-N`. The prose, structure, and body content are otherwise unchanged from real shipped issues.

---

## Example 1 — Epic (PROJ-1)

**Title:** `Epic: SEO & Discoverability`

**Labels:** `epic`, `web`, `seo`
**Priority:** No priority (status: Done)

**Body:**

> ## Goal
>
> Make the product discoverable. Today the public web app is effectively invisible to search engines: there is no `robots.ts`, no `sitemap.ts`, no `metadataBase`, no canonical URLs, and no structured data. Google has neither a crawl map nor enough signal to surface the brand or any specific event in rich results. For an events platform, this is the single highest-leverage gap: events are exactly the content type Google has a dedicated rich-result format for (the Events carousel), and we ship none of the markup needed to qualify.
>
> ## Outcomes
>
> * The site has a valid `robots.txt` and `sitemap.xml` covering events, public profiles, and marketing routes.
> * Every page has a canonical URL; filterable surfaces (`/events?genre=…`) don't create duplicate-content problems.
> * The brand has Organization + WebSite JSON-LD so Google recognizes the entity.
> * Every public event detail page emits Schema.org `Event` JSON-LD, qualifying for the Events carousel.
> * Shared event links carry custom Open Graph images instead of a generic site image.
>
> ## Out of scope
>
> * Indexing/ranking of authenticated routes (those should be `noindex`).
> * API/backend changes. All work is in `web/app/` metadata files and component-level JSON-LD scripts.
>
> ## Stories under this epic
>
> * Story 1 — SEO foundations: robots.ts, sitemap.ts, metadataBase, canonicals, Organization JSON-LD
> * Story 2 — Schema.org Event JSON-LD on event detail pages
> * Story 3 — Dynamic OG image generation per event

**What to imitate:**
- First sentence diagnoses the gap with file paths.
- Outcomes bullets are externally observable.
- Out-of-scope explicitly references the adjacent surface that's *not* part of this work.
- Stories are named by their full story title, not a paraphrase.

---

## Example 2 — Story (PROJ-19)

**Title:** `Add Helicone proxy for all OpenAI calls with cost + latency dashboard`

**Labels:** `api`, `ai`
**Priority:** No priority (status: Done)
**Parent:** `Epic: AI Foundation / Platform infra`

**Body:**

> **Epic:** AI Foundation / Platform infra
> **Title:** Add Helicone proxy for all OpenAI calls with cost + latency dashboard
>
> ## User Story
>
> As an operator, I want every LLM call routed through an observability gateway, so that I can see real-time cost, latency, and error rates per feature and catch runaway spend before it shows up on a bill.
>
> ## Description
>
> Add Helicone as a transparent proxy in front of OpenAI. The existing `api/src/services/openai-moderation.service.ts` and any future LLM caller imports a small `getOpenAIClient()` wrapper that points `baseURL` at Helicone with the org's API key. This is one config change, no business-logic refactor.
>
> ## Requirements
>
> 1. Create `api/src/lib/openai-client.ts` exporting `getOpenAIClient()` that returns an OpenAI client configured with `baseURL: https://oai.helicone.ai/v1` and the Helicone auth header set from `HELICONE_API_KEY`.
> 2. Refactor every OpenAI import in `api/src/` to use the new wrapper; verify with `rg "from 'openai'"` returning hits only in `openai-client.ts`.
> 3. Tag each LLM call with a `Helicone-Property-Feature` header (e.g., `moderation`, `support-triage`, `event-tagging`) so cost can be sliced per feature in the dashboard.
> 4. Add `HELICONE_API_KEY` to the secret manager (dev) and the host secrets (staging + prod); document in `docs/guides/AI_PLATFORM_GUIDE.md`.
>
> ## Acceptance Criteria
>
> 1. **Validates R1 + R2**: A test call from `api/` shows up in the Helicone dashboard within 10s with model, tokens, and cost; `rg "from 'openai'"` outside `openai-client.ts` returns zero hits.
> 2. **Validates R3**: Helicone dashboard "Properties" view groups calls by feature and shows distinct cost per feature.
> 3. **Validates R4**: The secret manager returns the key in dev; host secrets list shows it in staging and prod; the guide doc references it.
> 4. **Validates all**: A 24h soak in staging shows zero "fallback to direct OpenAI" log lines (i.e., the proxy stays healthy).

**What to imitate:**
- Header lines (`**Epic:**`, `**Title:**`) repeat the parent link and title before the User Story.
- Description names the file path being touched and ends with a simplifying constraint ("This is one config change, no business-logic refactor.").
- Each Requirement is one concrete grep-able action.
- Each AC explicitly cites which Requirements it validates; the final AC is a soak/integration check.

---

## Example 3 — Hardening (PROJ-64)

**Title:** `Harden openai-moderation.service.ts: fail-open, input validation, log leaks`

**Labels:** `compliance`, `api`
**Priority:** High (status: Backlog)

**Body:**

> ## Summary
>
> Four vulnerabilities in `api/src/services/openai-moderation.service.ts` found during the Helicone proxy work (`PROJ-19`). None are currently exploitable at scale (moderation is only called from internal service code, not directly from user input), but they become real bugs as moderation is wired into more surfaces.
>
> ## Issues
>
> ### 1\. Fail-open on API errors (lines 42-45, 73-76, 111-113)
>
> Every `catch` block returns `createSafeResult()`, meaning if OpenAI's API is down, rate-limited, or the key is revoked, all content silently bypasses moderation. An attacker who can trigger API failures (e.g. by exhausting the rate limit) gets a free pass.
>
> **Fix:** Return a blocked-by-default result on API failure, or queue the content for retry rather than allowing it through.
>
> ### 2\. No URL validation on imageUrl (lines 52, 94)
>
> `moderateImage` and `moderateContent` pass the URL straight to OpenAI with zero validation. No scheme check (`file://`, `ftp://`), no blocklist for internal IPs. While OpenAI's servers do the fetch (not ours), this still leaks arbitrary URLs to a third party.
>
> **Fix:** Validate scheme is `https://` before sending to OpenAI. This does not affect photo uploads from mobile. By the time `moderateImage` is called, the image has already been uploaded to storage and the URL is an HTTPS storage URL. Raw device paths never reach this service.
>
> ### 3\. No input size limit on text
>
> The only guard is `text.trim().length < 3` (line 29). There is no upper bound. A multi-MB string will not cost money (moderation is free), but it can cause timeouts, which triggers the fail-open path above.
>
> **Fix:** Cap input at a reasonable length (e.g. 100KB). Reject or truncate above that.
>
> ### 4\. Error objects may leak content to logs (lines 42, 73, 111)
>
> `console.error('...', error)` can serialize the full Axios/fetch error, which may include the request body (the user's text or image URL). Sensitive or harmful content submitted for moderation ends up in plaintext logs.
>
> **Fix:** Log only `error.message` and `error.status`, not the full error object.

**What to imitate:**
- Summary calibrates severity honestly (not exploitable at scale today, but becomes one as scope grows).
- Each numbered issue includes line numbers in the header.
- Each issue is 2–4 sentences of plain-language explanation, then a `**Fix:**` line.
- The `**Fix:**` line is one or two sentences, not a paragraph.
