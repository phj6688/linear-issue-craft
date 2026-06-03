# Labels and priority

Labels and priority are *categorical*, not ad-hoc. Apply the rules below mechanically.

## Label layering rule

Every issue gets at least two labels: **one domain** + **one or more capabilities**. Never use ownership or urgency labels.

### Domain labels (pick exactly one)

Use whatever domain split matches your codebase. A typical monorepo split:

- `api`: anything in `api/`. Backend, services, ORM, jobs, integrations.
- `web`: anything in `web/`. Web app, marketing pages, headers, SEO.
- `mobile`: anything in `mobile/`. React Native / iOS / Android client.

If your project has a different split (e.g., `frontend` / `backend` / `infra`, or per-service labels), use that, but pick **one taxonomy and stick to it**. Mixing schemas fragments the labels.

A cross-cutting initiative (e.g., a new auth design that affects all three) is an **epic**, and its children are split per-domain.

### Capability labels (pick one or more)

| Label | When to use |
|---|---|
| `epic` | Always present on Epic-archetype issues. |
| `ai` | Touches LLMs, embeddings, moderation, observability proxies, eval frameworks, AI features. |
| `seo` | robots / sitemap / metadata / structured data / OG / canonical URLs. |
| `compliance` | GDPR, ePrivacy, security headers, audit logs, data residency, content moderation. |
| `tech-debt` | Code that works but is fragile, duplicated, or blocks future work. No new user-visible behavior. |
| `ui-ux` | User-visible interaction or visual changes (styling, animation, accessibility). |

### Rules

- A domain label is **required**. Issues without one are rejected.
- `epic` is required iff the archetype is Epic.
- `ai`, `seo`, `compliance`, `ui-ux` are not mutually exclusive: apply all that fit.
- `tech-debt` and `ui-ux` are also not exclusive (e.g., a refactor of a poorly built UI may carry both).
- Do **not** use labels for: team ownership, sprint, severity ("urgent"), or status ("blocked").

### Real label sets

| Issue title | Labels |
|---|---|
| `Epic: SEO & Discoverability` | `epic`, `web`, `seo` |
| `Epic: Security & Compliance` | `epic`, `web`, `compliance` |
| `Epic: AI Foundation / Platform infra` | `epic`, `api`, `ai` |
| `Stand up Trigger.dev v3 in api/` | `api`, `ai` |
| `Add Helicone proxy …` | `api`, `ai` |
| `Hardened security headers …` | `web`, `compliance` |
| `Harden openai-moderation.service.ts …` | `compliance`, `api` |

## Priority: category-driven, not urgency-driven

Priority maps to **what kind of work** this is, not "how badly do I want it now." Within a category, recency in the backlog handles ordering.

| Priority | Category |
|---|---|
| **Urgent** | Active production incident. Use sparingly and only with a paging link. |
| **High** | Security work · compliance work · core infrastructure (job queue, observability, auth) · all epics. |
| **Medium** | User-visible features that are part of the roadmap but not blocking compliance/security. |
| **Low** | Decision-support / exploratory features, nice-to-have UI polish, research spikes. |
| **No priority** | Already shipped (Done state), or scoped-out / parked. |

### Real priority assignments

| Issue title | Priority | Why |
|---|---|---|
| `Epic: Security & Compliance` | High | Compliance epic blocks regulated traffic. |
| `Hardened security headers …` | High | Security baseline. |
| `GDPR cookie consent banner …` | High | Compliance gating EU traffic. |
| `Epic: AI Foundation …` | High | Core infra epic. |
| `Harden openai-moderation.service.ts …` | High | Security hardening. |
| `Build guest landing page at /` | Medium | User-facing feature. |
| `Venue — Demand forecasting + dynamic pricing` | Medium | High-leverage feature, but exploratory enough to not be High. |
| `Core Web Vitals audit + fix pass` | Low | Quality polish, no compliance gate. |
| `Artist — Per-show performance analytics …` | Low | Decision-support / exploratory. |
| `Epic: SEO & Discoverability` (Done) | No priority | Completed work. |

## Anti-patterns

- ❌ Tagging every active task as "Urgent" because it's currently being worked.
- ❌ Tagging exploratory or polish work as "High" because it feels important.
- ❌ Using a label like `frontend` or `backend` when the workspace uses project-based domains: use the project label instead.
- ❌ Using a label like `sprint-1` or `q3-2026`: Linear cycles handle this.
- ❌ Inventing new domain labels (`infra`, `data`, etc.) mid-stream: pick a taxonomy and stick to it, or have an explicit migration.
