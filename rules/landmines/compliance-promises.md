---
id: compliance-promises
version: 1
changed: 2026-10-02
asked_by: Anton Patrai
strictness: remove
applies_to: [email, social, webinar, imo-note, how-made]
---

# Landmine: compliance promises

## 1. What this landmine is

Any sentence that promises how AG handles a legal or trust question: consent to text (TCPA), STOP and
opt-out handling, 10DLC registration (who registers, in whose name), call recording (default, who sets the
rule, notice), use or sale of client data, retention, export and off-boarding, sharing with carriers, other
agencies or AI providers, audit trails. Also any sentence that says what the law requires of agents.

Only AG's CTO, founder or compliance lead, by name, closes one of these.

## 2. What it is not (hand-offs)

- What the product does with no legal weight (a tab, a path, where a note is saved) → `product-claims`.
- How long registration or porting takes, "we file it for you" → `setup-timelines`.
- What calls and texts cost, which plan has them → `pricing-plans`.
- What a competitor promises its users → `competitors-partners`.
- A count of complaints about data lock-in → `numbers-and-sources`.

## 3. Source of truth (resolution order; stop at the first that resolves)

1. AG's own published policy: privacy policy, license terms, help article, with URL, date and scope.
   AG's privacy policy says "We do not send marketing text messages"; that covers messages AG sends its
   own users, not texts agents would send from a future CRM.
2. A `decisions.md` row: the question, the decided wording, the owner by name, the date.
3. For what the law requires: the statute or regulation text, with the population it binds.
   FINRA rules bind broker-dealer representatives; most annuity agents are insurance-licensed only.

Never a source: the brief; a competitor's practice (GoHighLevel, Integrity); the model's summary of the law;
a reviewer's replacement text; an earlier version; the kit's own "To confirm" list (questions, not decisions).

## 4. Forbidden shapes (banned by shape)

- **F1 Promise with no decision row.** A promise on a compliance topic in customer copy with no
  `decisions.md` row (owner and date). Brackets do not rescue it: a bracketed promise is TO-CONFIRM and
  still needs the row. Cues: `opted in`, `said yes`, `STOP reply`, `call recording is`, `recording is off`,
  `never sold`, `never shared`, `never used`, `export any time`, `nothing is held back`,
  `takes it all with you`, `kept on the case`, `registered in the agent's own name`, `audit trail`,
  `compliant`, `compliance is covered`. Class: invented-fact. Severity: critical.
- **F2 Two rules for one topic.** Two different rules or statuses for one topic across pieces. Cues: the same topic (recording, consent, export, retention, data use) matched in two or more
  pieces with different text. Class: contradiction. Severity: critical.
- **F3 Legal duty without its population.** Cues: `agents must keep`, `you must retain`,
  `advisors are required to archive`. Class: invented-fact. Severity: major.

## 5. Allowed with a row

- **A1** A promise whose wording matches a `decisions.md` row verbatim, with owner (CTO, founder or
  compliance) and date. The copy may drop the bracket once the row exists.
- **A2** AG's current published policy, quoted, dated, with its scope.
- **A3** A pointer with no promise: "your firm's policies still apply".
- **A4** A topic named as a question for the live Q&A, with no answer in the copy.

## 6. Detection

**Stage 1: cues.** Format: `tools/README.md`. F2 (`kind: topic`) fires when two pieces carry different
text for one topic after brackets and case are removed.

```cues
# rule | target | rescues | kind  | pattern
F1     | copy   | none    | regex | (?i)\b(?:opted[ -]in|said yes|STOP (?:reply|message)|reply STOP|call recording (?:is|stays|follows)|recording is (?:off|on)|never (?:sold|shared|used)|exports? (?:any ?time|everything)|nothing is held back|takes it all with you|kept on the case|registered in (?:the agent's|your) own name|audit trail|compliant|compliance is covered)\b
F2     | copy   | none    | topic | recording=(?i)\bcall recording\b|\brecording (?:is|stays|follows)\b
F2     | copy   | none    | topic | consent=(?i)\bopted[ -]in\b|\bsaid yes\b|\bconsent\b
F2     | copy   | none    | topic | export=(?i)\bexports? (?:any ?time|everything)\b|\bnothing is held back\b
F2     | copy   | none    | topic | data-use=(?i)\bnever (?:sold|shared|used)\b
F3     | copy   | none    | regex | (?i)\b(?:agents?|advisors?|producers?|you) (?:must|are required to|have to|need to) (?:keep|retain|store|archive)\b
```

