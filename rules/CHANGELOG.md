# Rules changelog

Newest first. Each entry: date, rule set and version, what changed, why, who asked.

## 2026-10-02 · check `plain` v2 (page tooltips)

- With `--html`, `plain` also reads the tooltip (`title=`) of every dotted span on the page for F4 (unexplained terms and abbreviations) and F5 (shorthand cues), reported at the span's line. Fixtures `mf-plain-12` ("porting time: to confirm" fires F4), `mn-plain-09` (the plain tooltip does not). Why: the judge after wave 3 found jargon and shorthand in tooltips the check never read. Asked by: Anton Patrai.

## 2026-10-02 · `voice` v3 (VB1 cue), check `stray-labels` v2

- VB1: the cue no longer selects a list that opens with a channel noun (email, call, text, meeting): `(?!(?:emails?|calls?|texts?|meetings?),\s)\w+, \w+,? and \w+`. Such a list is concrete, and VB1 is about abstract words. Fixtures: `mf-38` (v1 "Book, confirm and remind" still fires), `mn-24` (the agreed bullet does not).
- `stray-labels`: on the page, a label hit whose whole sentence is also written in `kit.md` (parity-normalised) is the author's sentence end, not a printed label, and is skipped. Hits on text that the markdown does not carry still fire (`mf-18` to `mf-24` unchanged). `selftest.py` passes the fixture's `text` as the source when a fixture has both `text` and `html`. Fixture `mn-25`.
- Why: the owner's agreed bullet "Text any client [from your own number]. ... Each call, text and meeting is saved on the case." fired VB1 and the "number." label. Wave 1 had reworded it to dodge both; the plain-pass review put the agreed text back.
- `python tools/selftest.py`: 196 fixtures, 0 failed. The kit check exits 0.
- Asked by: Anton Patrai.

## 2026-10-02 · `plain-language` v1, check `plain` v1, `voice` v2 (section 8, AG's own terms)

- New landmine and check: F1-F7 (long sentence, overloaded item, repeated phrase, term not explained, shorthand side-note title, hard section by Flesch-Kincaid grade, history or reason in feature copy), 33 fixtures from kit `048e9d8`, the agreed rewrites and the working tree; strictness `rewrite` added; `process/LINE.md` step 4½ and `templates/plain-pass.md`. Why: the copy carried the facts in prose built to impress. Asked by: Anton Patrai.

## 2026-10-02 · `competitors-partners` v1 (F1, A4, fixture sources), `numbers-and-sources` v1 (fixtures F1/01, F2/01), `voice` v1 (scope)

- Wording only. F1 now describes "kill" or "replace" framing in general; A4 and the `voice.md` scope let how-made name
  GoHighLevel as a research subject. Two fixture texts lost a clause that the fire did not depend on (F1/01 still
  fires on 600, F2/01 on "top-ten"). No cue, shape or severity changed, so no version change.
- `python tools/selftest.py`: 160 fixtures, 0 failed. The release command in
  `process/runs/2026-10-02-ag-kit/README.md` exits 0.
- Asked by: Anton Patrai.

## 2026-10-02 · `numbers-and-sources` v1, fixture F4/01; `templates/numbers.json` N-03, N-26

- N-03 is 38 Shorts, from the raw tab list (`crm-research/raw/audit-youtube-captions/search-lists/tab-shorts.txt`,
  38 ids, 2026-10-01). It was 30, from `raw/audit-youtube.md` line 8, which was wrong. No version change: the
  shapes and cues are the same.
- F4/01 now fires on the audit note's "30 shorts listed" against an inline record of 38; before, it fired on
  the kit's "38 Shorts", which was right. 30 is not listed under N-03 `conflicts` in `templates/numbers.json`:
  the F4 check does not read the unit, and the kit prints "30 minutes".
- N-26: 30 minutes, the masterclass length (`raw-own-scan-2026-09-23.md` line 42). The kit's "30 minutes"
  had passed on N-03 while it held 30 Shorts.
- `python tools/selftest.py`: 160 fixtures, 0 failed. The release command in
  `process/runs/2026-10-02-ag-kit/README.md` exits 0.
- Asked by: Anton Patrai.

## 2026-10-02 · check `facts-count` v2

- `tools/check.py` `check_absence`: a facts row counts as overturned only when the last verdict word in its
  `refute` cell (`held`, `overturned`, `unverifiable`) is `overturned`. Before, the word anywhere in the cell
  counted. No finding changes; only the count in the `landmines` note.
- Why: the release run printed "5 overturned" while the refute pass overturned 2 (F-05, F-09); the cells of
  F-01, F-02 and F-04 keep their 01.10 history. Found by a read of the repository.
- Fixtures: `mn-22`, `mn-23` in `tools/fixtures/must_not_fire.jsonl`, with a new `stats` field the self-test
  checks. `python tools/selftest.py`: 160 fixtures, 0 failed.
- Asked by: Anton Patrai (finish the kit on 2026-10-02).

## 2026-10-02 · check `repeats` v2

- `tools/check.py` `check_repeats`: URLs and markdown link targets are blanked before the 8-word scan, with
  the regex `check_voice` already uses. Landmine and voice versions are unchanged; `rules/manifest.json` now
  also lists `checks.repeats`.
- Why: a false positive in the run of 2026-10-02: two links to pages on patraianton.github.io on two lines
  in a row fired `repeats/8-words` with no repeated prose.
- Fixture: `mn-21` in `tools/fixtures/must_not_fire.jsonl`, the two link lines. `python tools/selftest.py`:
  158 fixtures, 0 failed.
- Asked by: Anton Patrai (finish the kit on 2026-10-02); the change was made by the run's fix pass and checked
  by the Fable review of it (`review-fable.md`, note 3).

## 2026-10-02 · initial versions

- `voice` v1 · counts from the AG style guide of 2026-09-30 (40 blog posts, 24 LinkedIn posts, 17 webinar
  descriptions, 2 launch transcripts, site pages). VN1 (competitor names) applies to email, social,
  webinar and imo-note; how-made may name GoHighLevel as a research subject (`competitors-partners` A4).
- `landmines.product-claims` v1, `compliance-promises` v1, `pricing-plans` v1, `setup-timelines` v1,
  `competitors-partners` v1, `numbers-and-sources` v1, `research-absence` v1, `process-claims` v1 ·
  first versions.
- Why: the misses of the AG CRM launch kit (test task, 30.09 to 01.10.2026), listed in `process/misses.md`.
- A review of the repository on 2026-10-02, before the first commit, found shapes with no fixture and
  detection text describing code that did not exist. Those shapes now have fixtures and code
  (`numbers-and-sources` F4 and F6, `research-absence` F2 and F4, `process-claims` F2, F3, F4, F6); the
  git-date comparison for `process-claims` F1 and F6 is a stage-2 step done by hand. The same review
  widened `voice` VB7 from two em dashes in one sentence to any em dash, to match `CLAUDE.md` rule 10.
- Asked by: Anton Patrai.
