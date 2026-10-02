# Facts table (step 2, refuted in step 3)

One row per claim about AG's product, written before the draft. The draft may state a product fact only
if a row here backs it (`claims.csv` column `facts_row`). Numbers do not go here: they go to `numbers.json`.

Rows from the 01.10.2026 audit (`notes/annuities-genius/crm-features-audit-2026-10-01.md`,
lines 33-116). Coverage ids refer to `coverage.md`. Step 3 ran once, on 2026-10-02, after the draft, not before it:
`process/runs/2026-10-02-ag-kit/refute-codex.md` (9 rows: 6 held, 2 overturned, 1 unverifiable). The two overturned
claims were narrowed to their source's words; the pass has not been run again on the narrowed rows.
The refuter's UNKNOWN applied to the original wording of F-05 and F-09; the table keeps CONFIRMED on the
narrowed claim, which is the article's own sentence.

## Labels

| label | means | row fails when |
|---|---|---|
| `CONFIRMED` | a company document, help article, screenshot or video shows it | no URL, or no date |
| `CLAIMED` | marketing text or an employee's words; nothing shown | the speaker's role is missing |
| `ABSENT` | searched where it should be and not found | `where_searched` names no `coverage.md` row; the row is then relabelled UNKNOWN |
| `UNKNOWN` | cannot be known without product access | never fails; it can only be bracketed in copy |

The label belongs to the claim, not the source type. Help article 101 says "Agents cannot initiate chats";
an AG video shows an agent starting one (F-01). The 30.09 brief graded the article's version top because a
help article is a company document.

## Columns

`id` · `claim` · `label` · `source` (URL and timestamp, or file:line) · `as_of` (the date the source shows,
not the date we looked) · `where_searched` (ABSENT and UNKNOWN only: coverage ids) · `applies_to` (plan,
reader, lead type) · `speaker` (for CLAIMED and quotes: who, role) · `refute` (step 3: who tried to overturn
it, on which model family, result `held` or `overturned`, and what the new label is)

`tools/check.py` reads `label`, `where_searched` and `refute`: an ABSENT row needs coverage ids that exist
and were searched (research-absence F2) and a filled `refute` cell (F4). The `refute` cell is not searched
for absence words; the run prints how many rows are `overturned`. A cell keeps its history, so only the
last verdict word in it (`held`, `overturned`, `unverifiable`) counts.

## Rows

