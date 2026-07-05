#!/usr/bin/env python3
"""Tests for validate_issue.py. Good drafts must pass; planted violations must
be caught by the right rule code. Run: python3 test_validate.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from validate_issue import validate_text  # noqa: E402

GOOD_STORY = """**Epic:** AI Foundation / Platform infra
**Title:** Add Helicone proxy for all OpenAI calls with cost + latency dashboard
**Anchor:** api/src/lib/openai-client.ts:getOpenAIClient
**Labels:** `api`, `ai`
**Priority:** No priority

## User Story

As an operator, I want every LLM call routed through an observability gateway, so that I can see real-time cost, latency, and error rates per feature.

## Problem

Today every OpenAI call in `api/src/` imports the raw `openai` SDK and hits the API directly. There is no per-feature cost slice and no shared place to enforce retry policy.

## Solution

Add Helicone as a transparent proxy in front of OpenAI. The existing caller imports a small `getOpenAIClient()` wrapper. This is one config change, no business-logic refactor.

## Out of scope

* The moderation service's own retry policy; that stays as-is.

## Requirements

1. Create `api/src/lib/openai-client.ts` exporting `getOpenAIClient()` configured with `baseURL: https://oai.helicone.ai/v1`.
2. Refactor every OpenAI import in `api/src/` to use the wrapper; verify with `rg "from 'openai'"`.

## Evaluation

1. **Validates R1**: A test call from `api/` shows up in the Helicone dashboard within 10s.
2. **Validates all**: `pytest api/tests/test_openai_client.py` passes and `rg "from 'openai'"` outside the wrapper returns zero hits.
"""

# A story with no parent epic (a standalone refactor). The **Epic:** none
# sentinel is deliberate; it must not error.
STANDALONE_STORY = """**Epic:** none
**Title:** Refactor the pricing module in the api service
**Anchor:** api/src/pricing.ts:computePrice
**Labels:** `api`, `tech-debt`

## User Story

As a developer, I want the pricing module split by concern, so that changes stay local.

## Problem

Today `api/src/pricing.ts` mixes tax, discount, and rounding in one function.

## Solution

Split into three pure helpers behind the same signature. No behavior change.

## Out of scope

* New pricing rules; this is a structure-only refactor.

## Requirements

1. Extract `applyTax`, `applyDiscount`, `roundPrice` from `computePrice`.

## Evaluation

1. **Validates R1**: `pytest api/tests/test_pricing.py` passes with identical outputs.
"""

# A lightweight Bug/Chore/Spike. Type header selects the minimal shape: no
# persona, no requirement->evaluation mapping, but an Anchor and a runnable
# Verification are still required.
GOOD_TASK = """**Type:** Bug
**Title:** Fix drag reset on pointerup in the 3D graph
**Anchor:** web/components/graph-3d.tsx:657
**Labels:** `web`, `ui-ux`
**Priority:** Medium

## Problem

`dragPinned` is set true on pointerdown but reset to false on pointerup (graph-3d.tsx:657), so a pinned node snaps back.

## Verification

`npx playwright test drag-pin` shows the node stays pinned after release.
"""

# Fenced code carrying a drift heading, an AI-tell word, and an em-dash. All of
# it is quoted source, so none of it may fire.
FENCE_NOISE = """**Epic:** Platform
**Title:** Stand up the notifications service in the api
**Anchor:** api/src/notify.ts:send
**Labels:** `api`, `tech-debt`

## User Story

As a user, I want notifications, so that I stay informed.

## Problem

Today there is no notifications service in `api/`.

## Solution

Build a small `send()` module. One file.

## Out of scope

* Delivery retries.

## Requirements

1. Create `api/src/notify.ts` exporting `send()`.

```md
## Description
This robust, comprehensive layer — with an em-dash — is the OLD template.
```

## Evaluation

1. **Validates R1**: `pytest -k notify` passes.
"""

# A single story split by a mid-body `---`. The Requirements and Evaluation
# after the rule must stay in the same block, not be dropped from validation.
TAILDROP_STORY = """**Epic:** Platform
**Title:** Wire structured logging into the api service
**Anchor:** api/src/log.ts:logger
**Labels:** `api`, `tech-debt`

## User Story

As an operator, I want JSON logs, so that I can query them.

## Problem

Today `api/` logs unstructured text to stdout.

## Solution

Add a pino logger. One module, no behavior change.

