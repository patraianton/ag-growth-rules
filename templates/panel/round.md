# Panel round N: <piece>, merged editor report

Copy to `panel/round-N.md` for each round. A round without this file was not held.
Sample rows: six defects of the kit's round 4 (`panel/round-4.md`, 30.09.2026, v4, git eb2ef9d). Round 4
gave 1-10 scores per lens; the classes, severities and counts are ours, assigned on 2026-10-02.

## Header

- Date: 2026-09-30
- Version reviewed: v4, git `eb2ef9d` (kit.md and index.html).
- Personas: `templates/panel/personas.md` version 1. Roles that ran: (list ids).
- Kind of round: content | cuts only. On a cuts-only round, a fix that adds a sentence to customer copy is rejected.
- Lint before the round: `tools/check.py` exit code and finding count on this version. The round does not start on exit 3.
- sha256 of the reviewed `kit.md`: (the release hash in step 8 must equal this).
- Live reader from the audience: requested yes / no; answered yes / no. On the kit: not requested.

## Counts: slop class by severity

| class | critical | major | minor |
|---|---:|---:|---:|
| invented-fact | 1 | 1 | 0 |
| filler | 0 | 0 | 1 |
| empty-structure | 0 | 0 | 0 |
| false-precision | 0 | 0 | 1 |
| false-absence | 0 | 0 | 0 |
| voice-drift | 0 | 0 | 0 |
| contradiction | 0 | 1 | 0 |
| render-artifact | 1 | 0 | 0 |

No 1-10 scores (why: `process/misses.md` row 16).

## Defects

| # | class | severity | quote | file:line | fix | lens |
|---|---|---|---|---|---|---|
| 1 | render-artifact | critical | "Plans, attendee offer offer," | index.html v4:238 | the dotted span goes on the claim, the note lives only in `title`; then search the rendered text for the 10 strings in round-4 P1-1, expect 0 hits, show context for each hit | all six |
| 2 | invented-fact | critical | "If you ever leave, one export takes it all with you [confirm]." | kit.md v4:45 | cut; open a `decisions.md` row (D-10) | imo-exec |
| 3 | invented-fact | major | "Keep the number your clients know: bring your office line over, or pick a new local number [confirm]. Calling starts right away." | kit.md v4:36 | "Pick a local number and start calling right away - or [bring your office line over]." | fact-checker, voice-editor, agent-reader |
| 4 | contradiction | major | "Live on every plan from [date]." | kit.md v4:47 | cut; the IMO note says the agency decides | agent-reader, imo-exec, voice-editor |
| 5 | filler | minor | "without ever leaving the platform" | kit.md v4:24 | cut | agent-reader |
| 6 | false-precision | minor | "About 90 words without hashtags; AG's recent posts run 55–75." | index.html v4:212 | cut; AG's posts run 35-201 words | fact-checker, hiring-manager |

A replacement in the `fix` column cites the source line it rests on, or it is not applied. Steps 4 and 5 run
on it first (`personas.md`).

## Counters

| counter | this round |
|---|---|
| false claims found | 3 (defects 2, 3, 4) |
| promises removed | 2 (export; "Live on every plan") |
| sources added | 0 |
| minutes | about 11 (v4 commit 23:44, round-4 report 23:55, git times) |

## Verdict

One sentence that names what changed. A sentence repeated from the previous round is rejected.

Rejected on the kit: "Ship after edits. All six lenses said so." in rounds 2 and 3, repeated in round 1
("All six reviewers said so") and round 4 ("All six lenses said so, and every accepted fix is a cut or a move, with no new copy.").

## Release gate for the last round

- critical = 0.
- New sentences in customer copy = 0.
- Every fix applied; the version after the fixes gets the release hash. On the kit, seven fix scripts ran
  on 01.10 after the last round, and no round saw the result.

## Decisions for Anton

Rows added to `decisions.md`, by id. Nothing is decided in this file.
