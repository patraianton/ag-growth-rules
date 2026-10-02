---
id: product-claims
version: 1
changed: 2026-10-02
asked_by: Anton Patrai
strictness: cite-or-cut
applies_to: [email, social, webinar, imo-note, how-made]
---

# Landmine: product claims

## 1. What this landmine is

Any sentence that says what Annuities Genius (AG) does: a feature name, a tab, a button, a menu path,
what is saved where, what syncs, what is sent from which address or number, what happens after a click.

## 2. What it is not (hand-offs)

- "AG has no X", or a feature that exists announced as new (F3) → `research-absence`.
- Which plan has the feature, "every plan", "all plans", trial length → `pricing-plans`.
- How long setup takes, "right away", "nothing to set up", "we file it for you" → `setup-timelines`.
- Consent, STOP, call recording, data use, retention, export, sharing → `compliance-promises`.
- What Redtail, Wealthbox, GoHighLevel, FireLight or an IMO's tools do → `competitors-partners`.
- Counts of articles, videos, posts → `numbers-and-sources`. "I checked every source" → `process-claims`.

## 3. Source of truth (resolution order; stop at the first that resolves)

1. AG help center (`help.annuitiesgenius.com`): article number and its updated date.
2. AG's YouTube channel: video id, timestamp, caption text. Shown on screen is CONFIRMED; only said aloud
   is CLAIMED.
3. The product itself: a trial account, a dated screenshot.
4. AG blog and press releases, dated.
5. Founder and CTO posts, dated. Words without a screen are CLAIMED.

When sources disagree, a later dated showing beats an earlier spoken claim, and the row says so.
Example: direct email send from GrantAI was announced on 2026-02-13 ("you can send emails from here now"),
while the 2026-03-13 and 2026-07-23 demos and help article 114 (2026-05-13) show only "Open in Mail".
The row is CLAIMED and the copy may not state it as fact.

Never a source: the brief or the test task text; a competitor's feature; the model's memory of the product;
an earlier version of the kit; a reviewer's replacement text.

A new-release feature is never CONFIRMED: in copy it is A2 or A3.

## 4. Forbidden shapes (banned by shape)

- **F1 Product detail with no row.** An unbracketed feature name, tab, menu path, sending identity or
  post-click behaviour with no CONFIRMED row in the facts table. Cues: a menu path ending in a bare name
  (`→ Case → **Conversation**`), `<Name> tab`, `from your own address`, `from your own number`,
  `from the agent's own number`, `replies land`, `prefilled and submitted`. Class: invented-fact.
  Severity: major.
- **F2 CONFIRMED with no date.** A facts-table row labelled CONFIRMED with no date. Cue: a facts row
  containing `CONFIRMED` and no `YYYY-MM-DD`. Class: invented-fact. Severity: major.

## 5. Allowed with a row

- **A1** SOURCED: a claim with a CONFIRMED row (URL and date) in `facts.md`. Example from the final kit:
  "E-App prefilled (FireLight, where your IMO has it switched on)" matches help article 32 (2026-07-24)
  and the 2026-09-03 Start E-App post.
- **A2** PROPOSAL: a new-release name or behaviour in square brackets (`[Client Conversations]`), listed in
  `claims.csv` with status PROPOSAL.
- **A3** TO-CONFIRM: a bracketed mechanism (`[replies land next to it]`) with a `decisions.md` row naming
  the owner (CTO for product mechanics) and a date.

## 6. Detection

**Stage 1: cues.** Cue format, unit of text (one visible line; a dotted span reads as `[…]`) and rescues:
`tools/README.md`.

```cues
# rule | target | rescues | kind  | pattern
F1     | copy   | bracket | regex | →\s*\*{0,2}(?!\[)[A-Z][A-Za-z ]*[a-z]\*{0,2}\s*[.,;:]
F1     | copy   | bracket | regex | \b(?:[A-Z][A-Za-z]+ )+tab\b
F1     | copy   | bracket | regex | (?i)\bfrom (?:your|the agent's|their) own (?:address|email|number|line|phone)\b
F1     | copy   | bracket | regex | (?i)\breplies (?:land|show up|appear)\b
F1     | copy   | bracket | regex | (?i)\bprefilled and submitted\b
F2     | facts  | none    | regex | ^(?!.*\b20\d\d-\d\d-\d\d\b).*\|\s*CONFIRMED\s*\|
```