## Out of scope

* Log rotation.

---

## Requirements

1. Add `api/src/log.ts` exporting a configured pino instance.

## Evaluation

1. **Validates R1**: `pytest -k logging` shows JSON on stdout.
"""

# "Improve auth (blocks PROJ-19)": the digit 19 must not launder the vague verb.
VAGUE_WITH_ID = """**Epic:** Platform
**Title:** Improve the login throttle on the api
**Anchor:** api/src/login.ts:throttle
**Labels:** `api`, `compliance`

## User Story

As a user, I want protection, so that my account is safe.

## Problem

Improve auth (blocks PROJ-19) is the only note today.

## Solution

Add a limiter. One middleware.

## Out of scope

* Captcha.

## Requirements

1. Add `rateLimit()`.

## Evaluation

1. **Validates R1**: 100 rapid `POST /login` return 429.
"""

# "Optimize ... p95 < 200ms": the metric is adjacent, so no vague-verb error.
GOOD_OPTIMIZE = """**Epic:** Platform
**Title:** Add an LRU cache to the search endpoint
**Anchor:** api/src/search.ts:handleSearch
**Labels:** `api`, `tech-debt`

## User Story

As a user, I want fast search, so that results feel instant.

## Problem

Today `/search` recomputes on every call.

## Solution

Optimize `/search` to p95 < 200ms on a 10k-event corpus with an LRU cache. One module.

## Out of scope

* Query-syntax changes.

## Requirements

1. Add an LRU cache to `handleSearch`.

## Evaluation

1. **Validates R1**: `pytest -k search_latency` asserts p95 < 200ms.
"""

# Noun compounds ("self-improvement", "evaluator-optimizer", "optimizer") are
# terms of art, not vague action verbs, and must NOT fire vague-verb.
NOUN_COMPOUND = """**Epic:** none
**Title:** Wire the self-improvement loop into the evaluator-optimizer
**Anchor:** app/loop.py:run_optimizer
**Labels:** `ai`, `infra`

## User Story

As an operator, I want the gated self-improvement loop wired in, so that the optimizer proposes changes safely.

## Problem

Today `app/loop.py` runs the evaluator-optimizer pattern but the self-improvement loop is ungated; the optimizer writes with no review.

## Solution

Gate the optimizer behind the reviewer. One module.

## Out of scope

* Unattended self-improvement; the gate stays.

## Requirements

1. Add a review gate to `run_optimizer` in `app/loop.py`.

## Evaluation

1. **Validates R1**: `pytest -k optimizer_gate` asserts the optimizer blocks on a failing review.
"""

# A prose Anchor must be flagged (WARN) as not addressable.
ANCHOR_PROSE = """**Epic:** Platform
**Title:** Wire the rate limiter into the login route
**Anchor:** the whole auth flow
**Labels:** `api`, `compliance`

## User Story

As a user, I want brute-force protection, so that my account is safe.

## Problem

Today the login route has no throttle.

## Solution

Add a per-IP limiter. One middleware.

## Out of scope

* Captcha.

## Requirements

1. Add `rateLimit()` to the login route.

## Evaluation

1. **Validates R1**: 100 rapid `POST /login` return 429.
"""

GOOD_EPIC = """**Title:** Epic: SEO & Discoverability
**Labels:** `epic`, `web`, `seo`
**Priority:** No priority

## Goal

Today the public web app is invisible to search engines: there is no `robots.ts`, no `sitemap.ts`, no `metadataBase`, and no canonical URLs. For an events platform this is the single highest-leverage gap.

## Outcomes

* The site has a valid `robots.txt` and `sitemap.xml` covering events and marketing routes.
* Every page has a canonical URL; filterable surfaces do not create duplicate-content problems.

## Out of scope

* Indexing of authenticated routes (those should be `noindex`).

## Stories under this epic

* Story 1: SEO foundations: robots.ts, sitemap.ts, metadataBase, canonicals
* Story 2: Schema.org Event JSON-LD on event detail pages
* Story 3: Dynamic OG image generation per event
"""

GOOD_HARDENING = """**Title:** Harden openai-moderation.service.ts: fail-open, input validation, log leaks
**Labels:** `compliance`, `api`
**Priority:** High

## Summary

Four vulnerabilities in `api/src/services/openai-moderation.service.ts`. None are currently exploitable at scale, but they become real bugs as moderation is wired into more surfaces.

