# The line: eight steps from brief to send

Every piece (email, post, webinar page, IMO note, how-made note) goes through these steps in order. A step is done when its check passes; `not_run` and `uncertain` do not count. Anton's time for a piece the size of the AG kit: 40-45 minutes, at steps 1, 3, 6, 7 and 8 (an estimate, not measured). Once a quarter, 20-30 minutes: mark 20 reviewer findings agree or disagree. Anton never hands off: promises in AG's name, prices, people on stage, legal lines, the final read, the send.

Roles: **agent** writes and fills files; **program** is `tools/check.py`; **Anton** decides; **AG owner** closes a row at AG. Proposed owners: the founder for company promises and pricing, the CTO for product and telephony, the compliance owner for consent, recording and retention. Nobody at AG has agreed to own a row yet.

"On the AG kit" lines point to rows of `process/misses.md`.

## 1. Frame and coverage

Before the first line of copy: what the brief's words mean inside the company, and a coverage map of sources (type | total | read in full | searched by keyword | not covered).

- **Who:** agent builds it; Anton gives the feature list, trial access if any, and the cost ceiling (5 min).
- **Artifact:** `templates/coverage.md` (frame table, ceiling line, coverage table).
- **Check:** every required source type has a row (help center, all channel video captions, pricing archive, blog and posts, third-party demos, the product). A type that was neither searched nor read in full carries "no absence claims for this type", and `tools/check.py` fires research-absence F2 on an ABSENT row that names it. The file's commit is older than the first draft commit (checked by hand with `git log`). Any "I checked N ..." sentence in the how-made note takes N from this file.
- **On the AG kit:** misses rows 2, 5, 17.

## 2. Facts table

One row per fact, labelled CONFIRMED, CLAIMED, ABSENT or UNKNOWN, with an "as of" date and "applies to" (which plan, which seat). A quote is one row of the Quotes table: text, speaker, speaker's role, weight. The label rates the claim, not the type of source.

- **Who:** agents, several lanes, one lane on a different model family.
- **Artifact:** `templates/facts.md`.
- **Check:** ABSENT without a coverage id fails (research-absence F1). CONFIRMED without a date fails (product-claims F2). A quote without the speaker's role fails (stage 2).
- **On the AG kit:** misses rows 2, 10.

## 3. Refute pass

Before any draft exists, a separate agent on another model gets only the facts table and tries to overturn CONFIRMED and ABSENT rows, writing the result in each row's `refute` cell. Each overturned row is logged as a miss.

- **Who:** agent (different model family); Anton reads only the overturned rows (10 min).
- **Artifact:** the `refute` column of `templates/facts.md`; `process/misses.md`.
- **Check:** an ABSENT row with an empty `refute` cell fails (research-absence F4). `tools/check.py` prints the number of rows marked `overturned`; the pass is run again until a run overturns none. That count goes into the how-made note.
- **On the AG kit:** misses row 2.

## 4. Draft with claims ledger and numbers file

The draft is written from the facts table. Every factual sentence gets a ledger row with a status: SOURCED, PROPOSAL, TO-CONFIRM (owner, date). Every count lives in one numbers file with its source row and a flag: exact, approximate, double-counted, lane stopped. Ranks and shares are computed by the program. Every section names the reader decision it serves.

