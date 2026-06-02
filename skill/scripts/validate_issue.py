#!/usr/bin/env python3
"""Validate a linear-issue-craft draft against the mechanical house-style rules.

This is the hard gate the skill runs on every draft before showing it to the
user. It checks only the rules a script can verify deterministically (em-dash
in prose, vague verbs, AI tells, section order, Fix lines, label shape, ...).
Judgment calls (is the persona real? is the scope one PR?) stay with the agent.

Usage:
    python3 validate_issue.py draft.md          # validate a file
    cat draft.md | python3 validate_issue.py    # validate stdin

A draft may contain multiple issues (an epic plus its child stories) separated
by lines that are exactly `---`; each block carrying a `**Title:**` line is
validated on its own.

Exit code 0 when there are no ERRORs, 1 otherwise. WARNs never fail the gate.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass

EM_DASH = "—"  # banned in prose; en-dash (–) is tolerated in numeric ranges, so not checked

# Lines that may legitimately carry an em-dash: role-prefixed titles and the
# header fields that echo a (possibly role-prefixed) title. The house style
# puts the colon inside the bold markers (`**Title:**`), so tolerate both.
TITLE_FIELD = re.compile(r"^\s*\*\*\s*(Title|Parent|Epic|Type)\s*:?\s*\*\*", re.IGNORECASE)

VAGUE_VERBS = re.compile(r"\b(improv\w*|enhanc\w*|optimiz\w*)\b", re.IGNORECASE)
METRIC = re.compile(r"(\d|%|\bp\d{2}\b|\bms\b|\bms\.|\bseconds?\b|\bx\b)", re.IGNORECASE)

# AI tells: the skill's anti-patterns plus the operator's globally banned words.
AI_TELLS = [
    "generated with claude", "co-authored-by", "delve", "it's worth noting",
    "it is worth noting", "in conclusion", "navigate the landscape",
    "comprehensive", "robust", "seamless", "gracefully", "straightforward",
    "leverages", "leveraging", "this ensures", "for clarity", "this is critical",
    "thoughtful", "production-ready",
]

ARCHETYPE_SECTIONS = {
    "epic": ["Goal", "Outcomes", "Out of scope", "Stories under this epic"],
    "story": ["User Story", "Problem", "Solution", "Requirements", "Evaluation"],
    "hardening": ["Summary", "Issues"],
}
# Headings that signal the old/simple template drifted back in.
DRIFT_HEADINGS = {"Description", "Acceptance Criteria"}


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
    lines: list           # (abs_line_no, text)
    headings: list         # (abs_line_no, heading_text) for H2


def split_blocks(text):
    """Split the draft on `---` separators into issue blocks with a Title."""
    raw_lines = text.splitlines()
    blocks, cur, cur_start = [], [], 1
    for i, ln in enumerate(raw_lines, start=1):
        if ln.strip() == "---":
            if any("**Title:**" in x for _, x in cur):
                blocks.append((cur_start, cur))
            cur, cur_start = [], i + 1
        else:
            cur.append((i, ln))
    if any("**Title:**" in x for _, x in cur):
        blocks.append((cur_start, cur))
    return blocks


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


def detect_archetype(title, heading_names):
    t = strip_code(title).lower()
    if t.startswith("epic:") or ("Goal" in heading_names and "Stories under this epic" in heading_names):
        return "epic"
    if t.startswith("harden") or ("Summary" in heading_names and "Issues" in heading_names):
        return "hardening"
    return "story"


def make_block(start_line, lines):
    headings = [(n, m.group(1).strip())
                for n, ln in lines
                for m in [re.match(r"^##\s+(.*\S)\s*$", ln)] if m]
    heading_names = [h for _, h in headings]
    title = strip_code(field(lines, "Title"))
    archetype = detect_archetype(title, heading_names)
    return Block(
        title=title,
        labels=parse_labels(field(lines, "Labels")),
        priority=field(lines, "Priority"),
        archetype=archetype,
        start_line=start_line,
        lines=lines,
        headings=headings,
    )


def check_em_dash(block, out):
    for n, ln in block.lines:
        if EM_DASH in ln and not TITLE_FIELD.match(ln):
            out.append(Violation("ERROR", n, "em-dash",
                       "Em-dash in prose. Use a colon, comma, or rewrite "
                       "(em-dash is allowed only in role-prefixed titles)."))


def check_vague_verbs(block, out):
    for n, ln in block.lines:
        if VAGUE_VERBS.search(ln) and not METRIC.search(ln):
            verb = VAGUE_VERBS.search(ln).group(0)
            out.append(Violation("ERROR", n, "vague-verb",
                       f'Vague verb "{verb}" without a target metric. Name a '
                       f'number (p95, %, ms, count) or use a concrete action verb.'))


def check_ai_tells(block, out):
    for n, ln in block.lines:
        low = ln.lower()
        for tell in AI_TELLS:
            if tell in low:
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
    expected = ARCHETYPE_SECTIONS[block.archetype]
    present = [h for _, h in block.headings]
    # drift headings
    for n, h in block.headings:
        if h in DRIFT_HEADINGS:
            out.append(Violation("ERROR", n, "section-drift",
                       f'Section "{h}" is the old template. House style uses '
                       f'Problem / Solution / Evaluation.'))
    # required present
    for sec in expected:
        if sec not in present:
            out.append(Violation("ERROR", block.start_line, "section-missing",
                       f'Missing required section "## {sec}" for {block.archetype}.'))
    # relative order of the ones that are present
    idx = [present.index(s) for s in expected if s in present]
    if idx != sorted(idx):
        out.append(Violation("ERROR", block.start_line, "section-order",
                   f"Sections out of order. Expected: {' -> '.join(expected)}."))


def check_story(block, out):
    if not field(block.lines, "Epic"):
        out.append(Violation("ERROR", block.start_line, "epic-backlink",
                   "Story is missing the **Epic:** backlink line."))
    # Evaluation items must cite a requirement
    in_eval, saw_item = False, False
    for n, ln in block.lines:
        h = re.match(r"^##\s+(.*\S)\s*$", ln)
        if h:
            in_eval = h.group(1).strip() == "Evaluation"
            continue
        if in_eval and re.match(r"^\s*\d+\.\s+\S", ln):
            saw_item = True
            if "Validates R" not in ln and "Validates all" not in ln:
                out.append(Violation("ERROR", n, "eval-mapping",
                           "Evaluation item must start with **Validates R<n>** "
                           "or **Validates all**."))
    if "Evaluation" in [h for _, h in block.headings] and not saw_item:
        out.append(Violation("WARN", block.start_line, "eval-empty",
                   "Evaluation section has no numbered items."))


def check_epic(block, out):
    in_stories, count = False, 0
    for _, ln in block.lines:
        h = re.match(r"^##\s+(.*\S)\s*$", ln)
        if h:
            in_stories = h.group(1).strip() == "Stories under this epic"
            continue
        if in_stories and re.match(r"^\s*[-*]\s+Story\s+\d+", ln):
            count += 1
    if not (2 <= count <= 8):
        out.append(Violation("ERROR", block.start_line, "epic-story-count",
                   f"Epic lists {count} stories; must be 2-8 named in "
                   f'"Stories under this epic".'))
    if "epic" not in [lbl.lower() for lbl in block.labels]:
        out.append(Violation("ERROR", block.start_line, "epic-label",
                   'Epic archetype must carry the `epic` label.'))


def check_hardening(block, out):
    # each ### issue needs a **Fix:** before the next ###
    issue_line, has_fix, n_issues = None, False, 0
    for n, ln in block.lines:
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
    out.append(Violation("WARN", block.start_line, "labels-verify",
               "Verify the domain label exists in the target workspace "
               "(run list_issue_labels); do not invent a taxonomy."))


def validate_block(block):
    out = []
    check_title(block, out)
    check_em_dash(block, out)
    check_vague_verbs(block, out)
    check_ai_tells(block, out)
    check_sections(block, out)
    check_labels(block, out)
    if block.archetype == "story":
        check_story(block, out)
    elif block.archetype == "epic":
        check_epic(block, out)
    elif block.archetype == "hardening":
        check_hardening(block, out)
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
