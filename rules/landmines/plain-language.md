---
id: plain-language
version: 1
changed: 2026-10-02
asked_by: Anton Patrai
strictness: rewrite
applies_to: [email, social, webinar, imo-note, how-made]
---

# Landmine: plain language

## 1. What this landmine is
Copy that explains a feature, a price or a step with more words, or harder words, than its meaning needs. One idea per sentence.

## 2. What it is not (hand-offs)
Whether the sentence is true: the other landmines. Banned words and AG's own phrases: `rules/voice.md`.

## 3. Source of truth
Anton's instruction of 2026-10-02 and the rewrites he agreed. AG's own terms: `rules/voice.md` section 8.

## 4. Forbidden shapes
Scope: email, social, webinar, imo-note; F6 also how-made. Skipped: the email's hook (its first paragraph after the greeting) and quoted speech, which counts as one word.

- **F1 Long sentence.** More than 20 words. Was "GrantAI drafts each follow-up from the illustration you sent and your call notes, and it waits on the case for you to edit, send, or skip." → now two sentences. Class: filler. Severity: major.
- **F2 Overloaded item.** A list item or agenda row with a semicolon, two dash asides, or more than three sentences after its bold label and more than 30 words. Was the "Calls, texts, meetings: all from the case." bullet → now "**Calls, texts, meetings.** Call from your computer. Text any client [from your own number]. Send your booking link. Each call, text and meeting is saved on the case." (four short sentences, under 30 words). Class: filler. Severity: major.
- **F3 Repeated phrase.** One 3-word phrase 3 times in one item or paragraph; a changed preposition is the same phrase. Was "from the case ... on the case ... on the case" in one bullet → now once. Class: filler. Severity: minor.
- **F4 Term not explained.** A term outside AG's list and plain English, with no plain words in its sentence or the one before; an AG term in a heading with no plain words on the same line. Was "Lead to E-App" → now "from first call to signed application". Class: voice-drift. Severity: minor.
- **F5 Side-note title as shorthand.** "=", "X, not Y" with no subject, "line" for a line of the email. Was "Desk line = send, not watch." → now "Case Design: the agent sends, the desk does not watch." Class: filler. Severity: major.
- **F6 Hard section.** Flesch-Kincaid grade above 9 for the email body or the IMO note, above 11 for the how-made steps. Was the how-made steps of `048e9d8` at 11.2 → now 6.6, one fact per sentence. Class: filler. Severity: major.
- **F7 Feature with history or reason.** "until now", "as before", "because", "so that" in feature copy. Was "Text any client - until now, texting was for website leads only." → now "Text any client." and the history in a side note. Class: filler. Severity: major.

## 5. Allowed
AG's own terms in body copy; history and reasons in side notes; "So, we fixed it."; a list of short actions in one item.

## 6. Detection
Check `plain` (`tools/README.md`): the cues below select F2, F5 and F7; code counts F1, F3, F4 and F6.
`plain-ok` lists abbreviations readers know; `jargon` lists words that need plain words next to them.

```cues
# rule | target | rescues | kind  | pattern
F2     | copy   | none    | regex | ;
F2     | copy   | none    | regex | \s[-–—]\s|—
F5     | copy   | none    | regex | =
F5     | copy   | none    | regex | (?i)(?:^|[=:]\s*)(?:\w+\s+)?\w+,\s+not\s+\w+
F5     | copy   | none    | regex | (?i)(?<!office )(?<!phone )(?<!texting )\bline\b
F7     | copy   | none    | regex | (?i)\b(?:until now|until today|as before|no longer|previously|because|so that|which is why|that's why)\b|,\s+so\s+(?:you|your|they|their|the|it)\b
```

```plain-ok
AM PM PT CT ET MT US Q&A LIVE CRM IRA TX OK FAQ
```

```jargon
\bopt-?outs?\b
\bporting\b
\binbox sync\b
\bdeliverability\b
```

## 7. Fixtures