| id | claim | label | source | as_of | where_searched | applies_to | speaker | refute |
|---|---|---|---|---|---|---|---|---|
| F-01 | An agent can start a text chat with a website lead from the client page | CONFIRMED | https://www.youtube.com/watch?v=sj0Sk18uV1A 37:00, frame "Chat with Rob · Start a conversation with your client now" | 2025-10-27 | | website leads with a validated phone; one shared number (225) 535-4832 | AG presenter, AG channel | 30.09 brief said ABSENT from help article 101; overturned 01.10 by the youtube lane. 2026-10-02, gpt-5.6-sol (OpenAI, via Codex; `process/runs/2026-10-02-ag-kit/refute-codex.md`): held (captions 36:46-37:35) |
| F-02 | Tasks with a due date and a weekly repeat exist on the client | CONFIRMED | https://www.youtube.com/watch?v=MbCFF5j-LTM 28:17, "add this task due next week. Uh, repeat every week" | 2025-05-22 | | as shown in 2025 | partner (Valor Financial Specialists), not AG staff | 30.09 brief said ABSENT; overturned 01.10. 2026-10-02, gpt-5.6-sol (OpenAI, via Codex; `process/runs/2026-10-02-ag-kit/refute-codex.md`): held (captions 28:25-28:32) |
| F-03 | Those repeating tasks still exist in the 2026 product | UNKNOWN | | 2026-10-01 | COV-01 ("task" appears only as "taskbar"), COV-02 (no 2026 webinar shows tasks), COV-07 (/tasks returns 404) | | | needs product access (audit section 5). 2026-10-02, gpt-5.6-sol (OpenAI, via Codex; `process/runs/2026-10-02-ag-kit/refute-codex.md`): unverifiable here (no source cell; help search for "task" finds no task article) |
| F-04 | The client page shows a dated history of actions | CONFIRMED | https://www.youtube.com/watch?v=MbCFF5j-LTM 29:06, "7 months ago, I ran the annuity navigator"; https://www.youtube.com/watch?v=xkSCZURJO_Y 27:50, "it has a reports timeline" | 2025-10-01 | | | partner; AG presenter | 30.09 brief fact 5 said the client feed is empty; overturned: the conversation feed is empty, the action feed is not. 2026-10-02, gpt-5.6-sol (OpenAI, via Codex; `process/runs/2026-10-02-ag-kit/refute-codex.md`): held |
| F-05 | Audio recordings and transcripts can be uploaded through AI Import when a client is created; whether they stay on the client card is not shown | CONFIRMED | https://help.annuitiesgenius.com/article/129-i-have-a-client-what-do-i-do-next, "Upload PDFs, documents, audio recordings, or transcripts" | 2026-08-20 | | | | 30.09 brief did not list it; added 01.10. 2026-10-02, gpt-5.6-sol (OpenAI, via Codex; `process/runs/2026-10-02-ag-kit/refute-codex.md`): overturned "uploaded to the client card": the article says upload for AI Import and does not say the file is kept on the card; claim narrowed to the article's words |
| F-06 | AG has calling: a dialer, click to call, a call log, call recording | ABSENT | AG's own words: https://www.youtube.com/watch?v=XZ99GqPuKuc 11:15, "right now that's not on our menu" (audit line 59) | 2020-08-04 | COV-01 (help search "dialer", "voicemail": 0 hits), COV-02 (captions, keyword "call"), COV-04, COV-05, COV-07 | | AG presenter, 2020 | held; the 2020-2023 in-app voice recorder is a separate fact (audit line 60). 2026-10-02, gpt-5.6-sol (OpenAI, via Codex; `process/runs/2026-10-02-ag-kit/refute-codex.md`): held (captions 11:44-11:48, 13:22-13:27; help search "click to call", "call log", "call recording": 0 articles) |
| F-07 | AG syncs the agent's inbox (Gmail, Outlook) and logs email on the case | ABSENT | | 2026-10-01 | COV-01, COV-02 (101 captioned videos), COV-04 (40 blog posts), COV-07 (/email, /inbox, /crm/emails return 404) | | | held (audit line 35, confidence high). 2026-10-02, gpt-5.6-sol (OpenAI, via Codex; `process/runs/2026-10-02-ag-kit/refute-codex.md`): held (help search "email sync": 0 articles; Integrations category lists no inbox integration) |
| F-08 | GrantAI sends email to the client directly | CLAIMED | https://www.youtube.com/watch?v=Vf08MHSgX9w 21:47, "you can send emails from here now... we just added that last week" | 2026-02-13 | | | AG webinar host, said, not shown on screen | open: demos of 2026-03-13 (ggDptdUPVHA 13:32) and 2026-07-23 (V9OQE47mm9w 28:49) and help 114 (2026-05-13) show only "Open in Mail". 2026-10-02, gpt-5.6-sol (OpenAI, via Codex; `process/runs/2026-10-02-ag-kit/refute-codex.md`): held as a CLAIMED statement; later demos show the manual "Open in Mail" flow |
| F-09 | Analysis, reports and notes made while a client is selected save to that client's profile on their own; quotes are not named | CONFIRMED | https://help.annuitiesgenius.com/article/25-working-with-current-client, "Any analysis, reports, or notes you create while that client is selected will automatically be saved" | 2026-04-22 (article update date, read by the refute pass) | | | | held 01.10. 2026-10-02, gpt-5.6-sol (OpenAI, via Codex; `process/runs/2026-10-02-ag-kit/refute-codex.md`): overturned "Quotes ... save": the article names analysis, reports and notes, not quotes; claim narrowed to the article's words; kit table row "Quotes" changed to match |

## Quotes

One record per quote. A quote without the speaker's role fails.

| id | text | speaker and role | where, date | weight | used in the kit as |
|---|---|---|---|---|---|
| Q-01 | "A CRM that's 60% current is worse than a spreadsheet everyone trusts." | a commenter who runs a team of 8 producers | r/InsuranceAgent, 2026-07-12; `crm-module-brief-2026-09-30.md` line 183 | low (brief thesis T09) | v5-v9: "as one agent put it"; corrected to "as one team lead put it"; the line was cut in wave 1 (E-12), not in the kit now |
| Q-02 | "after I send it, what do I do next? I guess I'll call the guy and let him know there's something cool waiting in his mailbox." | AG's CTO in the GrantAI 2.0 demo (round 1 said "most likely"; round 4 verified) | `raw/audit-youtube-captions/9MhgDE_GNXQ.txt` | high for the wording | was in how-made step one, cut in wave 1 (E-12); the email's "Open in mail" hook and side note 1 rest on it |