**Stage 2** (`rules/README.md`, Detection) gets the passage and the facts table, not the draft or the
brief. It answers: which row supports this, what label, what date.

Final kit (`kit.md`, working tree 2026-10-01 23:41): stage 1 finds 7 unrescued F1 lines: 24 ("from your own
address", the only one that is a fixture), 33 and 122 (an unbracketed "own number" in the email's step 3 and
in the IMO note), 142, 147 and 149 (the approach section restating the proposal) and 171 (the "To confirm"
list). Stage 2 decides them.

## 7. Fixtures

```fixtures
{"id": "product-claims/F1/01", "rule": "F1", "expect": "fire", "target": "copy", "text": "**Where to find it:** open any client → Case → **Conversation**.", "source": "kit.md@662d63b:32 (v1); cut by panel round 1 (round-1.md line 47)"}
{"id": "product-claims/F1/02", "rule": "F1", "expect": "fire", "target": "copy", "text": "Attach a 20-second screen recording of the Conversation tab.", "source": "kit.md@662d63b:48 (v1)"}
{"id": "product-claims/F1/03", "rule": "F1", "expect": "fire", "target": "copy", "text": "Meet the Conversation tab: email, calls, texts and meetings on one case", "source": "kit.md@662d63b:77 (v1, webinar row 0:05)"}
{"id": "product-claims/F1/04", "rule": "F1", "expect": "fire", "target": "copy", "text": "from Annuities Genius, from your own address.", "source": "kit.md@662d63b:22 (v1, excerpt); round-1.md line 51 asked for a bracket"}
{"id": "product-claims/F1/05", "rule": "F1", "expect": "fire", "target": "copy", "text": "Replies land on the client's profile.", "source": "kit.md@662d63b:22 (v1); cut by round 2 F2: needs inbox sync"}
{"id": "product-claims/F1/06", "rule": "F1", "expect": "fire", "target": "copy", "text": "Meeting booked, notes captured, e-app prefilled and submitted", "source": "kit.md@662d63b:80 (v1, excerpt); AG does not track status after submission (help article 32)"}
{"id": "product-claims/F1/07", "rule": "F1", "expect": "fire", "target": "copy", "text": "Send the report and the follow-up from your own address.", "source": "kit.md final (working tree 2026-10-01 23:41):24; bracket asked in round 1, dropped by round 3; direct send is CLAIMED (crm-features-audit-2026-10-01.md line 51)"}
{"id": "product-claims/F2/01", "rule": "F2", "expect": "fire", "target": "facts", "text": "| 5 | Everything created under a selected client saves to the profile; the activity timeline exists per employee only, empty for the client | help article 25, 112 | CONFIRMED |", "source": "crm-module-brief-2026-09-30.md:62, translated; graded В (top grade) with no date; wrong per crm-features-audit-2026-10-01.md line 97"}
{"id": "product-claims/F1/n01", "rule": "F1", "expect": "no_fire", "target": "copy", "text": "**Where to find it:** open any client → Case → **[Client Conversations]**.", "source": "kit.md final:44"}
{"id": "product-claims/F1/n02", "rule": "F1", "expect": "no_fire", "target": "copy", "text": "Text any client - not only website leads - [from your own number].", "source": "kit.md final:25 (excerpt)"}
{"id": "product-claims/F1/n03", "rule": "F1", "expect": "no_fire", "target": "copy", "text": "Every email is saved on the case, and [replies land next to it].", "source": "kit.md final:24 (excerpt)"}
{"id": "product-claims/F1/n04", "rule": "F1", "expect": "no_fire", "target": "copy", "text": "Meeting booked → notes on the case → E-App prefilled (FireLight, where your IMO has it switched on)", "source": "kit.md final:100; CONFIRMED per crm-features-audit-2026-10-01.md line 137"}
{"id": "product-claims/F2/n01", "rule": "F2", "expect": "no_fire", "target": "facts", "text": "| Calendly button on the agent's website, Prime+ and Pro only | annuitiesgenius.com/blog/how-to-integrate-calendly-with-annuities-genius | 2024-08-13 | CONFIRMED |", "source": "crm-features-audit-2026-10-01.md:76, reformatted as a facts row"}
```