## Issues

### 1\\. Fail-open on API errors (lines 42-45)

Every `catch` block returns a safe result, so if OpenAI is down all content silently bypasses moderation.

**Fix:** Return a blocked-by-default result on API failure.

### 2\\. No URL validation on imageUrl (lines 52, 94)

The URL is passed straight to OpenAI with no scheme check.

**Fix:** Validate scheme is `https://` before sending.
"""

GOOD_BUNDLED = """**Epic:** AI Foundation
**Title:** AI rollout safety: prompt evals + feature flags
**Labels:** `api`, `ai`, `tech-debt`
**Priority:** High

## User Story

As an engineer, I want evals and feature flags, so that I can ship AI changes safely and roll back without a deploy.

## Problem

Two related primitives are missing from the AI platform today. Without evals, every prompt change is a guess; without flags, every rollout is all-or-nothing.

### Concept 1: Eval framework

**Problem:** When you change a prompt, you cannot tell if quality moved.

**Solution:** A fixed test suite that scores every prompt change before it ships.

### Concept 2: Postgres feature flags

**Problem:** Killing a bad feature needs a deploy today.

**Solution:** A `feature_flags` table checked at call time; flip a row to disable.

### Why bundled

Both wrap every future AI story; splitting risks shipping one without the other.

## Requirements

1. Initialize the eval config in `api/evals/` with baseline cases.
2. Add a `feature_flags` table and an `isEnabled(key, ctx)` helper.

## Evaluation

1. **Validates R1**: the eval suite runs in CI and fails the PR on regression.
2. **Validates all**: a flag flip disables the feature in prod with no deploy.
"""

BAD_EM_DASH = """**Epic:** Platform
**Title:** Wire rate limiter into the login route
**Labels:** `api`, `compliance`

## User Story

As a user, I want protection against brute force, so that my account stays safe.

## Problem

Today the login route has no throttle — an attacker can submit unlimited guesses.

## Solution

Add a per-IP limiter. This is one middleware, no business-logic change.

## Requirements

1. Add `rateLimit()` middleware to the login route.

## Evaluation

1. **Validates R1**: 100 rapid logins return 429.
"""

BAD_VAGUE = """**Epic:** Platform
**Title:** Improve search performance
**Labels:** `api`, `tech-debt`

## User Story

As a user, I want faster search, so that results feel instant.

## Problem

Today `/search` is slow.

## Solution

We will improve the query path and optimize the index.

## Requirements

1. Add an index.

## Evaluation

1. **Validates R1**: search is faster.
"""

BAD_DRIFT = """**Epic:** Platform
**Title:** Add caching to the search endpoint
**Labels:** `api`, `tech-debt`

## User Story

As a user, I want fast search, so that it feels instant.

## Description

Today there is no cache and we should build one.

## Requirements

1. Add an LRU cache.

## Acceptance Criteria

1. Cache hit rate above 80 percent.
"""

BAD_FIX = """**Title:** Harden auth.ts: rate limit, token log, email validation
**Labels:** `api`, `compliance`
**Priority:** High

## Summary

Three defects in `api/auth.ts`.

## Issues

### 1\\. No rate limit on login (lines 10-20)

The login route has no throttle.

### 2\\. Raw token logged (line 88)

The JWT is logged in plaintext.

**Fix:** Remove the token from the log call.
"""

BAD_AI_TELL = """**Epic:** Platform
**Title:** Stand up the notifications service in api/
**Labels:** `api`, `ai`

## User Story

As a user, I want notifications, so that I stay informed.

## Problem

Today there is no notifications service in `api/`.

## Solution

This comprehensive, production-ready service provides robust handling of all edge cases.

## Requirements

1. Create `api/src/notifications.ts`.

## Evaluation

1. **Validates R1**: a test notification is delivered.
"""

BAD_EPIC_COUNT = """**Title:** Epic: Mobile App
**Labels:** `epic`, `mobile`

## Goal

Today Deepwatch has no mobile app and no `mobile/` codebase.

## Outcomes

* A user can sign in on a phone.

## Out of scope

* In-app purchases.

## Stories under this epic

* Story 1: Stand up the Expo app
"""

BAD_EVAL_MAPPING = """**Epic:** Platform
**Title:** Wire structured logging into api/
**Labels:** `api`, `tech-debt`

## User Story

