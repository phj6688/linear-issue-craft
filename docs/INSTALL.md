# Install

The skill is a single folder. There are three install patterns depending on how you want to use it.

## 1. Symlink into `~/.claude/skills/` (Claude Code, single-user)

```bash
ln -s "$(pwd)/skill" ~/.claude/skills/linear-issue-craft
```

Claude Code auto-discovers skills under `~/.claude/skills/`. From any project, the skill becomes available under the name `linear-issue-craft`. Invoke explicitly with `/linear-issue-craft`, or let Claude pick it up via the skill description ("draft a Linear issue", "open an epic", etc.).

To uninstall:

```bash
rm ~/.claude/skills/linear-issue-craft
```

## 2. Copy into a target project's `.claude/skills/`

If you want the skill scoped to one project only (so it doesn't load globally):

```bash
cp -r skill /path/to/your-project/.claude/skills/linear-issue-craft
```

Then commit `.claude/skills/linear-issue-craft/` into that project's repo. The skill becomes available only in sessions opened in that project.

## 3. Use as a raw prompt reference

Paste the contents of `skill/SKILL.md` followed by the relevant `references/<NN>-*.md` file as a system prompt in a non-Claude-Code chat. Works in web Claude, ChatGPT, Cursor, etc.

## Verifying the install

After installing via method 1, open a Claude Code session anywhere and ask:

> draft a Linear issue: I want to add a referrals system to my web app. Capture `?ref=` query params, persist a 30-day cookie, attribute on signup.

If the skill is installed correctly, the assistant should:

1. Identify the archetype (likely a Story under a `Public-facing UX` epic, or part of a new `Growth & Attribution` epic).
2. Produce a draft using the Story body template.
3. Pick labels (`web`, plus capability) and a priority (Medium).
4. Pause before posting and show the draft for approval.

If you get a generic "Add referrals system" issue with no current-state diagnosis, the skill isn't being picked up — double-check the symlink.

## Dependency on the Linear MCP server

To actually file drafts in Linear, you need the Linear MCP server configured in your Claude Code settings. See [Linear's MCP docs](https://linear.app/docs/mcp). The skill produces drafts that are ready to be passed to `mcp__linear-server__save_issue` once approved.