**Stage 2** (`rules/README.md`, Detection) gets the passage, the facts table and `decisions.md`. It
answers: which decision row, which owner, which date; for F2, which of the two rules the row supports.

Final kit (`kit.md`, working tree 2026-10-01 23:41): stage 1 finds 13 lines: 5 in customer copy (38, 39, 41,
42, 129), 2 in the approach section (148, 153) and 6 in the "To confirm" list. No row of
`templates/decisions.md` (seeded from the kit) has an owner or a date, so no hit can be cleared.

## 7. Fixtures

```fixtures
{"id": "compliance-promises/F1/01", "rule": "F1", "expect": "fire", "target": "copy", "text": "The audit trail writes itself.", "source": "kit.md@662d63b:25 and :57 (v1); cut by round 1 F2, all six lenses"}
{"id": "compliance-promises/F1/02", "rule": "F1", "expect": "fire", "target": "copy", "text": "- [Texts go only to clients who've said yes, and a STOP reply ends texting to them automatically.]", "source": "kit.md final (working tree 2026-10-01 23:41):38; bracketed, no owner (round-4.md A4; templates/decisions.md D-07 open)"}
{"id": "compliance-promises/F1/03", "rule": "F1", "expect": "fire", "target": "copy", "text": "- [Your clients, messages, and recordings export any time; nothing is held back if you leave.]", "source": "kit.md final:42; cut by round 4 P1-3, re-added by apply-v8.py on 2026-10-01 with no recorded decision (templates/decisions.md D-10)"}
{"id": "compliance-promises/F1/04", "rule": "F1", "expect": "fire", "target": "copy", "text": "For your compliance team: texts go only to clients who've opted in, [from a number registered in the agent's own name]; a STOP reply ends texting on its own;", "source": "kit.md final:129 (excerpt); 'opted in' is unbracketed here and bracketed in the email"}
{"id": "compliance-promises/F1/05", "rule": "F1", "expect": "fire", "target": "copy", "text": "If you ever leave, one export takes it all with you [confirm].", "source": "kit.md@eb2ef9d:45 (v4, excerpt); cut by round 4 P1-3"}
{"id": "compliance-promises/F2/01", "rule": "F2", "expect": "fire", "target": "copy", "texts": [{"piece": "email", "text": "- [Call recording is off unless you turn it on.]"}, {"piece": "imo-note", "text": "[call recording follows the rule your agency sets]; [every message is kept on the case]."}], "source": "kit.md final:39 and :129; two control models for one switch (templates/decisions.md D-08 open)"}
{"id": "compliance-promises/F3/01", "rule": "F3", "expect": "fire", "target": "copy", "text": "outbound shows \"Spam Likely\"; insurance agents must keep recordings for years.", "source": "kit.md final:148 (excerpt); the cited FINRA rules bind broker-dealer reps, not insurance-only agents (crm-module-brief-2026-09-30.md line 33)"}
{"id": "compliance-promises/F1/n01", "rule": "F1", "expect": "no_fire", "target": "copy", "text": "Can't make it live? Register anyway to get the recording.", "source": "kit.md final:87"}
{"id": "compliance-promises/F1/n02", "rule": "F1", "expect": "no_fire", "target": "copy", "text": "Live Q&A (7 min): texting rules, your data and what happens if you leave, and your questions", "source": "kit.md final:103 (webinar row 0:23); topics named, no promise (A4)"}
{"id": "compliance-promises/F2/n01", "rule": "F2", "expect": "no_fire", "target": "copy", "texts": [{"piece": "email", "text": "- [Call recording is off unless you turn it on.]"}, {"piece": "webinar", "text": "Can't make it live? Register anyway to get the recording."}], "source": "kit.md final:39 and :87; the topic matches in one piece only"}
{"id": "compliance-promises/F3/n01", "rule": "F3", "expect": "no_fire", "target": "copy", "text": "Nothing changes in the tools you give your agents today.", "source": "kit.md final:127 (excerpt)"}
```
