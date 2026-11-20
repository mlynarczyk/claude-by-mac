---
name: pr-flow
description: Ship a change through a worktree and a pull request the user reviews and merges, then watch the PR and act on its outcome. Use for feature and fix work in a project whose CLAUDE.md opts in (names a check command and base branch for pr-flow), when the user asks to set a project up for it, and when opening, updating or following up on a PR.
---

# Worktree → PR → the user merges

The user reviews and squash-merges every PR. The session does everything
before that and everything after it.

## What the project supplies

A project opts in by naming these in its `CLAUDE.md`, under a `pr-flow`
heading or line. When the user asks to set a project up for it, find them
(package scripts, Makefile, CI config, the default branch), confirm them with
the user, and add them there:

- **The check command**: the one command that must pass before a commit.
- **The base branch**: `main` or `master`.
- **Worktree setup**: what a fresh worktree needs beyond tracked files
  (dependencies, env files, build output), if anything.

Needs `gh`, logged in to an account that can push to the repo.

## The loop

1. **Branch in a worktree, from the remote base:**
   `git fetch origin && git worktree add ../<repo>-<name> -b <type>/<name> origin/<base>`.
   Never from the local base branch, which can carry unpushed commits into
   the squash. The worktree keeps half-built files out of the main checkout,
   where another session's checks and commits would pick them up. Then run
   the project's worktree setup.
2. **Build and verify.** Break the code a test covers, watch the test go red,
   restore it. Run the check command redirected, never piped:
   `<check> > /tmp/check.log 2>&1; echo $?`. A pipe reports the last
   command's exit status, so a failure reads as a pass.
3. **Review the diff** before opening the PR when the change is substantive,
   through a consult agent if the setup has one. Small fixes skip it.
4. **Commit without asking** once the unit of work is done and the check
   passes. One logical change per commit.
5. **Push and open the PR** once `git log origin/<base>..HEAD` lists only
   this branch's commits.
6. **Watch it.** Right after opening, run `pr-watch.sh <number>` (beside this
   file) in the background, and act on the line it prints without being asked:
   - `conflicts`: merge `origin/<base>` into the branch in its worktree,
     resolve, rerun the check, push, watch again.
   - `merged`: `git worktree remove <path>`, never with `--force`, so
     uncommitted work refuses instead of vanishing. Keep the branch: deleting
     it is the user's call.
   - `closed`: tell the user, and do nothing else.
   - `error` or `timeout`: tell the user what it printed.

Plan docs and one-line fixes nothing else depends on may commit straight to
the base branch, which is pushed only when the user asks. When another session
may be live, never switch the main checkout's branch: that session's next
commit lands on whatever is checked out.

## Commit subject and PR title

`<type>(<scope>): <description>`. A PR title is a commit subject, because the
squash makes the title the commit that lands.

- **Types**, a closed list: `feat`, `fix`, `refactor` (no behavior change),
  `perf` (the body says what was measured), `design` (visual), `test`,
  `docs`, `style` (formatting only), `build`, `ops`, `chore`. A change that
  fits none is two changes.
- **Scope**: the subsystem, lowercase. Leave it off when there is no single one.
- **Description**: what the change does, plain and lowercase, the outcome over
  the mechanism. `fix(editor): stop a heading's lines rendering on top of each
  other` beats `fix(editor): heading fix`.

A commit body carries only what the diff can't show: a measured result, a
cause ruled out, a decision the code doesn't record.

## PR body

Open with `## In plain terms`, written last from the finished diff:

- The change as one line of real code from the diff, with a one-clause gloss.
- One concrete sentence of what that means for a person using it.
- For a fix: why nothing caught it, naming what failed (no test pinned it,
  the check never ran).
- Why it matters, in consequences.

Then `## Verification`, always: the check command's result, and the
break-on-purpose outcome with the named test and its failure message. Never
claim a guard you didn't watch fail.

Optional, only when there is something real to say: what was deliberately
left alone and why; follow-ups for a person to act on; behavior that looks
like a hole but is intended.

**Screenshots:** a visual change carries before and after, a new surface an
after. Same viewport, page, theme and scroll, cropped to what moved. Take the
before first, before touching the code. `gh` can't attach images to a PR, so
upload them where the project keeps them, or hand the files to the user to
drag into the PR.

Tables for anything enumerable. Never restate the diff.

## Has a branch shipped?

Ask the PR, not git: `gh pr list --head <branch> --state merged`. Squash-merged
commits never appear in the base branch's history, so `git log
origin/<base>..<branch>` lists a shipped branch's commits forever.
