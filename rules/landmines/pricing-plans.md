---
id: pricing-plans
version: 1
changed: 2026-10-02
asked_by: Anton Patrai
strictness: cite-or-cut
applies_to: [email, social, webinar, imo-note, how-made]
---

# Landmine: pricing and plans

## 1. What this landmine is

Any sentence about plan names (Starter, Prime+, Genius, Enterprise; earlier Scale and Growth), prices,
credits and what they buy, what a plan includes, "every plan" or "all plans", trial length, and launch offers
("next month is on us").

## 2. What it is not (hand-offs)

- What the feature does → `product-claims`. When it switches on → `setup-timelines`.
- Promises about data, consent or recording, even when tied to a plan → `compliance-promises`.
- A competitor's price (GoHighLevel, Agent CRM) → `competitors-partners`.
- "Billing is the second most frequent complaint" → `numbers-and-sources`.

## 3. Source of truth (resolution order; stop at the first that resolves)

1. The live pricing page, `annuitiesgenius.com/pricing`, with the date it was opened.
2. Web archive snapshots of that page (`web.archive.org`), with the snapshot date, for any claim about the
   past. The 2026-10-01 audit read all 65.
3. Help article 124 for credit costs. When it disagrees with the pricing page, the pricing page wins and the
   row records the conflict (article 124 prints "Genius $2,990/year $209/month"; 2,990 / 12 is 249;
   `crm-features-audit-2026-10-01.md` line 86).
4. A `decisions.md` row owned by the founder for any new price, plan placement, trial or offer.

Each row has an "applies to" column: personal plans carry a 14-day trial, Enterprise 30 days
(crm-features-audit-2026-10-01.md line 137).

Never a source: a partner's words on a webinar ("about 250 a month for the Cadillac" is CLAIMED);
a forum post; the brief; a competitor's pricing; the model's memory of AG's prices.

## 4. Forbidden shapes (banned by shape)

- **F1 Plan coverage stated as fact.** "all plans", "every plan", "included in your plan" with no
  pricing-page row and no founder decision. Cues: `all plans`, `every plan`, `on every plan`,
  `included in your plan`. Class: invented-fact. Severity: major.
- **F2 Trial or offer for the wrong audience.** A trial length or offer put in front of an audience whose
  plan has a different one. Cues:
  `14-day trial`, `14-day free trial`, `30-day trial`. Class: invented-fact. Severity: minor.

No shape yet for an undated price or credit amount: every price in the kit is a placeholder such as `$X`.
Add one when a real violation appears.

## 5. Allowed with a row

- **A1** SOURCED: plan, price, credit or trial with a pricing-page or archive row, its date and its audience.
- **A2** PROPOSAL: a plan placement in brackets, ours, listed in `claims.csv`
  (`[Email and meetings come with every plan.]`).
- **A3** A question to the team about plans ("every plan, or Prime+ and up?"), with the dated history it rests on.

## 6. Detection

**Stage 1: cues.** Format and rescues: `tools/README.md`. F2 has no stage-1 rescue: the audience is only
visible in the facts row.

```cues
# rule | target | rescues                  | kind  | pattern
F1     | copy   | bracket,proposal,question | regex | (?i)\b(?:all|every) plans?\b|\bincluded in (?:your|every|all) plans?\b
F2     | copy   | none                     | regex | (?i)\b\d+[- ]day (?:free )?trial\b
```

**Stage 2** (`rules/README.md`, Detection) gets the passage, the pricing rows of the facts table (with
dates and the "applies to" column) and `decisions.md`. It answers: which row, which date, which audience,
and does the audience of this piece match.

Final kit (`kit.md`, working tree 2026-10-01 23:41): stage 1 finds 1 line, 102 (F2). Lines 40, 162 and 182
say "every plan" and are rescued: a bracket, a question, a question marked as proposal.

## 7. Fixtures

```fixtures
{"id": "pricing-plans/F1/01", "rule": "F1", "expect": "fire", "target": "copy", "text": "Live on all plans from [date]; calling and texting switch on as your number is verified [plan/rollout detail].", "source": "kit.md@662d63b:32 (v1, excerpt); round 1 asked for 'Available on [plans]' (round-1.md line 48)"}
{"id": "pricing-plans/F1/02", "rule": "F1", "expect": "fire", "target": "copy", "text": "Live on every plan from [date].", "source": "kit.md@eb2ef9d:47 (v4, excerpt); cut by round 4 P1-4: contradicts the IMO note"}
{"id": "pricing-plans/F2/01", "rule": "F2", "expect": "fire", "target": "copy", "text": "Plans, [attendee offer], 14-day free trial, next Wednesday's masterclass", "source": "kit.md final (working tree 2026-10-01 23:41):102, webinar row 0:22; the same page invites IMO desks (line 109), whose Enterprise trial is 30 days"}
{"id": "pricing-plans/F1/n01", "rule": "F1", "expect": "no_fire", "target": "copy", "text": "- [Email and meetings come with every plan.] Calls and texts: [N minutes and N texts a month included, then $X a minute and $Y a text].", "source": "kit.md final:40; PROPOSAL in brackets (A2)"}
{"id": "pricing-plans/F1/n02", "rule": "F1", "expect": "no_fire", "target": "copy", "text": "- Pricing: email and meetings in every plan; calls and texts with N minutes and N texts included, then per minute and per text. My proposal, not AG's price list. In 2023-2025 in-platform texting sat on Scale and Growth only, and Client Management left Starter in June 2026: every plan, or Prime+ and up?", "source": "kit.md final:182; marked as proposal and asked as a question (A2, A3)"}
{"id": "pricing-plans/F2/n01", "rule": "F2", "expect": "no_fire", "target": "copy", "text": "if webinar-to-trial doesn't move, the promise isn't ready.", "source": "kit.md final:159 (excerpt)"}
```
