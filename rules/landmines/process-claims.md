---
id: process-claims
version: 1
changed: 2026-10-02
asked_by: Anton Patrai
strictness: cite-or-cut
applies_to: [email, social, webinar, imo-note, how-made]
---

# Landmine: claims about how the work was done

## 1. What this landmine is

Any sentence about the making of the piece: the order of steps ("before writing, I checked"), coverage
("every public source"), duration ("built in one night"), review ("four review rounds of six readers"),
headcount ("a crew of agents", "six reviewers").

Strictness `cite-or-cut`: a process claim is generated from the record on disk or checked against it.

## 2. What it is not (hand-offs)

- Counts inside the research ("1,927 complaints", "98 IMO sites") → `numbers-and-sources`. This file owns
  the counts of the process: rounds, readers, agents, scripts, hours.
- Where a feature was searched for, as evidence for an ABSENT → `research-absence`. This file checks the
  sentence that describes coverage to the reader; both read `coverage.md`.

## 3. Source of truth (resolution order; stop at the first that resolves)

1. `git log` of the piece's folder: commit times and messages (kit v1 `662d63b` 2026-09-30 22:49, v5
   `816d805` 23:59).
2. File times and contents on disk: research notes, fix scripts, `panel/round-N.md`. One report file per
   round claimed.
3. `templates/coverage.md`: `read fully` and `keyword-searched` per source type. "Every", "all" and
   "read" resolve here.
4. The release hash (`process/LINE.md` step 8): the sha256 of the shipped text against the hash of the
   version the last round reviewed.

Never a source: the writer's memory, a plan file that describes the intended order, a reviewer's summary
of the process, the previous version of the how-made section.

## 4. Forbidden shapes (banned by shape)

- **F1 Order of work contradicted by timestamps.** "Before writing, I checked ..." where the file that did
  the checking is newer than the first draft commit. Class: invented-fact. Severity: critical.
- **F2 "Every" over a keyword scan.** "every source", "all the videos", "checked every" for a type where
  `coverage.md` shows part keyword-searched or not covered. Class: false-precision. Severity: major.
- **F3 Round count without a report per round.** "N review rounds" where the panel folder holds fewer than
  N `round-*.md` reports. Class: invented-fact. Severity: major.
- **F4 Review claim over unreviewed text.** A round count printed in a text whose sha256 differs from the
  version the last round reviewed. Class: contradiction. Severity: critical.
- **F5 Headcount that implies people or independence.** "six readers (an annuity agent, an IMO owner ...)"
  for prompts of one model family on one research folder, without saying they are simulated roles.
  Class: invented-fact. Severity: major.
- **F6 Duration contradicted by timestamps.** "In one night" where commits and fix scripts span longer.
  Class: invented-fact. Severity: minor.

## 5. Allowed with a row

- **A1** An order claim that matches git: "git shows the order: draft first, audit second."
- **A2** A neutral coverage verb with counts from `coverage.md` ("all 93 help-center articles" where the
  row says 93 of 93 opened).
- **A3** A round count equal to the report files, on the reviewed text, with what came after named:
  "four review rounds on v1 to v5; seven fix scripts after the last one, not reviewed".
- **A4** Simulated roles named as such: "six reader roles, one model family, one research folder".

## 6. Detection

**Stage 1.** Regex cues select the sentences. Two lookups follow in `tools/check.py`:
- F3: with `--panel <folder>`, the round count in the sentence is compared with the number of `round-*.md`
  files there. Equal or fewer: the hit is cleared. More: F3 stays, with both numbers. Without `--panel`
  every round count stays a hit.
- F4: with `--reviewed-sha256 <hash>`, every round-count sentence in a piece whose sha256 differs gets F4.

**Stage 2** (`rules/README.md`). F1 and F6 need dates the script does not read: stage 2 gets the sentence,
the output of `git log --format="%h %ad %s" --date=iso -- <piece folder>` and the file times of the
research notes named nearby, run by hand, and answers: does the order or duration in the sentence match
the record. F2 gets the `coverage.md` rows.

```cues
# rule | target | rescues | kind  | pattern
F1     | copy   | none    | regex | (?i)\bbefore (?:writing|drafting|the first line)\b
F1     | copy   | none    | regex | (?i)\b(?:first|step one)[,:]? (?:I|we) (?:checked|read|audited|went through)\b
F2     | copy   | none    | regex | (?i)\b(?:checked|read|reviewed) (?:every|each|all)\b
F2     | copy   | none    | regex | (?i)\bevery (?:public )?(?:source|video|article|post|review|page|thread)s?\b
F3     | copy   | none    | regex | (?i)\b(?:two|three|four|five|six|\d+) (?:review |panel )?rounds?\b
F5     | copy   | none    | regex | (?i)\b(?:of|by|with|rounds?|review) (?:two|three|four|five|six|seven|eight|\d+) (?:readers|reviewers|experts)\b
F5     | copy   | none    | regex | (?i)\bcrew of\b
F6     | copy   | none    | regex | (?i)\b(?:in|over) (?:one|a single) (?:night|day|hour|evening)\b
```

## 7. Fixtures

`piece_sha256` is the sha256 of the kit's `kit.md` working copy on 2026-10-02 (v9 plus the 23:41
correction); `reviewed_sha256` is the sha256 of `kit.md` at `eb2ef9d` (v4, the version round 4 reviewed),
from `git show eb2ef9d:<path> | sha256sum`. `panel_reports` is the count of `panel/round-*.md`.

