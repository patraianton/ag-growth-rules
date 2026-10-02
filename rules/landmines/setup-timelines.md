---
id: setup-timelines
version: 1
changed: 2026-10-02
asked_by: Anton Patrai
strictness: remove
applies_to: [email, social, webinar, imo-note, how-made]
---

# Landmine: setup and timelines

## 1. What this landmine is

Any sentence about how long setup takes or how much work it is: "right away", "day one", "in minutes",
"nothing to set up", "not another system to set up", porting an office number, texting registration waits,
Google's review for reading Gmail, and work AG promises to do for the agent ("we file it for you").

## 2. What it is not (hand-offs)

- Whether the feature exists or what it does → `product-claims`.
- Who registers the number and in whose name, consent and STOP → `compliance-promises`.
- Which plan includes calling or texting, "live on all plans" → `pricing-plans`.
- A competitor's setup complaints ("A2P rejected or stuck for weeks" in GoHighLevel reviews) →
  `competitors-partners`, and their counts → `numbers-and-sources`.

## 3. Source of truth (resolution order; stop at the first that resolves)

1. The gatekeeper's own documentation, dated: Twilio A2P 10DLC docs for registration, the carrier or
   provider's porting docs, Google's OAuth verification policy for restricted Gmail scopes.
2. AG's help center for what is set up today (contacts and cases already in the account; one-click import
   from Redtail and Wealthbox).
3. A `decisions.md` row owned by the CTO for what ships on launch day and for any work AG does for the agent.

Never a source: the brief; a reviewer's estimate ("2-3 weeks" and "4-8 weeks" were added in round 2 and are
in neither source, per round-3.md line 9); a competitor's marketing; the model's memory.

## 4. Forbidden shapes (banned by shape)

- **F1 Time promise with no row.** "right away", "on day one", "from day one", "instantly",
  "immediately", "in 15 minutes", "starts as soon as", or a range of days or weeks. Class: invented-fact.
  Severity: major.
- **F2 Denial of setup effort.** "nothing to set up", "not another system to set up", "no setup",
  "out of the box". Brackets do not rescue it.
  Class: invented-fact. Severity: major.
- **F3 Work AG does for the agent, undecided.** "we file it for you", "AG files", "we port it for you"
  with no CTO decision row. Brackets do not rescue it: TO-CONFIRM needs an owner and a date.
  Class: invented-fact. Severity: major.

## 5. Allowed with a row

- **A1** A wait quoted from the gatekeeper's documentation, with source and date ("Twilio quotes up to
  5 business days per campaign").
- **A2** A gated statement with no time in it: "texting from the agent's own number as each one clears
  registration".
- **A3** What is already done today, CONFIRMED: "Every client you've quoted in Annuities Genius is already here."
- **A4** A time inside brackets as TO-CONFIRM, with a `decisions.md` row: `[bring your office line over]`.

## 6. Detection

**Stage 1: cues.** Format: `tools/README.md`. Run by the `time-promises` check.

```cues
# rule | target | rescues | kind  | pattern
F1     | copy   | bracket | regex | (?i)\bright away\b|\b(?:on|from) day one\b|\binstantly\b|\bimmediately\b|\bin (?:\d+|a few) minutes\b|\bstarts? as soon as\b|\b\d+\s*(?:–|-|to)\s*\d+\s+(?:business\s+)?(?:days|weeks)\b
F2     | copy   | none    | regex | (?i)\b(?:nothing|not another (?:system|tool|app|platform)|no (?:new )?(?:system|tool|app)) to (?:set up|setup|learn)\b|\bno set-?up\b|\bout of the box\b
F3     | copy   | none    | regex | (?i)\bwe(?:'ll| will)? (?:file|register|port|move) (?:it|them|your \w+) for you\b|\bAG files\b
```

**Stage 2** (`rules/README.md`, Detection) gets the passage, the facts table and `decisions.md`. It
answers: which gate this step passes (registration, porting, Google review, none), which row gives its
time, who decided AG does the work.

Final kit (`kit.md`, working tree 2026-10-01 23:41): stage 1 finds 8 lines: 31, 32 (F1), 33 (F3), 70 (F2) in
customer copy; 149 (F3) and 153 (F2) in the approach section; 180 (F1) and 181 (F3) in the "To confirm" list.

