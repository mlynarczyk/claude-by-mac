# claude-by-mac

Global config only. Nothing here is tied to a project.

## Adapt it with Claude (recommended)

Clone the repo, open Claude Code in it and say:

> Follow ADAPT.md and fit this setup to me.

It reads your existing `~/.claude/`, asks what it can't find out (your plan,
what you work on), and shows you the adapted files before installing anything.

## Install as is

```sh
cp CLAUDE.md ~/.claude/CLAUDE.md          # merge by hand if you already have one
mkdir -p ~/.claude/agents && cp agents/*.md ~/.claude/agents/
```

Then set the default model in `~/.claude/settings.json`:

```json
{ "model": "opus" }
```

## What each piece does

- **`CLAUDE.md`**: the rules. Sessions run on Opus; Fable is called only for
  judgment calls (plan review, design direction, stuck debugging). Bulk work
  goes to subagents so the main session stays short, because every turn
  re-reads the whole conversation and long sessions are the main cost.
- **`agents/implementer.md`**: does planned edits in its own context and hands
  back a short note. Keeps the main session from filling up with file dumps.
- **`agents/fable-consult.md`, `agents/opus-consult.md`**: read-only reviewers.
  You send a write-up, they return a verdict. They never edit.
- **`agents/designer.md`**: draws one round of 3-4 design directions from a
  spec file, checks each frame against it, and returns a short report with a
  contact sheet. The main session writes the spec and judges the result; the
  drawing and the image reads stay out of its context. Needs a drawing tool
  Claude can drive (a design-tool MCP, or HTML rendered to PNG) and
  ImageMagick for the sheet. Ask Claude to "write a spec for a designer round
  on X" and it will use the shape in the agent file.

## Habits that save the most

- Start a fresh session between unrelated tasks.
- Past ~100 turns, ask Claude for a handoff prompt and continue in a new session.
- Put project rules in the project's own `CLAUDE.md`; keep the global one short.
  Both are re-read on every turn.

## Notes

- The usage figures in `CLAUDE.md` (40% of cost past 200k context, etc.) are
  from my own sessions. Yours will differ; the direction holds.
- `/handoff` is a custom skill I have; without it, just ask "write a handoff
  prompt for a fresh session".
- `designer.md` uses `sips`, which is macOS-only. Elsewhere, swap it for
  ImageMagick's `magick <in> -resize 1600x1600 <out>`.
- If your plan doesn't include Fable, change `model: fable` to `opus` in
  `fable-consult.md`, or delete it and drop the Fable lines from `CLAUDE.md`.
