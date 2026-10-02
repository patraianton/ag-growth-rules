# Frame and coverage map (step 1)

Written before the first line of the draft. Its commit must be older than the first draft commit.
Every "I read N ..." sentence in the how-made note is copied from this table, never typed.

Filled with the kit's real coverage from the 01.10.2026 audit (`notes/annuities-genius/crm-features-audit-2026-10-01.md`,
section 6, lines 167-176). Paths are in the author's private repository; `raw/` is `crm-research/raw/` in the author's private working folder.

## Frame: what the brief's words mean inside the company

One row per word in the brief or the research that names a product, a rival or a goal. A row that cannot be filled goes to step 7.

| word | what it means inside AG | source | asked? |
|---|---|---|---|
| "GoHighLevel" | AG's own mail runs through LeadConnector, a GoHighLevel brand (`lc.annuitiesgenius.com`), next to Amazon SES, SendGrid, Zoho, Mailcoach, Kartra and Customer.io. A launch framed against GoHighLevel may touch AG's own marketing stack | audit line 24 (DNS records, certificates) | no; the kit never mentions it (`process/misses.md` row 17) |
| "CRM" | the Client Profile as a case file: reports, illustrations, documents, notes, the E-App; a CRM since 2019 | audit section 4 item 9; kit.md line 35 | |

Cost ceiling, set by Anton at this step: none was set for the kit (`templates/decisions.md`, release record).

## Rules

- One row per source type. Required types: help center, every channel video (captions), Shorts, site
  pages, pricing history, company and executive posts, third-party and partner videos, the product itself.
- A facts row labelled ABSENT names at least one covered row here by id. If it cannot, it becomes UNKNOWN.
- A type with nothing keyword-searched and not every item read in full allows no absence claim and says so
  in the last column. `tools/check.py` fires research-absence F2 on an ABSENT row that names it.
- When two files give different counts for the same type, write both with their sources. Do not pick one.

## Table

| id | source type | total | read fully | keyword-searched | not covered | proof |
|---|---|---:|---|---|---|---|
| COV-01 | AG help center articles | 93 | 93 | 93, plus about 60 queries in the help center search | videos embedded in articles 28, 72, 96, 102, 130 | audit line 169 |
| COV-02 | AG channel videos | 103 | 23 by the audit summary; 29 ids listed as "closely read" in the lane file, some of them from other channels | about 60, by captions; captions exist for 101 of 103 | 1 unavailable, 2 without captions | audit line 170; `raw/audit-youtube.md` lines 7, 112 |
| COV-03 | AG Shorts | 38 | 5 | captions for 33 (caption files in `raw/audit-youtube-captions/`) | 5 without captions, named in `raw/audit-youtube.md` line 8 | `raw/audit-youtube-captions/search-lists/tab-shorts.txt` (38 ids, 2026-10-01); `raw/audit-youtube.md` lines 8, 112. Line 8 says 30 Shorts; it was wrong, fixed 2026-10-02 |
| COV-04 | AG site pages in the sitemap | 166 | 0 stated | 166 loaded and searched; about 15 pages outside the sitemap | none listed | audit line 171 |
| COV-05 | Snapshots of AG's pricing page, web archive | 65 | 65 | 65 | none | audit line 171 |
| COV-06 | Posts by AG, its founder and its CTO (LinkedIn) | 54 | 54 | 54; plus 33 webinar transcripts keyword-searched | posts older than about 10 per profile (behind login); Facebook and X | audit lines 173, 176 |
| COV-07 | App addresses, DNS records, certificates | about 120 address checks; 17 certificate names | 0 | all | anything behind login | audit lines 171-172 |
| COV-08 | Third-party and partner videos and pages | 11 videos | 1 (Valor, 22.05.2025) | 10 | insurance-forums threads 118230, 116290, 116835 | audit lines 170, 174, 176 |
| COV-09 | The product itself (behind login) | 1 | 0 | 0 | all of it; no absence claims from this type | audit section 5, lines 141-159 |

## The 30.09 brief, for comparison

The v1 draft's research note (`crm-module-brief-2026-09-30.md`) had no such table. Its coverage in the same
columns (ids 21 and up; the fixtures of `rules/landmines/research-absence.md` use them):

| id | source type | total | read fully | keyword-searched | not covered | proof |
|---|---|---|---|---|---|---|
| COV-21 | AG help center articles | not recorded (v1 of the kit said "105 help-center articles"; there are 93) | read, count not recorded | not recorded | | kit v1 "What was read" (`tools/fixtures/must_fire.jsonl` mf-14) |
| COV-22 | AG channel videos | not recorded | 3 webinars | 0 | the other videos, not opened | the same line: "3 AG launch webinars" |
| COV-23 | The product itself | 1 | 0 | 0 | all of it | brief section 10: "the closed part of the app was not checked" |

The effect is `process/misses.md` row 2.

## Sentences this table allows in the how-made note

- Allowed: "all 93 help-center articles", "the 103 videos on AG's channel, searched by their
  captions" (the read-fully count is 23 or 29 depending on the file, so it is not printed), "65 snapshots of the pricing page".
- Not allowed: "every public source" (COV-06 and COV-08 list gaps; COV-09 is not covered);
  "Before writing, I checked ..." unless this file's commit is older than the first draft commit.
