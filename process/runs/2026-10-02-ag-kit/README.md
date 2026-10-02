# Run 2026-10-02: the AG CRM launch kit

Piece: the kit's `kit.md` and `index.html` (`$K` below), published at https://patraianton.github.io/annuities-genius-crm-launch-kit/.

## What ran, in order (2026-10-02)

1. 08:56 · step 5, `tools/check.py` on the 2026-10-01 version (sha256 `719d5a85...`): exit 1, 189 findings, 32 critical, 79 major, 78 minor ([before.txt](before.txt)).
2. 08:59-09:08 · step 3, refute pass by gpt-5.6-sol (OpenAI, Codex), facts table only: 9 rows, 6 held, 2 overturned (F-05, F-09), 1 unverifiable (F-03); 105,586 tokens ([refute-codex.md](refute-codex.md)).
3. 08:56-09:12 · fix pass by agents on Anthropic models: 46 lines cut, 53 rewritten, exit 0, sha256 `b6ca08cc...`. Every edit with its reason: `templates/decisions.md`, "Edits of 2026-10-02".
4. 09:12-09:18 · review of the fix pass by Fable (Anthropic, the writers' model family), on `b6ca08cc...`: 4 blockers, 9 notes ([review-fable.md](review-fable.md)).
5. 09:18-09:19 · the 4 blockers applied word for word (E-08 to E-11): exit 0, sha256 `7a990378...` ([after.txt](after.txt)).
6. Then steps 4, 7, 8: claims ledger (17 rows, 0 UNMARKED), numbers file (26 records), decision rows, how-made rewrite: exit 0 with `--panel` and `--reviewed-sha256` ([release.txt](release.txt)).
7. The checker on v5 (git `816d805`, the text after the four review rounds), markdown only: exit 1, 46 findings (`process/misses.md` row 18).

Per check, 2026-10-01 version → released: landmines 59 → 0, voice 16 → 0, numbers 24 → 0, parity 38 → 0, stray-labels 3 → 0, repeats 12 → 0, time-promises 17 → 0, claims 4 → 0, mark-budget 2 → 0, killed-lines 14 → 0, release-hash not run → pass.
`before.txt` and `after.txt` print "3 overturned": the checker of that time counted old verdicts in the `refute` cells. `release.txt`, with the current checker, prints 2.

## Released
plain-language: 21 findings on the 11:00 version (git `048e9d8`, sha256 `f7a2cfd4...`: F1 8, F2 4, F3 1, F4 3, F5 2, F6 1, F7 2; [plain-before.txt](plain-before.txt)), 0 on the released one; grades: how-made 11.2 → 6.6 (max 11), email 5 → 4.5 (max 9), social 4 → 3.9, webinar 5 → 5.2, IMO note 5.6 → 5.1 (max 9). Three waves: wave 1 (`2379ba69...`); wave 2 (21 lines, plain-pass.md) put the owner's agreed bullet back word for word and added plain words next to terms (`voice` v3, `stray-labels` v2); wave 3 (`da2ba966...` → `227644d9...`, 10 lines, plain-pass.md) added plain words next to the remaining terms and shorthand; the judge items after wave 3 (`0d2075eb...`, plain-pass.md) fixed the meaning of side note 6 (Twilio's wait is per campaign review), explained "the desk view" and "carriers", and put the page tooltips in plain words, which check `plain` now reads. Last, the owner's "Important" note went under the repository link (E-19; → this version): public sources only, no confidential information, the repository deleted after 24 hours (`numbers.json` N-27).
`kit.md` sha256 `9cf4cc0e6fe7812a02d32d1453da5fc8dbfc2a2b423ad747bfb3b633beaa7393`, from the repository folder:
```
python tools/check.py $K/kit.md --html $K/index.html --claims templates/claims.csv --panel $K/panel --reviewed-sha256 9cf4cc0e6fe7812a02d32d1453da5fc8dbfc2a2b423ad747bfb3b633beaa7393
```
Result: exit 0, 0 findings in all 12 checks ([important-after.txt](important-after.txt); before the note: [judge-after.txt](judge-after.txt); after wave 3: [plain-after.txt](plain-after.txt); the version before the plain pass: [release-wave5.txt](release-wave5.txt)). Against the 2026-10-01 version: the explanatory paragraphs and the long how-made section cut to six short numbered steps under the title, pieces and side notes kept; `claims.csv` 17 → 15 rows. Edits with reasons: E-12 to E-19 in `templates/decisions.md`; plain pass line by line: [plain-pass.md](plain-pass.md).
Without `--panel` it exits 1: process-claims F3 on "four review rounds" needs the four round reports. "Reviewed" here means the checker passed this hash; no reviewer read this text. Rule and check changes made in this run: `rules/CHANGELOG.md`.

## What did not run

- Steps 1 and 2 were not redone; `templates/coverage.md` and `templates/facts.md` hold the state seeded by hand. Step 3 ran after the draft, once.
- Step 6 as written (blind fact check, pinned personas, cold reviewer, adversary), stage 2, a live reader. No AG owner accepted a decision row; D-01 to D-16 are open. Spend after the refute pass was not recorded.
