# claude-by-mac

A Claude Code setup that spends tokens where they change the outcome. The
main session stays short, bulk work runs in subagents with their own context,
and the most expensive model is called only for judgment: plan reviews, design
direction, stuck debugging.

## Install

```sh
claude "Fit the setup at https://github.com/mlynarczyk/claude-by-mac to me, following its ADAPT.md."
```

Or paste that sentence into a session you already have open.

Claude reads your existing `~/.claude/`, asks what it can't find out (your plan,
what you work on), and shows you the adapted files before installing anything.
To pick up later changes, ask it to "update my setup from claude-by-mac".

## What each piece does

- **`CLAUDE.md`**: the rules. Sessions run on Opus; Fable is called only for
  judgment calls. Bulk work goes to subagents so the main session stays
  short, because every turn re-reads the whole conversation and long sessions
  are the main cost.
- **`agents/implementer.md`**: does planned edits in its own context and hands
  back a short note. Keeps the main session from filling up with file dumps.
- **`agents/fable-consult.md`, `agents/opus-consult.md`**: read-only reviewers.
  You send a write-up, they return a verdict. They never edit.
- **`agents/designer.md`**: draws one round of 3-4 design directions from a
  spec file, checks each frame against it, and returns a short report with a
  contact sheet. The main session writes the spec and judges the result; the
  drawing and the image reads stay out of its context. Needs a drawing tool
  Claude can drive (a design-tool MCP, or HTML rendered to PNG). Ask Claude to
  "write a spec for a designer round on X".
- **`skills/handoff/`**: writes a paste-ready prompt that starts a fresh
  session on the next piece of work, carrying only the decisions, traps and
  live state that session needs. Run it as `/handoff`.
- **`skills/usage-review/`**: measures where your tokens went from the local
  transcripts (main session vs each subagent type, model shares, runs past
  200k context, what filled the context), proposes changes to `CLAUDE.md` or
  the agents, and re-measures a change you made earlier. Run it as
  `/usage-review`, or ask "where did my usage go this week?".
- **`skills/pr-flow/`**: for projects that opt in, feature and fix work goes
  through a worktree and a pull request you review and merge. Claude commits,
  opens the PR in a set shape (`## In plain terms`, then verification), then
  watches it: it fixes merge conflicts and cleans up the worktree once you
  merge, without being asked. A project opts in by naming its check command
  and base branch in its `CLAUDE.md`.

## Habits that save the most

- Start a fresh session between unrelated tasks.
- Take the handoff when it's offered. Past ~100 turns, Claude offers
  `/handoff` at the next natural break; paste the prompt it writes into a new
  session. You can run `/handoff` yourself any time.
- Put project rules in the project's own `CLAUDE.md`; keep the global one
  short. Both are re-read on every turn.

The usage figures in `CLAUDE.md` are from my sessions. Run `/usage-review` to
get yours.

## The other half

This repo is global config only. The other half lives in each project's
`.claude/` folder, gets committed with the code, and is where most of the
gains are, because there Claude stops guessing how your project works:

- **A project `CLAUDE.md`**: the codebase's rules and conventions. Keep it to
  rules. Lists of files, counts and status go stale, and it is re-read every
  turn.
- **Path-scoped rules** in `.claude/rules/`: detail that loads only when Claude
  opens matching files, so frontend rules don't cost tokens during backend
  work.
- **Project agents** in `.claude/agents/`: agents that know the project's
  tools. I use `verify-check`, which runs a scripted browser check against the
  app and reports pass/fail with screenshots, and a `designer` tied to my
  drawing kit and design folder. The `designer.md` here is a stripped-down
  copy of that one.
- **Skills** in `.claude/skills/<name>/SKILL.md`: workflows you repeat, written
  once. Examples: how to launch and verify the app, add a migration, run a
  review round. Claude loads one when the task matches, or you call it as
  `/name`.

Rule of thumb: the second time you explain something to Claude, ask it to
write it into one of these.
