# Adapting this setup (instructions for Claude)

The person running you wants this repo's setup fitted to them. These files are
written for Mac's work and plan. Your job is to produce their version, not to
copy Mac's.

## 1. Read before asking

- Every file in this repo.
- Their `~/.claude/CLAUDE.md`, `~/.claude/agents/`, and the `model` key in
  `~/.claude/settings.json`, if they exist.
- Their OS (`uname`), and whether `magick` (ImageMagick) is installed.

## 2. Ask only what you could not find

One round of questions, at most these:

- Which models their plan gives them, and whether Fable is among them.
- What they mostly use Claude Code for (code, design, writing, research).
- For design work: which drawing tool Claude can drive for them (a
  design-tool MCP, or HTML rendered to PNG).

## 3. Adapt

- **No Fable:** point `fable-consult` at their strongest model, or drop it and
  the Fable lines in `CLAUDE.md`. Keep the rule that consults are read-only
  and reserved for judgment calls.
- **Not on macOS:** replace `sips` in `designer.md` with ImageMagick
  (`magick <in> -resize 1600x1600 <out>`, crops with `-crop WxH+X+Y`).
- **No design work:** leave out `designer.md`. **No code work:** leave out
  `implementer.md` and the code-specific lines in `CLAUDE.md` (diff review,
  failing checks, worktrees).
- **Mac-specific references:** the usage figures in `CLAUDE.md` are from Mac's
  sessions, so keep them as rationale or cut them. If they already have a
  handoff skill, keep theirs and point the `/handoff` line in `CLAUDE.md` at
  it instead of installing `skills/handoff/`.
- **Their existing `CLAUDE.md` wins** where it conflicts with this one. Name
  each conflict instead of resolving it silently.

Keep what the setup is for: the main session stays short, bulk work runs in
subagents with their own context, and the expensive model is called only
where judgment changes the outcome.

## 4. Install only after approval

Show them the adapted files and a diff against anything they already have in
`~/.claude/`. Write nothing to `~/.claude/` until they say so, and never
overwrite an existing file without showing what it replaces.
