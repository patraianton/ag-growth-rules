---
version: 1
changed: 2026-10-02
asked_by: Anton Patrai
---

# Panel personas (step 6)

A persona is a measuring instrument: change it and round-over-round results measure the persona, not the text.

Rules
- Personas never change between rounds of one piece. A change is a new `version` of this file with a
  `rules/CHANGELOG.md` entry, and counts from rounds on different versions are not compared.
- Each round report names the `personas.md` version it used.
- Every persona gets its listed seed files and nothing else. A finding that cites a file outside the seeds
  is marked `uncertain`.
- Replacement text from any persona goes through steps 4 and 5 (claims ledger, lint) before it is applied.

On the kit (`process/misses.md` row 16) all six roles were prompts on one model family reading one research
folder, so a gap in the folder was a gap in all six. Two roles drifted between rounds:

| role | round 1 | round 2 | round 4 |
|---|---|---|---|
| agent-reader | "61-year-old annuity agent" | "22-year Texas annuity agent on Redtail" | same as round 2 |
| imo-exec | "IMO executive" | "IMO owner, 900 agents, 6-person Case Design desk" | "IMO owner, 900 agents, HighLevel CRM handed out free" |

## The six reader roles (model family A, strongest model available)

Paths are in the author's private repository, `notes/annuities-genius/`.

| id | pinned definition | reads | seeds |
|---|---|---|---|
| agent-reader | Independent annuity agent, 22 years licensed, Texas, pays for an own AG seat, keeps Redtail as the book of record, about 400 existing clients | the customer copy | `agent-portrait-v3-2026-09-30.md`; `crm-module-brief-2026-09-30.md` section 3; `ghl-complaints-2026-10-01.md` insurance section |
| imo-exec | IMO owner, 900 agents, a 6-person Case Design desk; its agents get a free white-label CRM (both attributes appeared in the kit rounds; version 1 pins both) | the customer copy, the IMO note first | `imo-interview-brief-2026-09-30.md`; the IMO research notes of 2026-09-27 |
| hiring-manager | AG's hiring manager for the Head of Growth role, judging the kit as a work sample | everything | `test-task-brief.md` |
| voice-editor | AG house voice | the customer copy | `crm-style-guide-2026-09-30.md`; `rules/voice.md` |
| design-critic | the rendered page at 390 px and 1280 px, and the printed PDF | `index.html`, the PDF | AG's site styles (`raw/ag-launch-style.md`) |
| fact-checker | blind: checks claims, never sees the draft | `claims.csv`, `facts.md`, `numbers.json` | the sources linked from those rows |

## The three added readers

| id | model | reads | job |
|---|---|---|---|
| other-family | model family B | the customer copy and `facts.md` | the same defect list as the six, so a gap shared by family A shows up as a disagreement |
| cold-reader | family A | the customer copy only: no research, no brief, no facts table | marks every sentence it would ask "says who?" about; each mark must map to a `claims.csv` row or it becomes a defect |
| prosecutor | family B | `facts.md`, `coverage.md`, the customer copy | quota: three false claims, each with the row and the source that breaks it, or a written reason per piece why there are none. Tries ABSENT rows first. |

None of the three has run on any piece yet: no round report here or in the kit's `panel/` folder names them.
The prosecutor is the step-3 refuter run again on the draft.
