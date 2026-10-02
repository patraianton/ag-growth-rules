---
landmine: setup-timelines
rule: F1
verdict: rewrite
slop_class: invented-fact
severity: major
piece: email
source: kit.md@eb2ef9d:36
verdict_by: panel round 4, fact-checker, voice-editor, agent-reader
verdict_ref: panel/round-4.md P1-2
date: 2026-09-30
---

## Passage (verbatim, as it stood in that version)

> 2. Keep the number your clients know: bring your office line over, or pick a new local number [confirm]. Calling starts right away.

## Why

Round 4, P1-2: "'Calling starts right away' is false for the first option. Moving an existing US number
takes days to weeks. A CTO who has built telephony will catch this in one line."

## If rewrite: the replacement

> 2. Pick a local number and start calling right away - or [bring your office line over].

Applied in v5 (git 816d805, kit.md line 34; final kit line 32). `[bring your office line over]` is
TO-CONFIRM, with porting time open (`templates/decisions.md` D-04).

## What the rewrite did not fix

The rewrite bracketed the false option and left "start calling right away" unbracketed. AG has no telephony
today (`templates/facts.md` F-06, ABSENT); the kit's own To confirm list says "Calling on day one is the
heaviest build in this kit" (kit.md line 180), and the 01.10 audit (section 4, item 5) flagged "on day one"
for calls as the heaviest promise. A rewrite that cuts one false clause is checked again as a new passage.