- **Who:** agent writes and fills; program computes; Anton 0 min.
- **Artifact:** `templates/claims.csv`, `templates/numbers.json`.
- **Check:** UNMARKED = 0 and every TO-CONFIRM has an accepted owner and a date (`claims`). A number in the text not found in `numbers.json` (numbers-and-sources F1, F4). "Approximate" in the source means "about" in the text (F3). A rank or share without a computed row (F2). At most 7 TO-CONFIRM marks in one section (`mark-budget`; the limit is the kit panel's own, `panel/round-3.md` line 104). A section with no named reader decision is cut (stage 2).
- **On the AG kit:** misses rows 6, 7, 8, 9, 11, 14.

## 4½. Plain pass

The draft is rewritten in plain words, one idea per sentence, before the lint: long sentences split, overloaded items cut down, terms explained, history and reasons moved to side notes. Facts, marks and structure stay; the hook and quoted speech are not touched.

- **Who:** agent with `templates/plain-pass.md`; Anton 0 min.
- **Artifact:** `plain-pass.md` in the run folder (`process/runs/<run>/`): the `was → now` list, one line per changed sentence.
- **Check:** `tools/check.py` check `plain` at 0 (`rules/landmines/plain-language.md` F1-F7, with the grade per section in the summary).
- **On the AG kit:** Anton's instruction of 2026-10-02 (the webinar title, the calls/texts/meetings bullet, side note 4).

## 5. Lint

`tools/check.py` runs on every version before any reviewer: landmine cues, banned words and shapes from `rules/voice.md`, stray label words in the rendered page text (shown with context, not as a bare count), sentence-level diff between the text file and the page, repeats of 8 words or more, one feature with one rule in every piece (compliance-promises F2), and lines cut by an earlier decision (`killed-lines`, from the table in `templates/decisions.md`). `python tools/selftest.py` runs the fixtures from the AG kit after every change to the rules or the program.

- **Who:** program; Anton does not read the text until this step is clean.
- **Artifact:** the `tools/check.py` report for the version, kept next to the draft; with `--stamp`, one record per landmine in `<piece>.stamps.jsonl`.
- **Check:** exit 0, or a written reason per finding. An exception to the banned list exists only as a line in `rules/voice.md` with AG's own usage count.
- **On the AG kit:** misses rows 3, 4, 12, 13.

## 6. Blind check and one review round

The fact check reads the claims ledger and sources, not the draft. A separate lane compares each factual sentence with its source row for meaning (lost caveats, ranges). Reader personas are written down once and do not change. One reviewer is from another model family, one is cold (no research folder), one is an adversary with a quota: three false claims, or a written reason there are none. Results are pass or fail per slop class with severity critical, major or minor; no 1-10 scores. Replacement text from reviewers goes through steps 4 and 5 before it is applied. A second round, if any, only cuts.

- **Who:** agents; Anton reads only the critical rows (10 min).
- **Artifact:** `templates/panel/personas.md`, `templates/panel/round.md`.
- **Check:** a verdict repeated word for word from a previous round is not accepted. A replacement without a source line is not applied. A round without a report file did not happen. At the last round, critical = 0 and new customer-copy sentences = 0.
- **On the AG kit:** misses row 16.

## 7. Decision log

The only place Anton decides. Everything a source cannot close goes here: promises in AG's name, prices, people on stage, consent capture, call recording, number registration, data sharing and export. A cut line goes to the killed-lines table. A live reader from the audience is requested here.

- **Who:** agent prepares rows; Anton decides his and proposes owners for the rest (10-15 min); the owners at AG close theirs, once they accept.
- **Artifact:** `templates/decisions.md` (decisions, killed lines, release record). The "To confirm" list in the copy is generated from it.
- **Check:** customer copy has 0 rows without a decision or an owner. Legal and company-promise rows are closed by a named person, not an agent. A killed line comes back only with a decision id in `reversed by`. The release record says whether a live reader was asked and answered; if not, the page says so.
- **On the AG kit:** misses rows 4, 12, 14.

## 8. Release with hash match

The hash of the shipped text equals the hash of the last reviewed version. The how-made note is built from `coverage.md`, the refute count, the round reports and `git log`, not from memory. The spend is written next to the ceiling from step 1.

- **Who:** program and agent; Anton 5 min for the final read and the send.
- **Artifact:** the release record in `templates/decisions.md`; a line in the how-made note: "reviewed version vN, sha256 ..."; a one-page index for a reviewer at AG with five links: facts table, claims ledger, round reports, decision log, version log.
- **Check:** `python tools/check.py <piece> --html <page> --claims <ledger> --panel <panel folder> --reviewed-sha256 <hash in the last round report>`. A hash mismatch fails `release-hash` and gives process-claims F4 on every round-count sentence; send is blocked. A round count above the number of `round-*.md` reports fails process-claims F3. Sentences about the order of work are checked against `git log` by hand (process-claims F1, F6). Spend over the ceiling is Anton's call, written in the release record.
- **On the AG kit:** misses rows 5, 15. No ceiling was set.

## What the line counts

| Measure | Target | Measured by | AG kit value |
|---|---|---|---|
| UNMARKED claims in customer copy | 0 | `claims` check on the ledger | no ledger existed; 0 product claims unmarked by round 4, at least 5 unsourced in the how-made note (misses rows 5-10). 2026-10-02: 15 rows after the tidy (E-12) (17 at the morning release), 0 UNMARKED, 14 PROPOSAL, 0 TO-CONFIRM |
| TO-CONFIRM marks in one email | at most 7, each with an owner | `mark-budget`; `claims` | 16 on the page, 0 owners. 2026-10-02: 7 on the page, 0 owners |
| Numbers not found in the numbers file | 0 | `numbers` | no numbers file; 2 counts without a source, 1 rank wrong. 2026-10-02: 0, with 26 records |
| ABSENT rows overturned before the draft | 0 after the last refute run | `landmines` note: "N overturned" | 3, found after the draft. 2026-10-02 refute pass, also after the draft: 0 ABSENT rows overturned, 2 CONFIRMED rows overturned (F-05, F-09) |
| Audit corrections to finished copy | at most 2 | by hand, from the audit file | 12 |
| Errors written by reviewers | 0 | by hand, from the round reports | at least 5 |
| Cut lines that came back | 0 | `killed-lines` | 2 (K-01, K-02), plus 1 new promise with no review (K-06). 2026-10-02: 0, all three cut again |
| Shipped hash = last reviewed hash | yes | `release-hash` | no. 2026-10-02: yes, against the hash the release check passed; no reviewer read that text |
| Live reader before send | yes, or the page says no | by hand, release record | no. 2026-10-02: no, and the page says so |
| `tools/check.py` findings on the shipped version | 0, or a written reason per finding | `tools/check.py` | 189 on the 2026-10-01 version (`before.txt`). 2026-10-02: 189 on the 2026-10-01 version without `--reviewed-sha256`, 0 on the released version (`process/runs/2026-10-02-ag-kit/README.md`) |
| Spend against the ceiling from step 1 | at or under | release record | no ceiling set; four rounds of six roles in about 70 minutes. 2026-10-02: refute pass 105,586 tokens; the rest not recorded |
| Reviewer findings Anton agrees with, on 20 marked findings | threshold set after the first marking | by hand, once a quarter | not counted |

## Limits

- The program matches numbers, words, repeats and mismatches, not meaning. A false sentence with no number and no banned word passes it; steps 3 and 6 carry the rest.
- The facts table and claims ledger are filled by a model. What is not written down as a row is not checked.
- Without product access part of the facts table stays UNKNOWN, and those lines stay marked in the copy.
- Personas are simulated readers, not a live reader.
- Every writer and reviewer on the kit was one model family. Step 3 ran once with a second family (gpt-5.6-sol, 2026-10-02), after the draft and on the facts table only; step 6 with a second family has not run.
- Steps 1 and 3 and a review of the shipped version add agent time per piece. On the kit (2026-10-02) the refute pass took 9 minutes and 105,586 tokens; the fix pass ran from 08:56 to 09:18; the rest was not timed.
- Legal and company-promise rows wait for named people at AG.
- Nothing here measures whether the copy works on readers.
- Every step above was written after the kit. The kit went through steps 3 (after the draft), 4, 5 and 8 on 2026-10-02, with one same-family review of the edit in place of step 6; step 7 got new rows and no decisions (`process/runs/2026-10-02-ag-kit/README.md`). Steps 1 and 2 hold the state seeded by hand. No piece has gone through steps 1 to 8 in order.
