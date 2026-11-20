---
name: usage-review
description: Measure where Claude Code tokens went from the local transcripts, find what drives the cost, propose changes to CLAUDE.md or agents, and re-measure a change made earlier. Use when the user asks about usage, limits, spend or cost, says they ran out of their limit, or asks whether a rule change helped.
---

# Usage review

A loop: measure, find the driver, change one thing, measure again. The data is
the transcripts in `~/.claude/projects/`; `scan.py` beside this file reads them.
Nothing here leaves the machine.

## 1. Pin the question

One of:

- **Where does it go?** Default window: the last 7 days.
- **Did a change help?** Find when it was made (a dated note, the file's
  `git log`, or ask) and pass that time as `--cut`.
- **Why did I run out?** Ask the user for the usage page's bars (weekly %,
  and any per-model sub-cap such as Fable) and when the week resets. The
  transcripts can't see the limit.

Look for notes from earlier reviews first (memory, `~/.claude/usage-log.md`).
Never reuse their numbers; rerun and compare.

## 2. Measure

```sh
python3 -I <this skill's folder>/scan.py --since <YYYY-MM-DD> [--project <substr>] [--cut <iso>] [--prs prs.txt]
```

- **Units** weight tokens by API price ratios (cache reads 0.1, output 5) and
  by a per-model multiplier. The default multipliers are an estimate of how
  each model counts against a subscription limit. If the usage page shows a
  model's sub-cap, calibrate: its share of units should match its share of
  the bar, and `--weights fable=<n>` sets it.
- **Normalise by work done.** Units per day falls when less gets done. If the
  user ships through PRs, make `--prs` from each repo:
  `gh pr list --state merged --author @me --limit 500 --search "merged:>=<date>" --json mergedAt -q '.[].mergedAt' >> prs.txt`
- `--project` matches a substring of the project folder name in
  `~/.claude/projects/`. A value starting with `-` needs the `=` form:
  `--project=-myrepo-`.
- Use `--csv <dir>` when you need to go below the tables.

## 3. Find the driver before prescribing

Read the tables in this order:

1. **Main session vs subagents.** A long main session pays for its whole
   history on every turn: when the top sessions dominate, the fix is session
   length (fresh sessions, handoffs, delegation), not a cheaper model.
2. **Past the context threshold.** Context grows a few thousand tokens per
   turn, so a run's length sets its cost. A high share of units past 200k
   means runs are too long: split the work, or find what fills context early
   (tool results table: paging through files, big reads, images).
3. **Expensive models.** Check what each call buys before cutting it. A
   review that catches blocking bugs is cheap at its price; cut volume
   (fewer, larger units of work) before cutting quality.

Open two or three of the most expensive transcripts and confirm the mechanism
by hand: what filled the context, where the loop repeated. A table shows
where, not why.

## 4. Propose

Each proposal is one change to `CLAUDE.md`, an agent file or a habit, with:
the driver it targets, the number it should move, and when to re-measure.
Change one lever at a time, or the re-measure can't attribute the result.
Write nothing until the user approves.

## 5. Record

Append a dated entry to the user's notes (memory if the setup has it, else
`~/.claude/usage-log.md`): the window, the headline numbers, what changed and
when, the expected effect, and the re-measure date.

## 6. Re-measure

Rerun with `--cut` at the change. Compare per unit of work, not per day. Wait
for at least three working days after the change; one day or a weekend is
noise. Report the result against the expectation from step 4, including
when it didn't move.

## Traps

- **Peer sessions and automation** (`claude -p` jobs, scheduled agents) are
  transcripts too and count as main sessions. Split them out with
  `--project` before blaming the interactive work.
- **A per-model cap can share the overall limit.** A model's tokens can cost
  several times another's against the limit, more than API prices suggest.
  The usage page decides; calibrate the weight from it.
- **A fall in units/day after a change is not proof.** Check the work done
  fell less.

## Report

Lead with the answer to the question in step 1, then at most five lines of
numbers, then the proposals. Tables only if the user asks for them.
