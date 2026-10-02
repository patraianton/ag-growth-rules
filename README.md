# ag-growth-rules

Rules and a checker for agent-written growth copy at Annuities Genius (AG): launch email, social post, webinar page, IMO note, "how this was made" note.
Each rule is a landmine (a kind of sentence agents get wrong) with its source of truth, regex cues and fixtures taken from one real piece, the AG CRM launch kit.

## The run on the kit, 2026-10-02
Full record: [process/runs/2026-10-02-ag-kit/README.md](process/runs/2026-10-02-ag-kit/README.md).

- The 2026-10-01 version: exit 1, 189 findings (32 critical, 79 major, 78 minor): compliance promises with no owner, two call-recording rules in two pieces, three cut lines back, "right away" setup promises, counts with no source ([before.txt](process/runs/2026-10-02-ag-kit/before.txt)).
- v5, the text the four review rounds passed: 46 findings, 7 of them critical compliance promises ([process/misses.md](process/misses.md) row 18).
- Fix pass (46 lines cut, 53 rewritten) and the four blockers of one review: exit 0 ([after.txt](process/runs/2026-10-02-ag-kit/after.txt)).
- plain-language: 21 findings on the 11:00 version, 0 on the released one; grades: how-made 11.2 → 6.6 (max 11), email 5 → 4.5 (max 9), social 4 → 3.9, webinar 5 → 5.2, IMO note 5.6 → 5.1 (max 9) ([plain-before.txt](process/runs/2026-10-02-ag-kit/plain-before.txt)).
- Released text, `kit.md` sha256 `9cf4cc0e...` (the judge-items version `0d2075eb...` plus the "Important" note under the repository link): exit 0 with `--panel` and `--reviewed-sha256` ([important-after.txt](process/runs/2026-10-02-ag-kit/important-after.txt)).
- Refute pass by another model family (gpt-5.6-sol) on the 9 facts rows: 6 held, 2 overturned, 1 not checkable ([refute-codex.md](process/runs/2026-10-02-ag-kit/refute-codex.md)).
- Not run: steps 1-2 again, step 6 as written, stage 2, a live reader. No reviewer read the released text.

## Run it
```
python tools/selftest.py
python tools/check.py path/to/draft.md --claims templates/claims.csv
python tools/check.py draft.md --html page.html --claims templates/claims.csv --panel panel/ --reviewed-sha256 <hash>
```

Exit codes: 0 clean, 1 findings, 3 not run. Flags and file formats: [tools/README.md](tools/README.md). CI runs the self-test and the two samples in `tools/fixtures/sample/`.

## The line ([process/LINE.md](process/LINE.md))
1. Frame and coverage: every source type mapped in `templates/coverage.md` before the draft.
2. Facts table: `templates/facts.md`, each fact CONFIRMED, CLAIMED, ABSENT or UNKNOWN, with a date.
3. Refute pass: an agent on another model family tries to overturn the facts rows.
4. Draft with claims ledger and numbers file: `templates/claims.csv` (UNMARKED = 0), `templates/numbers.json`.
4½. Plain pass: one idea per sentence, AG's words (`templates/plain-pass.md`); check `plain` at 0.
5. Lint: `tools/check.py` on every version, exit 0 before anyone reads.
6. Blind check and one review round: pinned personas, severities, no 1-10 scores (`templates/panel/`).
7. Decision log: `templates/decisions.md`; a promise in AG's name is closed only by a named AG owner.
8. Release with hash match: the shipped sha256 equals the last checked one.

## The nine landmines ([rules/landmines/](rules/landmines/))
- `product-claims`: what AG's product does today: features, screens, menu paths.
- `compliance-promises`: consent, call recording, texting registration, retention, data use.
- `pricing-plans`: prices, plan names and contents, trials, "live on all plans".
- `setup-timelines`: "right away", "nothing to set up", minutes and weeks.
- `competitors-partners`: GoHighLevel and other rivals, IMO tools, integration partners.
- `numbers-and-sources`: every count, rank, share and quote, and "about" around it.
- `research-absence`: "AG has no X" without where it looked.
- `process-claims`: how the work was done: order of steps, coverage, review rounds.
- `plain-language`: long sentences, overloaded bullets, unexplained terms, shorthand side-note titles, history in feature copy.

MIT licence ([LICENSE](LICENSE)).
