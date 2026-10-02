---
id: research-absence
version: 1
changed: 2026-10-02
asked_by: Anton Patrai
strictness: cite-or-cut
applies_to: [email, social, webinar, imo-note, how-made]
---

# Landmine: "AG does not have X" (ABSENT)

## 1. What this landmine is

Any statement that a feature, page, integration or behaviour does not exist ("AG has no telephony",
"agents cannot initiate chats", "no CSV import", "the client timeline is empty"), and any launch line that
presents as new something that already exists. In the facts table this is the label ABSENT.

Strictness `cite-or-cut`: an ABSENT stays only with a `templates/coverage.md` row that names where it
looked. ABSENT without a coverage row becomes UNKNOWN and is printed as a question or a bracket.

## 2. What it is not (hand-offs)

- A promise that AG will add something → `product-claims`.
- A zero inside a study ("one record in 1,927") → `numbers-and-sources`.
- A competitor's missing feature ("GoHighLevel has no quoting"): the evidence is checked here, whether the
  line may be printed at all is `competitors-partners`.
- "AG never shares data with carriers" is a promise → `compliance-promises`.

## 3. Source of truth (resolution order; stop at the first that resolves)

1. `templates/coverage.md`: one row per source type (`id | source type | total | read fully |
   keyword-searched | not covered | proof`). An ABSENT row in `facts.md` names the covered rows by id
   (`COV-01, COV-02`) in `where_searched`. A type with nothing searched and not all read allows no
   absence claim.