The exact lines cut for F2 are also in the killed-lines table of `templates/decisions.md` (`killed-lines`
check).

## 7. Fixtures

```fixtures
{"id": "setup-timelines/F1/01", "rule": "F1", "expect": "fire", "target": "copy", "text": "Calling starts right away.", "source": "kit.md@eb2ef9d:36 (v4, excerpt); cut by round 4 P1-2: porting takes days"}
{"id": "setup-timelines/F1/02", "rule": "F1", "expect": "fire", "target": "copy", "text": "2. Pick a local number and start calling right away - or [bring your office line over].", "source": "kit.md final (working tree 2026-10-01 23:41):32; round 4's replacement kept 'right away'; the kit calls calling 'the heaviest build' (line 180)"}
{"id": "setup-timelines/F1/03", "rule": "F1", "expect": "fire", "target": "copy", "text": "1. Connect your email once - email and meetings work right away.", "source": "kit.md final:31; reading replies needs Google's security assessment (line 171)"}
{"id": "setup-timelines/F1/04", "rule": "F1", "expect": "fire", "target": "copy", "text": "Email and meetings work from day one - connect your email once.", "source": "kit.md@fceca84:28 (v2, excerpt)"}
{"id": "setup-timelines/F1/05", "rule": "F1", "expect": "fire", "target": "copy", "text": "Watch Us Take a Client from Lead to E-App in 15 Minutes - Without Leaving Annuities Genius (Live Demo)", "source": "kit.md@eb2ef9d:87 (v4); added by round 3 F19, cut by round 4 P2-2"}
{"id": "setup-timelines/F1/06", "rule": "F1", "expect": "fire", "target": "copy", "text": "Texting needs each agent's number registered with the carriers first (10–15 business days);", "source": "kit.md@fceca84:120 (v2, excerpt); Twilio says up to 5 business days (round-3.md line 9)"}
{"id": "setup-timelines/F2/01", "rule": "F2", "expect": "fire", "target": "copy", "text": "**Nothing to set up.** Your clients and cases are already here.", "source": "kit.md@662d63b:28 (v1, excerpt); cut by round 1 F1, all six lenses"}
{"id": "setup-timelines/F2/02", "rule": "F2", "expect": "fire", "target": "copy", "text": "> Not another system to set up. The same case you already quote in - now with the email, the call, and the text on it.", "source": "kit.md final:70 (excerpt); the round 1 cut, regrown in a later script edit"}
{"id": "setup-timelines/F3/01", "rule": "F3", "expect": "fire", "target": "copy", "text": "3. Texting switches on after the one-time registration every US business texting line needs - we file it for you [typical wait: confirm].", "source": "kit.md@eb2ef9d:37 (v4); templates/decisions.md D-09 open"}
{"id": "setup-timelines/F3/02", "rule": "F3", "expect": "fire", "target": "copy", "text": "Text any client from your own number. AG files the registration. STOP handled. Every text on the case.", "source": "kit.md final:149 (how-made table, release-one column)"}
{"id": "setup-timelines/F1/n01", "rule": "F1", "expect": "no_fire", "target": "copy", "text": "Three weeks later you're rebuilding the story before you call back.", "source": "kit.md final:20 (excerpt)"}
{"id": "setup-timelines/F1/n02", "rule": "F1", "expect": "no_fire", "target": "copy", "text": "From [date], agents on Annuities Genius can email, call, and book meetings from the client's case, with texting from the agent's own number as each one clears registration.", "source": "kit.md final:122 (A2)"}
{"id": "setup-timelines/F2/n01", "rule": "F2", "expect": "no_fire", "target": "copy", "text": "**Getting started.** Every client you've quoted in Annuities Genius is already here.", "source": "kit.md final:30; CONFIRMED per crm-features-audit-2026-10-01.md line 137 (A3)"}
{"id": "setup-timelines/F3/n01", "rule": "F3", "expect": "no_fire", "target": "copy", "text": "Already on Redtail or Wealthbox? Keep them for your book - bring any contact in with one click, as you do today.", "source": "kit.md final:35"}
```
