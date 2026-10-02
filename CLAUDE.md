# CLAUDE.md: agent entry for ag-growth-rules

Read first: `process/LINE.md`, `rules/README.md`, `rules/voice.md`, the landmine for every topic the piece touches, the template for your step, `process/misses.md`.

## Hard rules

1. UNMARKED is zero: every factual sentence in customer copy is SOURCED, PROPOSAL or TO-CONFIRM (`templates/claims.csv`).
2. ABSENT names where it looked; without a coverage row it is UNKNOWN (`templates/coverage.md`).
3. Every number has a row in `templates/numbers.json`; ranks and shares are computed; approximate counts say "about".
4. Promises on consent, call recording, retention, export and data sharing are closed only by a named AG owner (`templates/decisions.md`).
5. A cut line stays cut in any wording unless a decision row reverses it in the killed-lines table.
6. A sentence about how the work was done is checked against file dates and `git log`.
7. A check result is `pass | fail | not_run | uncertain`; only `pass` is pass; exit 3 outranks 1.
8. Reviewers use the pinned personas (`templates/panel/`), report per slop class with severity critical, major or minor, no 1-10 scores; their replacement text passes steps 4 and 5 first.
9. Ship only the text whose sha256 equals the last reviewed version; only Anton sends it.
10. AG voice: no em dashes, no banned word without a counted exception in `rules/voice.md`.

## Conventions

- English. A sentence that adds no rule, check or fact is cut.
- A rule changes only through the five steps in `rules/README.md`, "How to change a rule".
- A new miss goes to `process/misses.md` with the file that proves it, and to `tools/fixtures/must_fire.jsonl`.