2. A dated company statement of absence, CONFIRMED with URL ("no importing from a CSV file, but you can
   export", AG video, 2025-09-24).
3. The refute pass (`process/LINE.md` step 3): a second agent on a different model gets only the facts
   table and tries to overturn every ABSENT row. It writes the result in the row's `refute` cell: who,
   which model family, `held` or `overturned`, and the new label.

Never a source: one help article (one source type), the reliability grade of the source instead of the
claim ("high" on "Agents cannot initiate chats" from a single help article), "I didn't see it", a reviewer
who read the same research folder and agreed.

## 4. Forbidden shapes (banned by shape)

- **F1 ABSENT without a coverage row.** A facts row that says a thing does not exist ("cannot", "inbound
  only", "is empty", "not found", or the label ABSENT) and names no `COV-` row. Class: false-absence.
  Severity: critical.
- **F2 ABSENT on an uncovered type.** The row names a `COV-` row that does not exist in `coverage.md`, or
  one whose type was neither keyword-searched nor read in full. Class: false-absence. Severity: critical.
- **F3 "New" for something that existed.** A launch line that presents as new a feature with a CONFIRMED
  past or present row. Class: false-absence. Severity: major.
- **F4 ABSENT that skipped the refute pass.** An ABSENT row whose `refute` cell is empty.
  Class: false-absence. Severity: major.

## 5. Allowed with a row

- **A1** ABSENT with every named coverage row searched or read in full.
- **A2** A dated company statement of absence ("a CSV import (AG has none today)").
- **A3** UNKNOWN printed as a question in the "To confirm" list ("Do they still exist, and does the
  follow-up plan become them?").
- **A4** A narrow CONFIRMED with its limit ("Chat with website leads only, from one shared number").

## 6. Detection

**Stage 1.** Absence is checked in the facts table, not in copy. F1 and F3 are cues
(`facts` target: the data rows of the facts table, refute column blanked; `copy` as in `product-claims.md`).
F2 and F4 are lookups in `tools/check.py` (`check_absence`): for each ABSENT row it reads the named `COV-`
rows from `--coverage` (default `templates/coverage.md`) and the row's `refute` cell. ABSENT rows that name
coverage while `coverage.md` is missing make the check `not_run`. The same pass prints how many rows the
refute column marks `overturned`.

```cues
# rule | target | rescues | kind  | pattern
F1     | facts  | none    | regex | ^(?!.*\bCOV-\d+\b).*\|\s*ABSENT\s*\|
F1     | facts  | none    | regex | (?i)^(?!.*\bCOV-\d+\b)\|.*\b(?:cannot|can't|inbound only|only inbound|is empty|not found)\b
F3     | copy   | bracket | regex | (?i)\bnow shows up\b
F3     | copy   | bracket | regex | (?i)\btext back and forth\b
F3     | copy   | bracket | regex | (?i)\bfor the first time\b
```

**Stage 2** (`rules/README.md`) gets the row or sentence and the named coverage rows, not the draft. It
answers: which source types would show this feature, were they searched, did the refute pass try.

## 7. Fixtures

`must_fire` rows for F1, F2 and F4 are rows of the 30.09 brief (`crm-module-brief-2026-09-30.md`, Russian),
translated and reformatted as facts rows; the brief had no facts table, no coverage ids and no refute
pass. Its video coverage is `COV-22` in the "30.09 brief" table of `templates/coverage.md`. All three brief
rows passed four review rounds and were overturned by `crm-features-audit-2026-10-01.md` line 20.
`must_not_fire` rows are rows of `templates/facts.md` and translated ABSENT rows of the 01.10 audit,
with their lanes written as coverage ids.

```fixtures
{"id": "research-absence/F1/01", "rule": "F1", "expect": "fire", "target": "facts", "text": "| 6 | Chat: inbound only. The client confirms a phone with a code on the agent's site; \"Agents cannot initiate chats from the platform\"; messages go from (225) 535-4832 | help article 101 | high |", "source": "crm-module-brief-2026-09-30.md:63 (translated); overturned by AG video 2025-10-27, an agent writes to a lead first (audit line 37)"}
{"id": "research-absence/F1/02", "rule": "F1", "expect": "fire", "target": "facts", "text": "| 5 | Everything created under a selected client saves to the profile; the activity timeline exists per staff member only, on the client it is empty | help articles 25, 112 | high |", "source": "crm-module-brief-2026-09-30.md:62 (translated); overturned by partner video 2025-05-22, '7 months ago, I ran the annuity navigator' (audit line 97)"}
{"id": "research-absence/F1/03", "rule": "F1", "expect": "fire", "target": "facts", "text": "| Public description of calls, meetings in the product, mail and calendar sync, tasks and deal stages | not found | ABSENT |", "source": "crm-module-brief-2026-09-30.md:87, section 1.3 (translated, reformatted as a row); tasks with a repeat shown in partner video 2025-05-22 (audit line 96)"}
{"id": "research-absence/F2/01", "rule": "F2", "expect": "fire", "target": "facts", "text": "| id | claim | label | where_searched | refute |\n|---|---|---|---|---|\n| B-6 | Agents cannot initiate chats from the platform; chat is prospect-initiated only | ABSENT | COV-22 | |", "coverage": "| id | source type | total | read fully | keyword-searched | not covered | proof |\n|---|---|---|---|---|---|---|\n| COV-22 | AG channel videos, as the 30.09 brief covered them | not recorded | 3 webinars | 0 | the other videos, not opened | kit v1 'What was read' lists 3 AG launch webinars and no other video (must_fire.jsonl mf-14) |", "source": "crm-module-brief-2026-09-30.md:63 (translated, reformatted as an ABSENT row with the brief's own video coverage); the video that overturned it is in the type the brief did not open"}
{"id": "research-absence/F4/01", "rule": "F4", "expect": "fire", "target": "facts", "text": "| id | claim | label | where_searched | refute |\n|---|---|---|---|---|\n| B-1.3 | Public description of calls, meetings in the product, mail and calendar sync, tasks and deal stages | ABSENT | COV-21, COV-22 | |", "source": "crm-module-brief-2026-09-30.md:87 (translated, reformatted as a row); the brief had no refute pass"}
{"id": "research-absence/F3/01", "rule": "F3", "expect": "fire", "target": "copy", "text": "- **Calls, texts, and meetings from the case.** Call from your computer, text back and forth, send a booking link - the reminder goes out on its own. All of it is saved on the case automatically.", "source": "kit.md@816d805:27 (v5); audit section 4 item 1: two-way lead chat on the case since 2023"}
{"id": "research-absence/F3/02", "rule": "F3", "expect": "fire", "target": "copy", "text": "- **Follow-ups that don't slip.** GrantAI's follow-up plan now shows up on the case as reminders.", "source": "kit.md@816d805:28 (v5, excerpt); audit section 4 item 2: dated, repeating tasks shown 2025-05-22"}
{"id": "research-absence/F1/n01", "rule": "F1", "expect": "no_fire", "target": "facts", "text": "| Calls, own calendar, mail sync, deal stages, campaigns | not found in 93 help articles, 101 captioned videos, 166 site pages, 65 pricing snapshots, DNS records and app routes | ABSENT | COV-01, COV-02, COV-04, COV-05, COV-07 |", "source": "crm-features-audit-2026-10-01.md:22 (translated, reformatted as a row)"}
{"id": "research-absence/F1/n02", "rule": "F1", "expect": "no_fire", "target": "facts", "text": "| Meetings: own calendar, availability, sync with Google or Outlook | /calendar, /meetings, /crm/calendar return 404; 'calendar' in two unrelated help articles only | ABSENT | COV-01, COV-07 |", "source": "crm-features-audit-2026-10-01.md:38 (translated, reformatted as a row)"}
{"id": "research-absence/F2/n01", "rule": "F2", "expect": "no_fire", "target": "facts", "text": "| id | claim | label | where_searched | refute |\n|---|---|---|---|---|\n| F-07 | AG syncs the agent's inbox (Gmail, Outlook) and logs email on the case | ABSENT | COV-01, COV-02 (101 captioned videos), COV-04 (40 blog posts), COV-07 (/email, /inbox, /crm/emails return 404) | held (audit line 35, confidence high) |", "coverage": "| id | source type | total | read fully | keyword-searched | not covered | proof |\n|---|---|---:|---|---|---|---|\n| COV-01 | AG help center articles | 93 | 93 | 93, plus about 60 queries in the help center search | videos embedded in articles 28, 72, 96, 102, 130 | audit line 169 |\n| COV-02 | AG channel videos | 103 | 23 by the audit summary | about 60, by captions | 1 unavailable, 2 without captions | audit line 170 |\n| COV-04 | AG site pages in the sitemap | 166 | 0 stated | 166 loaded and searched | none listed | audit line 171 |\n| COV-07 | App addresses, DNS records, certificates | about 120 address checks | 0 | all | anything behind login | audit lines 171-172 |", "source": "templates/facts.md F-07 and templates/coverage.md COV-01, 02, 04, 07 (01.10 audit)"}
{"id": "research-absence/F4/n01", "rule": "F4", "expect": "no_fire", "target": "facts", "text": "| id | claim | label | where_searched | refute |\n|---|---|---|---|---|\n| F-06 | AG has calling: a dialer, click to call, a call log, call recording | ABSENT | COV-01, COV-02, COV-04, COV-05, COV-07 | held; the 2020-2023 in-app voice recorder is a separate fact (audit line 60) |", "source": "templates/facts.md F-06 (columns cut to five)"}
{"id": "research-absence/F3/n01", "rule": "F3", "expect": "no_fire", "target": "copy", "text": "- **Follow-ups that don't slip.** GrantAI's follow-up plan [becomes dated reminders on the case], each drafted by GrantAI from the illustration you sent and your call notes.", "source": "kit.md final:26 (excerpt)"}
{"id": "research-absence/F3/n02", "rule": "F3", "expect": "no_fire", "target": "copy", "text": "Text any client - not only website leads - [from your own number].", "source": "kit.md final:25 (excerpt)"}
{"id": "research-absence/F1/n03", "rule": "F1", "expect": "no_fire", "target": "copy", "text": "- Reminders: tasks with a due date and a repeat appear in a partner's May 2025 video and nowhere in the 2026 materials. Do they still exist, and does the follow-up plan become them?", "source": "kit.md final:174"}
```

The audit has its own count slip: line 22 says 131 videos, line 170 says 103 videos and 30 Shorts (the raw tab list has 38 Shorts, `templates/numbers.json` N-03). F1/n01
uses the 101 captioned videos from line 170.
