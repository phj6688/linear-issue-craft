#!/usr/bin/env python3
"""Validate a linear-issue-craft draft against the mechanical house-style rules.

This is the hard gate the skill runs on every draft before showing it to the
user (and, once welded, the gate a save-hook runs before every create). It
checks only the rules a script can verify deterministically: em-dash in prose,
vague verbs without an adjacent metric, AI tells, section order, Fix lines,
Anchor shape, label shape, and so on. Judgment calls (is the persona real? is
the scope one PR? does the named Anchor actually exist in the repo?) stay with
the agent and the pipeline, which can see the repo.

Usage:
    python3 validate_issue.py draft.md          # validate a file
    cat draft.md | python3 validate_issue.py    # validate stdin

A draft may contain multiple issues (an epic plus its child stories) separated
by lines that are exactly `---`; each block carrying a `**Title:**` line is
validated on its own. A `---` inside a fenced code block, or one that only
splits body prose (the following text carries no new `**Title:**`), is treated
as content, not a separator, so it can never silently drop the tail of an issue
from validation.

Exit code 0 when there are no ERRORs, 1 otherwise. WARNs never fail the gate.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass

EM_DASH = "—"  # banned in prose; en-dash is tolerated in numeric ranges and not checked

# Lines that may legitimately carry an em-dash: role-prefixed titles and the
# header fields that echo a (possibly role-prefixed) title. The house style
# puts the colon inside the bold markers (`**Title:**`), so tolerate both.
TITLE_FIELD = re.compile(r"^\s*\*\*\s*(Title|Parent|Epic|Type|Anchor)\s*:?\s*\*\*", re.IGNORECASE)

# A bullet under "Stories under this epic" lists a child story title verbatim; a
# role-prefixed child (`Venue — Demand forecasting`) legitimately carries the
# em-dash the title pattern mandates, so those lines are exempt from the em-dash
# scan too.
STORY_BULLET = re.compile(r"^\s*([-*]|\d+\.)\s+\S")

# Vague ACTION verbs only, not their noun forms. "self-improvement", "optimizer",
# and "evaluator-optimizer" are terms of art, not vague actions, and must not fire
# (the old `improv\w*|optimiz\w*` matched the nouns and blocked real issues).
VAGUE_VERBS = re.compile(
    r"\b(improve|improves|improving|enhance|enhances|enhancing"
    r"|optimi[sz]e|optimi[sz]es|optimi[sz]ing)\b",
    re.IGNORECASE,
)
# A real target metric: a percentage, a pNN latency marker, a comparison bound,
# or a number bound to a unit. A bare integer (a version, issue id, port, or
# line number) is NOT a metric, so "Improve auth (blocks PROJ-19)" no longer
# slips through on the 19.
METRIC = re.compile(
    r"(\bp\d{2,3}\b"
    r"|\d+\s?%"
    r"|[<>]=?\s?\d"
    r"|\b\d+(\.\d+)?\s?(ms|s|sec|secs|seconds?|m|min|mins|minutes?|h|hours?"
    r"|kb|mb|gb|rps|qps|x)\b)",
    re.IGNORECASE,
)

# AI tells: the skill's anti-patterns plus the operator's globally banned words.
# Matched on word boundaries against code-stripped prose so that identifiers
# (`robust-parser.ts`, `optimizePackageImports`) and quoted source do not trip.
AI_TELLS = [
    "generated with claude", "co-authored-by", "delve", "it's worth noting",
    "it is worth noting", "in conclusion", "navigate the landscape",
    "comprehensive", "robust", "seamless", "gracefully", "straightforward",
    "leverages", "leveraging", "this ensures", "for clarity", "this is critical",
    "thoughtful", "production-ready", "elegant",
]
AI_TELL_RES = [(t, re.compile(r"(?<!\w)" + re.escape(t) + r"(?!\w)", re.IGNORECASE))
               for t in AI_TELLS]

PRIORITIES = {"urgent", "high", "medium", "low", "no priority"}

# The Anchor is the one new authoring primitive: a named, addressable thing the
# held-out probe can target. Accept exactly the shapes a machine can resolve;
# reject prose ("the auth flow"). Comma-separated anchors are allowed; each part
# must match one shape.
ANCHOR_RE = re.compile(
    r"""^(
        [\w./\-]+\.\w+:\d+                                   # file.ext:line
      | [\w./\-]+\.\w+:[A-Za-z_]\w*                          # file.ext:symbol
      | [A-Za-z_]\w*(\.[A-Za-z_]\w*){2,}                     # dotted.module.function (>=3 segments)
      | (GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+/\S*\s*(->|→|returns?)\s*\d{3}  # METHOD /path -> status
      | playwright:\S.*                                      # playwright:selector
    )$""",
    re.VERBOSE | re.IGNORECASE,
)

# A last-line acceptance check should be runnable headless. Flag the closer when
# it leans on something no headless stage can observe (soak, dashboard, staging
# credentials) AND carries no runnable token.
UNOBSERVABLE = re.compile(
    r"\b(soak|staging|dashboard|overnight|24\s?-?\s?h(our)?s?|prod(uction)?\b[^.]*\bcredential)",
    re.IGNORECASE,
)
RUNNABLE = re.compile(
    r"(`[^`]+`|\bcurl\b|\bpytest\b|\bnpx?\b|\bnpm\b|\bpnpm\b|\bplaywright\b|\brg\b|\bmake\b"
    r"|\b(GET|POST|PUT|PATCH|DELETE)\b|https?://|\bexit\s?code\b|\breturns?\s+\d)",
    re.IGNORECASE,
)

ARCHETYPE_SECTIONS = {
    "epic": ["Goal", "Outcomes", "Out of scope", "Stories under this epic"],
    "story": ["User Story", "Problem", "Solution", "Requirements", "Evaluation"],
    "hardening": ["Summary", "Issues"],
    # Lightweight shape for bugs, chores, spikes, ops tasks. The full story
    # ceremony (persona, requirement->evaluation mapping) is optional here; the
    # minimum contract (Anchor + a runnable Verification) still applies.
    "task": ["Problem", "Verification"],
}
# Headings that signal the old/simple template drifted back in.
DRIFT_HEADINGS = {"Description", "Acceptance Criteria"}

HEADING_RE = re.compile(r"^(#{2,3})\s+(.*\S)\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


@dataclass
class Violation:
    level: str   # "ERROR" or "WARN"
    line: int    # 1-based line in the original text, 0 if not line-specific
    code: str
    message: str


@dataclass
class Block:
    title: str
    labels: list
    priority: str
    archetype: str
    start_line: int
    lines: list            # (abs_line_no, text)
    headings: list         # (abs_line_no, heading_text) for H2/H3 outside fences
    fenced: set            # abs line numbers inside fenced code
    story_bullets: set     # abs line numbers of child-story list bullets


def strip_inline_code(s):
    """Blank out `inline code` spans so identifiers and quoted source do not
    trip the prose scanners."""
    return re.sub(r"`[^`]*`", "  ", s)


def fenced_line_numbers(raw_lines, offset=0):
    """Return the set of 1-based line numbers (offset + index) that sit inside a
    fenced code block, fence markers included."""
    fenced, in_fence = set(), False
    for i, ln in enumerate(raw_lines):
        n = offset + i + 1
        if FENCE_RE.match(ln):
            fenced.add(n)
            in_fence = not in_fence
            continue
        if in_fence:
            fenced.add(n)
    return fenced


def split_blocks(text):
    """Split the draft into issue blocks on `---` separators, fence-aware.

    A `---` inside a fenced block is content. A `---` that splits off a tail
    carrying no new `**Title:**` is a thematic break, so the tail is merged back
    into the issue it belongs to instead of being silently dropped."""
    raw = text.splitlines()
    fenced = fenced_line_numbers(raw)
    # Cut into segments on bare `---` lines that are not inside a fence.
    segments, cur, cur_start = [], [], 1
    for i, ln in enumerate(raw):
        n = i + 1
        if ln.strip() == "---" and n not in fenced:
            segments.append((cur_start, cur))
            cur, cur_start = [], n + 1
        else:
            cur.append((n, ln))
    segments.append((cur_start, cur))
    # A segment with a Title starts a block; a title-less segment (a mid-body
    # `---`, or trailing prose) attaches to the block before it. A title-less
    # leading segment (preamble before the first issue) is dropped.
    blocks = []
    for start, seg in segments:
        has_title = any("**Title:**" in t for _, t in seg)
        if has_title:
            blocks.append([start, list(seg)])
        elif blocks:
            blocks[-1][1].extend(seg)
    return [(start, blk) for start, blk in blocks
            if any("**Title:**" in t for _, t in blk)]


def field(lines, name):
    pat = re.compile(r"^\s*\*\*\s*%s\s*:?\s*\*\*\s*:?\s*(.+?)\s*$" % re.escape(name), re.IGNORECASE)
    for _, ln in lines:
        m = pat.match(ln)
        if m:
            return m.group(1).strip()
    return ""


def parse_labels(raw):
    return [t.strip().strip("`").strip() for t in raw.split(",") if t.strip()]


def strip_code(s):
    return s.replace("`", "").strip()


def detect_archetype(title, heading_names, type_field):
    t = strip_code(title).lower()
    ty = strip_code(type_field).lower()
    if ty in ("bug", "chore", "spike", "task", "ops") or re.match(r"^(bug|chore|spike|ops)\b\s*[:\-]", t):
        return "task"
    if t.startswith("epic:") or ("Goal" in heading_names and "Stories under this epic" in heading_names):
        return "epic"
    if t.startswith("harden") or ("Summary" in heading_names and "Issues" in heading_names):
        return "hardening"
    return "story"


def make_block(start_line, lines):
    abs_nos = [n for n, _ in lines]
    lo = min(abs_nos) if abs_nos else start_line
    raw = [ln for _, ln in lines]
    fenced = fenced_line_numbers(raw, offset=lo - 1)
    headings = [(n, m.group(2).strip())
                for n, ln in lines
                for m in [HEADING_RE.match(ln)] if m and n not in fenced]
    heading_names = [h for _, h in headings]
    # Child-story bullets under "Stories under this epic" carry verbatim titles.
    story_bullets, in_stories = set(), False
    for n, ln in lines:
        if n in fenced:
            continue
        m = HEADING_RE.match(ln)
        if m:
            in_stories = m.group(2).strip() == "Stories under this epic"
            continue
        if in_stories and STORY_BULLET.match(ln):
            story_bullets.add(n)
    title = strip_code(field(lines, "Title"))
    archetype = detect_archetype(title, heading_names, field(lines, "Type"))
    return Block(
        title=title,
        labels=parse_labels(field(lines, "Labels")),
        priority=field(lines, "Priority"),
        archetype=archetype,
        start_line=start_line,
        lines=lines,
        headings=headings,
        fenced=fenced,
        story_bullets=story_bullets,
    )


def check_em_dash(block, out):
    for n, ln in block.lines:
        if n in block.fenced or TITLE_FIELD.match(ln) or n in block.story_bullets:
            continue
        if EM_DASH in strip_inline_code(ln):
            out.append(Violation("ERROR", n, "em-dash",
                       "Em-dash in prose. Use a colon, comma, or rewrite "
                       "(em-dash is allowed only in role-prefixed titles)."))


def check_vague_verbs(block, out):
    for n, ln in block.lines:
        if n in block.fenced:
            continue
        s = strip_inline_code(ln)
        m = VAGUE_VERBS.search(s)
        if not m:
            continue
        # The metric must sit near the verb (the next ~8 words), not anywhere on
        # the line, so an unrelated number cannot launder a vague action.
        window = " ".join(s[m.start():].split()[:9])
        if not METRIC.search(window):
            out.append(Violation("ERROR", n, "vague-verb",
                       f'Vague verb "{m.group(0)}" without an adjacent target metric. '
                       f'Name a number with a unit (p95, %, ms, count) next to it, '
                       f'or use a concrete action verb.'))


def check_ai_tells(block, out):
    for n, ln in block.lines:
        if n in block.fenced:
            continue
        s = strip_inline_code(ln)
        for tell, rex in AI_TELL_RES:
            if rex.search(s):
                out.append(Violation("ERROR", n, "ai-tell",
                           f'AI tell / banned phrase: "{tell.strip()}". Delete or rewrite.'))


def check_title(block, out):
    t = block.title
    if not t:
        out.append(Violation("ERROR", block.start_line, "title-missing",
                   "No **Title:** field found."))
        return
    if t.rstrip().endswith("."):
        out.append(Violation("ERROR", block.start_line, "title-period",
                   "Title must not end with a period."))
    words = len(t.split())
    if words < 4 or words > 16:
        out.append(Violation("WARN", block.start_line, "title-length",
                   f"Title is {words} words; aim for 6-14 (longer usually means bundling)."))
    if block.archetype == "hardening" and not re.match(r"^Harden(ed)?\b", t, re.IGNORECASE):
        out.append(Violation("WARN", block.start_line, "title-harden",
                   'Hardening title should start with "Harden <stem>: <symptoms>".'))


def check_sections(block, out):
    expected = list(ARCHETYPE_SECTIONS[block.archetype])
    present = [h for _, h in block.headings]
    # Bundled-concept story variant: ### Concept blocks carry the solution, so
    # the ## Solution H2 is replaced by them and is not separately required.
    if block.archetype == "story" and any(
        n not in block.fenced and re.match(r"^###\s+(Concept\b|Why bundled\b)", ln)
        for n, ln in block.lines
    ):
        expected = [s for s in expected if s != "Solution"]
    for n, h in block.headings:
        if h in DRIFT_HEADINGS:
            out.append(Violation("ERROR", n, "section-drift",
                       f'Section "{h}" is the old template. House style uses '
                       f'Problem / Solution / Evaluation.'))
    for sec in expected:
        if sec not in present:
            out.append(Violation("ERROR", block.start_line, "section-missing",
                       f'Missing required section "## {sec}" for {block.archetype}.'))
    idx = [present.index(s) for s in expected if s in present]
    if idx != sorted(idx):
        out.append(Violation("ERROR", block.start_line, "section-order",
                   f"Sections out of order. Expected: {' -> '.join(expected)}."))


def check_anchor(block, out):
    """Every story/task must point at a machine-resolvable Anchor. WARN-only in
    the skill validator (it sees a markdown draft, not a create-vs-edit call);
    the save-hook promotes this to a create-only ERROR."""
    raw = field(block.lines, "Anchor")
    if not raw:
        out.append(Violation("WARN", block.start_line, "anchor-missing",
                   "No **Anchor:** line. Name the thing a probe can target: "
                   "file.ext:line, file.ext:symbol, module.function, "
                   "METHOD /path -> status, or playwright:selector."))
        return
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    bad = [p for p in parts if not ANCHOR_RE.match(p)]
    if bad:
        out.append(Violation("WARN", block.start_line, "anchor-shape",
                   f'Anchor "{bad[0]}" is prose, not addressable. Use '
                   f'file.ext:line, file.ext:symbol, module.function, '
                   f'METHOD /path -> status, or playwright:selector.'))


def check_story(block, out):
    epic = field(block.lines, "Epic")
    if not epic:
        out.append(Violation("WARN", block.start_line, "epic-backlink",
                   "No **Epic:** backlink. Add the parent epic, or "
                   "**Epic:** none for a deliberately standalone story."))
    check_anchor(block, out)
    headings = [h for _, h in block.headings]
    if "Out of scope" not in headings and "Non-goals" not in headings:
        out.append(Violation("WARN", block.start_line, "story-non-goals",
                   "No **## Out of scope** section. Name one non-goal so the "
                   "implementer does not gold-plate past the intended scope."))
    # Evaluation items must cite a requirement; the closer must be runnable.
    in_eval, saw_item, last_item = False, False, None
    for n, ln in block.lines:
        if n in block.fenced:
            continue
        h = HEADING_RE.match(ln)
        if h:
            in_eval = h.group(2).strip() == "Evaluation"
            continue
        if in_eval and re.match(r"^\s*\d+\.\s+\S", ln):
            saw_item, last_item = True, (n, ln)
            if "Validates R" not in ln and "Validates all" not in ln:
                out.append(Violation("ERROR", n, "eval-mapping",
                           "Evaluation item must start with **Validates R<n>** "
                           "or **Validates all**."))
    if "Evaluation" in headings and not saw_item:
        out.append(Violation("WARN", block.start_line, "eval-empty",
                   "Evaluation section has no numbered items."))
    if last_item:
        n, ln = last_item
        if UNOBSERVABLE.search(ln) and not RUNNABLE.search(ln):
            out.append(Violation("WARN", n, "eval-unobservable",
                       "Final acceptance leans on a soak/dashboard/staging check "
                       "no headless stage runs. Make it a runnable command; move "
                       "the soak to a 'Post-ship follow-up' line."))


def check_task(block, out):
    check_anchor(block, out)
    in_verify, runnable = False, False
    for n, ln in block.lines:
        if n in block.fenced:
            continue
        h = HEADING_RE.match(ln)
        if h:
            in_verify = h.group(2).strip() == "Verification"
            continue
        if in_verify and RUNNABLE.search(ln):
            runnable = True
    if "Verification" in [h for _, h in block.headings] and not runnable:
        out.append(Violation("WARN", block.start_line, "verify-unrunnable",
                   "Verification has no runnable check (a command, endpoint, or "
                   "expected exit/return). A bug/chore still needs one."))


def check_epic(block, out):
    count = len(block.story_bullets)
    if not (2 <= count <= 8):
        out.append(Violation("ERROR", block.start_line, "epic-story-count",
                   f"Epic lists {count} stories; must be 2-8 named in "
                   f'"Stories under this epic".'))
    if "epic" not in [lbl.lower() for lbl in block.labels]:
        out.append(Violation("ERROR", block.start_line, "epic-label",
                   'Epic archetype must carry the `epic` label.'))


def check_hardening(block, out):
    issue_line, has_fix, n_issues = None, False, 0
    for n, ln in block.lines:
        if n in block.fenced:
            continue
        if re.match(r"^###\s+\d", ln):
            if issue_line is not None and not has_fix:
                out.append(Violation("ERROR", issue_line, "fix-missing",
                           "Hardening issue has no **Fix:** line."))
            issue_line, has_fix, n_issues = n, False, n_issues + 1
        elif issue_line is not None and ln.strip().startswith("**Fix:**"):
            has_fix = True
    if issue_line is not None and not has_fix:
        out.append(Violation("ERROR", issue_line, "fix-missing",
                   "Hardening issue has no **Fix:** line."))
    if n_issues < 2:
        out.append(Violation("WARN", block.start_line, "harden-count",
                   f"Hardening ticket has {n_issues} issue(s); 2+ expected "
                   f"(one issue is usually a story)."))


def check_labels(block, out):
    n = len(block.labels)
    if n < 2:
        out.append(Violation("ERROR", block.start_line, "labels-shape",
                   f"{n} label(s); need 1 domain + >=1 capability."))


def check_priority(block, out):
    p = block.priority.strip().lower()
    if p and p not in PRIORITIES:
        out.append(Violation("WARN", block.start_line, "priority-enum",
                   f'Priority "{block.priority}" is not one of '
                   f'Urgent / High / Medium / Low / No priority.'))


def validate_block(block):
    out = []
    check_title(block, out)
    check_em_dash(block, out)
    check_vague_verbs(block, out)
    check_ai_tells(block, out)
    check_sections(block, out)
    check_labels(block, out)
    check_priority(block, out)
    if block.archetype == "story":
        check_story(block, out)
    elif block.archetype == "epic":
        check_epic(block, out)
    elif block.archetype == "hardening":
        check_hardening(block, out)
    elif block.archetype == "task":
        check_task(block, out)
    return out


def validate_text(text):
    """Return (violations, n_blocks)."""
    blocks = split_blocks(text)
    if not blocks:
        return ([Violation("ERROR", 0, "no-issue",
                "No issue block found (need a **Title:** line).")], 0)
    all_v = []
    for start, lines in blocks:
        all_v.extend(validate_block(make_block(start, lines)))
    return (all_v, len(blocks))


def main(argv):
    if len(argv) > 1 and argv[1] not in ("-", "--"):
        with open(argv[1], encoding="utf-8") as fh:
            text = fh.read()
        src = argv[1]
    else:
        text = sys.stdin.read()
        src = "<stdin>"
    violations, n_blocks = validate_text(text)
    errors = [v for v in violations if v.level == "ERROR"]
    warns = [v for v in violations if v.level == "WARN"]
    for v in sorted(violations, key=lambda x: (x.line, x.level)):
        loc = f"L{v.line}" if v.line else "-"
        print(f"  {v.level:5} {loc:>5}  [{v.code}] {v.message}")
    print(f"\n{src}: {n_blocks} issue block(s), "
          f"{len(errors)} error(s), {len(warns)} warning(s)")
    if errors:
        print("FAIL: fix the errors above before showing the draft.")
        return 1
    print("PASS: mechanical checks clear (judgment checks still on you).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