```fixtures
{"id": "process-claims/F1/01", "rule": "F1", "expect": "fire", "target": "copy", "text": "1. **Step one: what the CRM does today.** Before writing, I checked every public source: all 93 help-center articles, the 103 videos and 38 Shorts on AG's channel,", "source": "kit.md v9:142 (excerpt); first written by apply-v7.py:47 (2026-10-01 17:36), v9 wording is the old string in anti-slop/fix-kit-how-made.py:6", "record": "draft v1 662d63b 2026-09-30 22:49; crm-features-audit-2026-10-01.md file time 2026-10-01 17:10; coverage: 23 videos read fully, about 60 keyword-searched (audit line 170)"}
{"id": "process-claims/F1/02", "rule": "F1", "expect": "fire", "target": "copy", "text": "Before writing a launch for new CRM functionality, I checked what the CRM does today, from public sources only, so the launch calls new only what is new.", "source": "ag-public/crm-audit.html:62 (published audit page, markup dropped), file time 2026-10-01 17:45", "record": "draft v1 662d63b 2026-09-30 22:49"}
{"id": "process-claims/F2/01", "rule": "F2", "expect": "fire", "target": "copy", "text": "Before writing, I checked every public source: all 93 help-center articles, the 103 videos and 38 Shorts on AG's channel,", "source": "kit.md v9:142 (excerpt)", "record": "coverage.md COV-02: 23 of 103 videos read fully, the rest searched by captions; COV-09 the product: not covered"}
{"id": "process-claims/F3/01", "rule": "F3", "expect": "fire", "target": "copy", "text": "then put through four review rounds of six readers each", "source": "kit.md final:140 (excerpt); no --panel given, so the count is not checked and the hit stays"}
{"id": "process-claims/F4/01", "rule": "F4", "expect": "fire", "target": "copy", "text": "then put through four review rounds of six readers each", "source": "kit.md final:140 (excerpt); the rounds saw v1 to v4, the shipped text is v9 plus corrections", "panel_reports": 4, "piece_sha256": "719d5a855b6006c848df9a74143634d04309e2bb6b11976a3b913aa185773ca5", "reviewed_sha256": "ebfb265c004674edbd4085ec41b552dd3bc7ab983848f6dedd893b9fde49228a"}
{"id": "process-claims/F5/01", "rule": "F5", "expect": "fire", "target": "copy", "text": "Built in one night, September 30 to October 1, by a crew of research and writing agents I run, then put through four review rounds of six readers each (an annuity agent, an IMO owner, the hiring manager, AG's house voice, a design critic, a fact-checker), with fixes applied between rounds.", "source": "kit.md final:140", "record": "the six readers were prompts on one model family (panel/round-1.md to round-4.md)"}
{"id": "process-claims/F6/01", "rule": "F6", "expect": "fire", "target": "copy", "text": "Built in one night, September 30 to October 1, by a crew of research and writing agents I run,", "source": "kit.md final:140 (excerpt)", "record": "v1 662d63b 2026-09-30 22:49; 7 fix scripts on 2026-10-01 15:43 to 22:51 (apply-v6, v6b, v7, audit-fixes, v7b, v8, v9)"}
{"id": "process-claims/F3/n01", "rule": "F3", "expect": "no_fire", "target": "copy", "text": "I read 3,803 public reviews, posts, and feature requests about it from eight source types and sorted 1,927 complaints by module (counts are close, not exact: two lanes read the same review sites):", "source": "kit.md final:143 (excerpt)"}
{"id": "process-claims/F3/n02", "rule": "F3", "expect": "no_fire", "target": "copy", "text": "then put through four review rounds of six readers each", "source": "kit.md final:140 (excerpt); panel/ holds round-1.md to round-4.md, so the count itself holds (F4 is the problem with this line)", "panel_reports": 4}
{"id": "process-claims/F1/n01", "rule": "F1", "expect": "no_fire", "target": "copy", "text": "I caught it a day later by asking \"are we sure?\" and running a six-lane audit with four labels, CONFIRMED, CLAIMED, ABSENT, UNKNOWN, where ABSENT has to say where it looked; it produced twelve corrections, including \"since 2023\" to \"since 2019\", and git shows the order: draft first, audit second.", "source": "not kit text: a drafted note on the process, by Anton (excerpt)"}
{"id": "process-claims/F2/n01", "rule": "F2", "expect": "no_fire", "target": "copy", "text": "1. **Step one: what the CRM does today.** I went through the public record: all 93 help-center articles, the 103 videos and the Shorts on AG's channel, 166 site pages and 65 snapshots of the pricing page since 2019,", "source": "kit.md final:142 (excerpt), after the 2026-10-01 23:41 correction"}
{"id": "process-claims/F5/n01", "rule": "F5", "expect": "no_fire", "target": "copy", "text": "**Three readers, one message:** the agent who pays for their own seat · the agent who came through an IMO · the IMO's Case Design desk (its own note, below).", "source": "kit.md final:7; audience segments, not a review claim"}
{"id": "process-claims/F3/n03", "rule": "F3", "expect": "no_fire", "target": "copy", "text": "Check after the fix: copy the rendered text of the page and search it for `offer offer`, `sync.`, `export.`, `Activity.`, `number.`, `wait.`, `switch.`, `registration;`, `shared.`, `co-sign.`. Expect zero hits.", "source": "not kit text: panel/round-4.md:57"}
```

The final kit's line 140 fires F4, F5 and F6. Lines 142 and 143 were corrected on 2026-10-01 at 23:41 by
`anti-slop/fix-kit-how-made.py`; line 140 was not.