```fixtures
{"id": "plain-language/F1/01", "rule": "F1", "expect": "fire", "target": "copy", "piece": "email", "text": "- **Follow-ups that don't slip.** GrantAI drafts each follow-up from the illustration you sent and your call notes, and it waits on the case for you to edit, send, or skip.", "source": "kit.md@048e9d8:36"}
{"id": "plain-language/F1/n01", "rule": "F1", "expect": "no_fire", "target": "copy", "piece": "email", "text": "- **Follow-ups that don't slip.** GrantAI drafts each follow-up from the illustration you sent and your call notes. The draft waits on the case for you to edit, send, or skip.", "source": "kit.md working tree 2026-10-02 11:28 (plain pass under way):36"}
{"id": "plain-language/F2/01", "rule": "F2", "expect": "fire", "target": "copy", "piece": "email", "text": "- **Calls, texts, meetings: all from the case.** Call from your computer. Text any client [from your own number] - until now, texting was for website leads only. Send your booking link; the meeting and its reminder land on the case. All of it is saved on the case automatically.", "source": "kit.md@048e9d8:35"}
{"id": "plain-language/F2/n01", "rule": "F2", "expect": "no_fire", "target": "copy", "piece": "email", "text": "- **Calls, texts, meetings.** Call from your computer. Text any client [from your own number]. Send your booking link. Each call, text and meeting is saved on the case.", "source": "agreed rewrite of 048e9d8:35 (owner, 2026-10-02)"}
{"id": "plain-language/F3/01", "rule": "F3", "expect": "fire", "target": "copy", "piece": "email", "text": "- **Calls, texts, meetings: all from the case.** Call from your computer. Text any client [from your own number] - until now, texting was for website leads only. Send your booking link; the meeting and its reminder land on the case. All of it is saved on the case automatically.", "source": "kit.md@048e9d8:35"}
{"id": "plain-language/F3/n01", "rule": "F3", "expect": "no_fire", "target": "copy", "piece": "email", "text": "- **Calls, texts, meetings.** Call from your computer. Text any client [from your own number]. Send your booking link. Each call, text and meeting is saved on the case.", "source": "agreed rewrite of 048e9d8:35 (owner, 2026-10-02)"}
{"id": "plain-language/F4/01", "rule": "F4", "expect": "fire", "target": "copy", "piece": "webinar", "text": "**Watch Us Take a Client from Lead to E-App - Without Leaving Annuities Genius (Live Demo)**", "source": "kit.md@048e9d8:104"}
{"id": "plain-language/F4/n01", "rule": "F4", "expect": "no_fire", "target": "copy", "piece": "webinar", "text": "**Live demo: one client, from first call to signed application, without leaving Annuities Genius**", "source": "agreed rewrite of 048e9d8:104 (owner, 2026-10-02)"}
{"id": "plain-language/F5/01", "rule": "F5", "expect": "fire", "target": "copy", "piece": "email", "text": "**Side notes: why it reads this way**\n4. **Desk line = send, not watch.** Request Case Design already exists; attaching the conversation to it is the new part.", "source": "kit.md@048e9d8:62,66"}
{"id": "plain-language/F5/n01", "rule": "F5", "expect": "no_fire", "target": "copy", "piece": "email", "text": "**Side notes: why it reads this way**\n4. **Case Design: the agent sends, the desk does not watch.** Request Case Design already exists in AG. New: the agent picks which emails and call notes go with the request. The desk sees only what the agent sent.", "source": "agreed rewrite of 048e9d8:66 (owner, 2026-10-02)"}
{"id": "plain-language/F6/01", "rule": "F6", "expect": "fire", "target": "copy", "piece": "how-made", "text": "The rules, the checker and the record of this run: [github.com/patraianton/ag-growth-rules](https://github.com/patraianton/ag-growth-rules)\n\n1. I went through AG's public record: all 93 help-center articles, the 103 videos and the Shorts on AG's channel (searched by their captions), 166 site pages, 65 snapshots of the pricing page since 2019, 54 posts by the company, its founder, and its CTO: [crm-audit.html](https://patraianton.github.io/annuities-genius-crm-launch-kit/crm-audit.html)\n2. I read 3,803 public records about GoHighLevel, a CRM sold to insurance agents under other brand names, and sorted 1,927 complaints by module (counts are close, not exact: two research passes read the same review sites): [ghl-complaints.html](https://patraianton.github.io/annuities-genius-crm-launch-kit/ghl-complaints.html)\n3. The agent portrait is built from 155 Reddit threads, about 60 insurance-forum threads, 769 Indeed reviews, and 98 IMO sites ([numbers.json](https://github.com/patraianton/ag-growth-rules/blob/HEAD/templates/numbers.json)); AG's voice, from its own launches: [voice.md](https://github.com/patraianton/ag-growth-rules/blob/HEAD/rules/voice.md)\n4. Research and writing agents I run wrote it, September 30 to October 2. Four review rounds ran on the night of September 30, each by six simulated reader roles from one model family; the text changed after them, and the checker (step 5) is what checked this version. No annuity agent has read it: [misses.md](https://github.com/patraianton/ag-growth-rules/blob/HEAD/process/misses.md)\n5. The checker gave 189 findings on the October 1 version of this kit and none on this one: [run report](https://github.com/patraianton/ag-growth-rules/blob/HEAD/process/runs/2026-10-02-ag-kit/README.md)\n6. An agent on another model family (OpenAI's) tried to overturn the nine product facts: six held, two were overturned and narrowed to what their source shows, one could not be checked from public pages: [facts.md](https://github.com/patraianton/ag-growth-rules/blob/HEAD/templates/facts.md)", "source": "kit.md@048e9d8:9-16, the how-made steps"}
{"id": "plain-language/F6/n01", "rule": "F6", "expect": "no_fire", "target": "copy", "piece": "how-made", "text": "1. I went through AG's public record: all 93 help-center articles and 166 site pages. I searched the 103 videos and the Shorts on AG's channel by their captions. I added 65 pricing-page snapshots since 2019 and 54 posts by AG, its founder and CTO: [crm-audit.html](https://patraianton.github.io/annuities-genius-crm-launch-kit/crm-audit.html)\n2. I read 3,803 public records about GoHighLevel, a CRM sold to insurance agents under other brand names. I sorted 1,927 complaints by product area. The counts are close, not exact, because two research passes read the same review sites: [ghl-complaints.html](https://patraianton.github.io/annuities-genius-crm-launch-kit/ghl-complaints.html)\n3. Agent portrait sources: 155 Reddit threads, about 60 insurance-forum threads, 769 Indeed reviews and 98 IMO sites ([numbers.json](https://github.com/patraianton/ag-growth-rules/blob/HEAD/templates/numbers.json)). AG's voice comes from its own launches: [voice.md](https://github.com/patraianton/ag-growth-rules/blob/HEAD/rules/voice.md)\n4. AI agents I run did the research and wrote it, September 30 to October 2. Six simulated readers from one AI model family reviewed an earlier text in four rounds, the night of September 30. Since then, only the checker (step 5) has checked this version, and no annuity agent has read it: [misses.md](https://github.com/patraianton/ag-growth-rules/blob/HEAD/process/misses.md)\n5. The checker gave 189 findings on the October 1 version of this kit and none on this one: [run report](https://github.com/patraianton/ag-growth-rules/blob/HEAD/process/runs/2026-10-02-ag-kit/README.md)\n6. An agent on another AI model family (OpenAI's) tried to overturn the nine product facts. Six held, and one could not be checked from public pages. Two were overturned and narrowed to what their source shows: [facts.md](https://github.com/patraianton/ag-growth-rules/blob/HEAD/templates/facts.md)", "source": "kit.md working tree 2026-10-02 11:28 (plain pass under way):11-16"}
{"id": "plain-language/F7/01", "rule": "F7", "expect": "fire", "target": "copy", "piece": "email", "text": "Text any client [from your own number] - until now, texting was for website leads only.", "source": "kit.md@048e9d8:35 (excerpt)"}
{"id": "plain-language/F7/n01", "rule": "F7", "expect": "no_fire", "target": "copy", "piece": "email", "text": "**Side notes: why it reads this way**\n3. **Texting before this launch.** Until now, texting was for website leads only.", "source": "kit.md working tree 2026-10-02 11:28 (plain pass under way):65; the history moved to a side note"}
```