As an operator, I want JSON logs, so that I can query them.

## Problem

Today `api/` logs unstructured text to stdout.

## Solution

Add a pino logger. This is one module, no behavior change.

## Requirements

1. Add `api/src/log.ts` exporting a configured pino instance.

## Evaluation

1. Logs are now JSON.
"""


def errors(text):
    v, _ = validate_text(text)
    return [x for x in v if x.level == "ERROR"]


def codes(text):
    return {x.code for x in errors(text)}


def warn_codes(text):
    v, _ = validate_text(text)
    return {x.code for x in v if x.level == "WARN"}


def n_blocks(text):
    _, n = validate_text(text)
    return n


def main():
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"  FAIL: {name}")

    # Good drafts: zero errors.
    for name, txt in [("good_story", GOOD_STORY), ("good_epic", GOOD_EPIC),
                      ("good_hardening", GOOD_HARDENING), ("good_bundled", GOOD_BUNDLED)]:
        errs = errors(txt)
        check(f"{name} has no errors", not errs)
        if errs:
            for e in errs:
                print(f"      unexpected: L{e.line} [{e.code}] {e.message}")

    # Bad drafts: the right rule fires.
    check("bad_em_dash flags em-dash", "em-dash" in codes(BAD_EM_DASH))
    check("bad_vague flags vague-verb", "vague-verb" in codes(BAD_VAGUE))
    check("bad_drift flags section-drift", "section-drift" in codes(BAD_DRIFT))
    check("bad_fix flags fix-missing", "fix-missing" in codes(BAD_FIX))
    check("bad_ai_tell flags ai-tell", "ai-tell" in codes(BAD_AI_TELL))
    check("bad_epic_count flags epic-story-count", "epic-story-count" in codes(BAD_EPIC_COUNT))
    check("bad_eval_mapping flags eval-mapping", "eval-mapping" in codes(BAD_EVAL_MAPPING))

    # New good drafts: zero errors.
    for name, txt in [("standalone_story", STANDALONE_STORY), ("good_task", GOOD_TASK),
                      ("fence_noise", FENCE_NOISE), ("taildrop_story", TAILDROP_STORY),
                      ("good_optimize", GOOD_OPTIMIZE)]:
        errs = errors(txt)
        check(f"{name} has no errors", not errs)
        if errs:
            for e in errs:
                print(f"      unexpected: L{e.line} [{e.code}] {e.message}")

    # Standalone story: epic-backlink is a WARN, never an ERROR.
    check("standalone_story does not error on epic-backlink",
          "epic-backlink" not in codes(STANDALONE_STORY))

    # Fence blindness: a drift heading / AI-tell / em-dash inside a code fence
    # is quoted source and must not fire.
    fence_codes = codes(FENCE_NOISE)
    check("fence_noise ignores fenced section-drift", "section-drift" not in fence_codes)
    check("fence_noise ignores fenced ai-tell", "ai-tell" not in fence_codes)
    check("fence_noise ignores fenced em-dash", "em-dash" not in fence_codes)

    # Mid-body `---` must not split a single issue; the tail stays validated.
    check("taildrop_story is one block", n_blocks(TAILDROP_STORY) == 1)
    check("taildrop_story keeps its tail sections",
          "section-missing" not in codes(TAILDROP_STORY))

    # METRIC false-negative: a bare issue id must not launder a vague verb.
    check("vague_with_id still flags vague-verb", "vague-verb" in codes(VAGUE_WITH_ID))
    check("good_optimize accepts an adjacent metric", "vague-verb" not in codes(GOOD_OPTIMIZE))

    # Noun compounds are terms of art, not vague action verbs.
    check("noun_compound does not flag vague-verb", "vague-verb" not in codes(NOUN_COMPOUND))
    check("noun_compound has no errors", not errors(NOUN_COMPOUND))

    # Anchor: prose warns, a good-shaped anchor does not.
    check("anchor_prose warns anchor-shape", "anchor-shape" in warn_codes(ANCHOR_PROSE))
    check("good_story has a clean anchor", "anchor-shape" not in warn_codes(GOOD_STORY))
    check("good_story does not warn anchor-missing", "anchor-missing" not in warn_codes(GOOD_STORY))

    # The undischargeable labels-verify WARN is gone.
    check("labels-verify WARN retired", "labels-verify" not in warn_codes(GOOD_STORY))

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
