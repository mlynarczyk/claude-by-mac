# Global Guidelines

## Model routing

Sessions run on **Opus** (set in `settings.json`); the user never picks a
model. Fable has no pool of its own: its usage bar is a cap inside the one
weekly limit, and a Fable token costs several times an Opus token against it.
Spend it where judgment changes the outcome, never in a session loop.

**Default consults.** Skip one only when the work is trivial:

1. **Plan review** before implementing any multi-phase plan.
2. **Diff review** before a change is called done: on Fable for a schema
   change or anything the project's CLAUDE.md names as high-stakes, through
   `opus-consult` for any other substantive diff, none for a small fix.
3. **Design direction:** any choice between visual/UX directions, and
   whenever the user pushes back on the look of something.
4. **Debugging:** as soon as a bug's mechanism isn't explained after the
   first real attempt, not after a string of failed fixes.
5. **Architecture:** a decision that crosses subsystem boundaries or would be
   expensive to reverse (schema shape, API design).
6. **The user asks** ("ask fable").

Fable is reached only through `subagent_type: "fable-consult"`, never a fork,
which inherits the session model. The session implements what comes back.

## Subagents

**Keep bulk work in subagents.** Every turn re-reads the whole conversation,
so session length, not who types the edits, is the dominant cost.

- Implementation already planned in the session goes to `implementer`, never
  `general-purpose`, briefed with files, approach, constraints, how to
  verify, and file:line pointers. Trivial few-line edits stay inline.
- **An implementer gets a unit it can finish in about 60 turns**, where an
  agent passes 200k context whatever it is doing. A planned change goes whole
  unless its plan has several commits and it edits more than about 10 files;
  then it goes one implementer per commit. The session spawns each in turn
  and briefs it with the plan and the previous implementer's note, never the
  note alone, and has it read the earlier commits' diff. The diff review
  still covers the whole change, since commits can each be right and still
  not fit together.
- **When the session cannot name the code a change touches, find it
  first.** An `Explore` agent on `model: "sonnet"` lists the files and line
  ranges involved, and the implementer's brief carries that list, because
  an implementer left to find them crosses 200k before its first edit.
- Browser checks run in a Sonnet verification agent (the project's
  `verify-check` where one exists), never in the implementer, and the
  session judges any screenshots against the design itself.
- A review-fix round goes to a **fresh** implementer briefed with the branch,
  the diff and the findings, never a `SendMessage` to the old one: a
  continued implementer drags a 400k+ context into every fix turn. **The
  same holds for failing checks:** when an implementer hands back after two
  failures on the same step, a fresh one gets the diff, the failing output
  and its note.
- Closed-ended checks with objective criteria and no editing (verification,
  existence checks): `model: "sonnet"`.
- Trivial non-browser scans (grep-style sweeps, log scans): `model: "haiku"`.
- Planning and visual/design judgment never go to a downshifted agent.
- Between unrelated features, prefer a fresh session over one long one. When a
  feature's PR is open and the next ask is unrelated, say so in one line and
  suggest a fresh session before starting.
- **Past about 100 turns, offer a `/handoff` at the next natural break** (a
  PR opened, a plan approved, a round reported), in one line. A 1M window
  means a session never compacts, and past 200k context each turn re-reads
  the whole of it: on 2026-11-18, 40% of main-session cost was past 200k.

A project's own subagent rules take precedence for the cases they cover.

## Output style

- **No fluff.** No opening pleasantries, no conversational filler. Start with
  the answer.
- **No closing coda.** End on the last sentence that carries information. A
  trailing paragraph of adjacent context, bookkeeping, or something the user
  already said has no action or decision in it for them.
- **No purple prose.** Direct, literal, factual. No metaphor, no dramatization,
  no elaborating a point that is already made.
- **Brevity.** If a sentence or a snippet answers it, that is the answer. Length
  is earned by content, never by thoroughness for its own sake.

Lists for enumerable things; prose only where a claim needs a because. Never
fill a gap with speculative prose: state the assumption you are proceeding on,
in one line.
