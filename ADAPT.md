# Adapting this setup (instructions for Claude)

The person running you wants this repo's setup fitted to them. These files are
written for Mac's work and plan. Your job is to produce their version, not to
copy Mac's.

## 1. Read before asking

- Every file in this repo.
- Their `~/.claude/CLAUDE.md`, `~/.claude/agents/`, `~/.claude/skills/`, and
  the `model` key in `~/.claude/settings.json`, if they exist.
- Their OS (`uname`), whether `magick` (ImageMagick) is installed, and
  whether `gh auth status` succeeds.
- `~/.claude/claude-by-mac.md`, if it exists: they installed before, and
  this is an update (step 5).

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
- **Not on iTerm:** the `/handoff tab` section of `skills/handoff/SKILL.md`
  opens a tab through `osascript` and iTerm. Rewrite that command for their
  terminal (Terminal.app, Ghostty, tmux `new-window`), or drop the section
  and the unattended bullet in `CLAUDE.md` if they don't want it.
- **No design work:** leave out `designer.md`. **No code work:** leave out
  `implementer.md`, `skills/pr-flow/` and the code-specific lines in
  `CLAUDE.md` (diff review, failing checks, worktrees, pull requests).
  **Code but no GitHub, no working `gh`, or no PR review:** leave out
  `skills/pr-flow/` and the `## Pull requests` section. With `gh` missing but
  wanted, tell them how to install and log in, and install `pr-flow` anyway.
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

Where each piece goes:

- `CLAUDE.md` → `~/.claude/CLAUDE.md`, merged into theirs if they have one.
- `agents/*.md` → `~/.claude/agents/`.
- Each folder in `skills/` → `~/.claude/skills/<name>/`, scripts kept
  executable.
- The session model → `"model"` in `~/.claude/settings.json` (`"opus"`, or
  their strongest everyday model). Edit only that key; keep the rest of the
  file.

Then write `~/.claude/claude-by-mac.md`: the commit installed from
(`git ls-remote https://github.com/mlynarczyk/claude-by-mac HEAD`, or the
clone's `git rev-parse HEAD`), the date, and one line per adaptation you made
(what was left out, renamed or re-pointed, and why). Tell them to start a new
session, since `CLAUDE.md` and agents load at session start.

## 5. Updating

When `~/.claude/claude-by-mac.md` exists, adapt only what changed: diff the
repo from the recorded commit to `HEAD`, apply each change through the
adaptations recorded there, show the result as in step 4, and update the
recorded commit. A change to a file they left out is skipped unless it
changes the reason it was left out.
