---
name: handoff
description: Write a paste-ready prompt that starts a fresh session on the next piece of work. Use when the user asks for a handoff, a prompt for a new session, says the session is getting big or long, or wants to continue elsewhere. `/handoff tab` also opens the new session in a new Orca or iTerm tab.
---

# Handoff prompt for a fresh session

The output is one fenced block the user pastes into a new session, plus at
most one line outside it. The new session has CLAUDE.md, the rule files and
memory loaded already; it has none of this conversation.

## What goes in

A line belongs only if it **decides something the next session will do**.
Informing is the feature doc's job.

1. **The task, in one or two sentences**, and the doc that holds it (the active
   plan, the feature doc, a PR, a TODO item). Point; don't summarise.
2. **Read first**: the few files or doc sections the task starts from, with
   `file:line` where it helps. Not an inventory.
3. **Decisions already made by the user** that the next session would
   otherwise re-ask or reverse, as conclusions. Never the argument for them.
4. **Traps that bite on this task**, each naming where it bites ("`map_from/1`
   collapses a map to nil when exclude and include are empty, so a new key
   needs the emptiness check widened"). Frozen or parked work appears only
   as a trap at the path where it will be met.
5. **Live state the next session must act on**: unpushed commits, open PRs,
   running servers or stacks this session started, database copies,
   worktrees. Each as a fact plus the command that confirms it, because it
   may have changed by the time the prompt is pasted.
6. **The first step**, concretely: "Write the plan for X, get a Fable plan
   review, then build", or "Fix the review findings on PR #N". When the task
   is a new user-facing surface, the first step is design explorations (3-4
   structurally different directions) and an explicit **stop until the user
   confirms a direction**, unless the user has already picked one.

## What stays out

- What this session did. Link the PR or commit instead.
- The status of work nobody is doing.
- The case for a settled decision. Keep the conclusion, cut the case.
- Anything CLAUDE.md, a rule file or memory already says. The next session
  has those; repeating them makes the handoff the copy that drifts.
- Counts and inventories that will be wrong by morning.

## How to write it

1. **If the next task is unclear, pick the obvious one** (the next item in the
   active plan, or the user's last stated direction) and say in the line
   outside the block which you picked. Ask only if two candidates are equally
   likely and they lead to different work.
2. **Check live state, never write it from memory.** Run, batched:
   `git branch --show-current`, `git log --oneline origin/<main>..<main>`,
   `gh pr list --author @me --state open`, `git worktree list`, and `lsof` on
   any port this session started a server on. Put only what the next session
   has to act on into the prompt.
3. **Write the block.** Imperative voice, addressed to the next session, plain
   and terse. Aim for under 40 lines. Headings only where they help scanning.
4. **Test each line** against "does this decide something the next session
   will do?" and cut what fails.
5. Outside the block, one line at most: something left running that the user
   may want to stop, or which next task you picked. Nothing else.

Don't write the prompt to a file unless asked, or opening it in a tab (below):
it's a message, not a document.
If the project keeps memory, check that the durable parts of the work (a user
direction, a trap that will outlive the task) are in memory or the feature
doc **before** writing the handoff, so the prompt can point at them.

## Opening it in a new tab

When the user runs `/handoff tab`, or says "open it" after a handoff, start the
fresh session for them instead of leaving the block to paste:

1. Write the block's contents (without the fence) to
   `<scratchpad>/handoff-<slug>.md`, the slug naming the next task.
2. Open a tab running `claude` with it as the first message, from the repo
   root of this session:

   ```bash
   ~/.claude/skills/handoff/open-tab.sh <repo root> <file> [extra claude args]
   ```

   It opens the tab in the terminal this session runs in: Orca (macOS or
   Linux, through the `orca` CLI) or iTerm (macOS, through `osascript`). The
   prompt is read in the new tab's shell, so backticks and `$` pass through
   as text.
3. If it exits non-zero (2 is an unsupported terminal; otherwise iTerm's
   Automation permission refused or Orca unreachable), print the block as
   usual and give the file's path.
4. Reply in one line: the tab is open, and the file's full path in case the
   user needs to paste it by hand. You cannot see the tab, so say so rather
   than claiming the session started.

### Unattended

When the session is unattended (global CLAUDE.md; also called unsupervised,
hands-off or overnight), nobody is there to paste the block, so:

- **Finish first.** Commit the unit in hand. Stop every background watcher
  and server this session started, and list each one the next session must
  restart (a PR watcher, a dev server) under Live state with its
  command, so two sessions never work the same tree.
- **Carry the mark.** The block's first line is
  `Unattended session, generation <n> of 3: hand off with /handoff tab, not an offer.`
  with `n` one past this session's (1 if it had none). At generation 3, don't
  open a tab: print the block and stop, so a bad loop cannot fan out.
- **Same permission mode.** Pass `--permission-mode <mode>` as an extra
  claude arg to `open-tab.sh`, naming this session's mode (`auto`, `acceptEdits`, …). A tab that
  stops on its first permission prompt does nothing until morning.
- **Then stop.** After the tab opens, do no more work in this session.
