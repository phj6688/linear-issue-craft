#!/usr/bin/env python3
"""Tests for validate_issue.py. Good drafts must pass; planted violations must
be caught by the right rule code. Run: python3 test_validate.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from validate_issue import validate_text  # noqa: E402

GOOD_STORY = """**Epic:** AI Foundation / Platform infra
**Title:** Add Helicone proxy for all OpenAI calls with cost + latency dashboard
**Labels:** `api`, `ai`
**Priority:** No priority

## User Story

As an operator, I want every LLM call routed through an observability gateway, so that I can see real-time cost, latency, and error rates per feature.

## Problem

Today every OpenAI call in `api/src/` imports the raw `openai` SDK and hits the API directly. There is no per-feature cost slice and no shared place to enforce retry policy.

## Solution

Add Helicone as a transparent proxy in front of OpenAI. The existing caller imports a small `getOpenAIClient()` wrapper. This is one config change, no business-logic refactor.

## Requirements

1. Create `api/src/lib/openai-client.ts` exporting `getOpenAIClient()` configured with `baseURL: https://oai.helicone.ai/v1`.
2. Refactor every OpenAI import in `api/src/` to use the wrapper; verify with `rg "from 'openai'"`.

## Evaluation

1. **Validates R1**: A test call from `api/` shows up in the Helicone dashboard within 10s.
2. **Validates all**: A 24h soak in staging shows zero fallback log lines.
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
                      ("good_hardening", GOOD_HARDENING)]:
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

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
