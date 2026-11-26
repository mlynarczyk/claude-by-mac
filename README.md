# claude-by-mac

A Claude Code setup for handing work off and coming back to pull requests
ready to review. Describe the work, leave Claude to it, during the day or
overnight, and each PR you come back to says what changed and why before it
shows any code, and how it was checked.

What gets it there:

- **Sessions keep going without you.** An unattended session hands off to a
  fresh one at a natural break (`/handoff tab`), up to three in a row, so a
  long job doesn't stall on a full context.
- **Every PR walks you through itself.** `pr-flow` opens it with
  `## In plain terms`: the change as one real line from the diff, and what it
  means for someone using it. Then `## Verification`: the check's result, and
  a test broken on purpose and watched failing. A visual change carries before
  and after screenshots.
- **Mistakes are caught before you read it.** A plan gets a Fable review
  before anything is built, and a substantive diff gets a review before the
  PR opens: Fable for high-stakes changes, Opus for the rest.
- **It cleans up after you merge.** The PR watcher fixes merge conflicts and
  removes the worktree once a PR lands.
- **It runs on one plan.** The main session stays short, bulk work runs in
  subagents with their own context, and the most expensive model is called
  only for judgment.

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
  live state that session needs. Run it as `/handoff`; `/handoff tab` also
  opens the new session in a new Orca or iTerm tab. Tell Claude a session is unattended
  (or unsupervised, hands-off, overnight) and it chains tabs on its own, up to
  three sessions.
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

## What it changed for me

On the Ultra plan, working heavily: up to 11 sessions at once, about 150
merged PRs a week. From my transcripts:

- The reviews earn their cost: on one day, 4 of 7 Fable diff reviews found a
  blocking bug.
- In August my sessions ran on Fable. One week used up the Fable allowance in
  four working days, and 86% of that was the session re-reading its own
  history, not the work. With Opus as the session model and Fable only for
  reviews, the next days kept the same pace.
- In November, after tightening how work is split across subagents, a week of
  about 150 merged PRs cost a third less per day than the same output two
  weeks earlier (7.8M units per PR, down from 10.8M).

PR size varies week to week, so read the numbers as a direction. Your plan,
your models and how you work will move them; `/usage-review` measures your
own.

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
- **A backlog and a triage round**: unattended work leaves follow-ups behind
  (a review finding left for later, a gap a PR names). Mine go into a backlog
  kept as files in the repo, and a `/triage` skill gathers the follow-ups from
  merged PRs, shapes each into a card, and puts them on one local page I
  decide in a single sitting. It is tied to my backlog script, so it isn't
  here; ask Claude to build one around wherever you keep work.

Rule of thumb: the second time you explain something to Claude, ask it to
write it into one of these.
