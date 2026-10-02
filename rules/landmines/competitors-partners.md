---
id: competitors-partners
version: 1
changed: 2026-10-02
asked_by: Anton Patrai
strictness: remove
applies_to: [email, social, webinar, imo-note, how-made]
---

# Landmine: competitors, IMOs, integration partners, carriers

## 1. What this landmine is

Any line that names or implies another company the reader works with: a competitor (GoHighLevel and its
white labels: Agent CRM, Quility's Switchboard, LeadConnector), the reader's IMO and the CRM it hands out
(IntegrityCONNECT, BOSS4AGENTS, Tevah), an integration partner (Redtail, Wealthbox, FireLight/Hexure,
SmartOffice), or a carrier.

Strictness `remove`. Positioning against a partner is never kept on a citation alone.

## 2. What it is not (hand-offs)

- AG's own product depth ("calls from the case") → `product-claims`.
- What data AG shares with carriers or IMOs ("never shared with carriers") → `compliance-promises`.
- Plan and price lines for IMO Enterprise accounts → `pricing-plans`.
- Counts about a competitor ("1,927 complaints", "third-largest complaint") → `numbers-and-sources`.
- "AG has no X" set against a competitor → `research-absence` for the ABSENT; this file owns the frame.
- The bare competitor name cue → `rules/voice.md` VN1.

## 3. Source of truth (resolution order; stop at the first that resolves)

1. `rules/voice.md` VN1: AG names no competitor in launch copy (GoHighLevel: 0 mentions on AG's site).
2. A CONFIRMED row in `templates/facts.md` from AG's integration help article or the partner's own
   documentation, with URL and date. It sets the depth: the Redtail import is one-way, 9 fields in, nothing
   back (panel `round-1.md` line 39), and Redtail has a support article only (2023-10-23,
   `crm-features-audit-2026-10-01.md` line 133); Wealthbox has an integration page and a "Send to" menu
   (https://help.wealthbox.com/hc/en-us/articles/29980390642331, 2025-08-27, audit line 110); FireLight is
   switched on at the IMO level (AG help article 32, 2026-07-24, audit line 40).
3. A `templates/decisions.md` row closed by AG (founder or CTO) on how AG positions an IMO or a partner.
   Agents prepare the row; they do not close it.

Never a source: a partner logo strip ("Works with tools you already use"), AG comparison pages, a reviewer
persona ("22-year Texas agent on Redtail"), reviewer replacement text, the brief's internal wording.

## 4. Forbidden shapes (banned by shape)

- **F1 Competitor framing.** A competitor named in email, social, webinar or imo-note (cue: VN1), or the
  "kill" or "replace" framing on any page that may be public: "kill X", "replace your CRM". In
  how-made, naming GoHighLevel as a research subject is allowed (A4). Class: voice-drift. Severity: major.
- **F2 "Leave your IMO's tools".** A line telling an IMO-sourced agent to stop using or route around the
  IMO's CRM, or giving the IMO desk blanket sight of every agent's conversations. Class: invented-fact.
  Severity: critical. Cues: `leave your IMO`, `switch from your IMO`, `every agent's emails`, `your marketers`.
- **F3 Integration deeper than the facts row.** "Book of record", "two-way", "posts back", "both list AG in
  their catalogs" over a one-way import or a support article. Class: invented-fact. Severity: major.
- **F4 "One place" next to a kept partner.** "No jumping between systems", "one place for every client
  conversation" in a kit that also says "keep Redtail". The phrase is AG's own (`voice.md`); the voice
  allowance does not clear a contradiction. Class: contradiction. Severity: major.
- **F5 "Carriers" for phone companies.** To an annuity agent a carrier is an insurer; texting registration
  is with phone companies (panel round-2 F3). Class: voice-drift. Severity: minor.

## 5. Allowed with a row

- **A1** "Already on Redtail or Wealthbox? Keep them for your book", with the import at the facts-row depth.
- **A2** "Your IMO's desk sees more": the desk gets what the agent sends with a Case Design request.
- **A3** "Nothing changes in the tools [IMO name] gives you."
- **A4** In how-made only: GoHighLevel named as a research subject, white labels named as findings.
- **A5** FireLight named with its condition ("where your IMO has it switched on").

## 6. Detection

**Stage 1.** Cue format as in `product-claims.md`. F1 and F2 are never rescued.

```cues
# rule | target | rescues | kind  | pattern
F1     | copy   | none    | regex | (?i)\bkill(?:s|ing)?\b.{0,30}\b(?:go)?high ?level\b
F1     | copy   | none    | regex | (?i)\breplace (?:your|their) (?:crm|imo)\b
F2     | copy   | none    | regex | (?i)\b(?:leave|ditch|drop|switch from|instead of) (?:your )?imo\b
F2     | copy   | none    | regex | (?i)\bevery agent's (?:emails?|calls?|texts?)\b
F2     | copy   | none    | regex | (?i)\byour marketers\b
F3     | copy   | bracket | regex | (?i)\bbook of record\b
F3     | copy   | bracket | regex | (?i)\b(?:two-way|bi-?directional) (?:sync|integration)\b
F3     | copy   | bracket | regex | (?i)\bposts? back to\b
F3     | copy   | bracket | regex | (?i)\bboth list AG\b
F4     | copy   | bracket | regex | (?i)\bno (?:jumping|switching) between systems\b
F4     | copy   | bracket | regex | (?i)\bone place for every\b
F5     | copy   | bracket | regex | (?i)\bregistered with the carriers\b
F5     | copy   | bracket | regex | (?i)\bcarrier (?:approval|registration)\b
```

**Stage 2** (`rules/README.md`) gets the passage, the piece name and the `facts.md` rows for the named
company. It answers: is the company named in a piece that allows it, and does the line stay at the depth
of its row.

## 7. Fixtures

`must_fire` rows are real lines from the kit's git history (`kit.md@<commit>:<line>` in the author's private
repository). `must_not_fire` rows are real lines of the final kit (working tree 2026-10-01 23:41).

```fixtures
{"id": "competitors-partners/F3/01", "rule": "F3", "expect": "fire", "target": "copy", "text": "Your clients and cases are already here. Keep Redtail or Wealthbox as your book of record", "source": "kit.md@662d63b:28 (v1, excerpt); round-1.md line 39: the import is one-way, 9 fields in, nothing back"}
{"id": "competitors-partners/F3/02", "rule": "F3", "expect": "fire", "target": "copy", "text": "> Nothing to set up. Your clients are already here. Redtail and Wealthbox stay your book of record.", "source": "kit.md@662d63b:59 (v1, social post)"}
{"id": "competitors-partners/F3/03", "rule": "F3", "expect": "fire", "target": "copy", "text": "Day to day, annuity agents lose the thread in the inbox, a spreadsheet, Redtail or Wealthbox (both list AG in their catalogs)", "source": "kit.md@816d805:144 (v5, excerpt); crm-features-audit-2026-10-01.md section 4 item 10: Redtail has a support article only"}
{"id": "competitors-partners/F2/01", "rule": "F2", "expect": "fire", "target": "copy", "text": "**Run a team or a case-design desk?** Every agent's emails, calls and texts land on the shared case, so your marketers see the full story without the email thread.", "source": "kit.md@662d63b:30 (v1); round-1.md F4: blanket visibility scares IMO-sourced agents"}
{"id": "competitors-partners/F4/01", "rule": "F4", "expect": "fire", "target": "copy", "text": "> No jumping between systems. One place for every client conversation, from first call to e-app. Already on Redtail or Wealthbox? Keep them.", "source": "kit.md@fceca84:63 (v2, social post); round-2.md line 119"}
{"id": "competitors-partners/F5/01", "rule": "F5", "expect": "fire", "target": "copy", "text": "Texting needs each agent's number registered with the carriers first (10–15 business days); today's Redtail and Wealthbox links are one-way imports.", "source": "kit.md@fceca84:120 (v2, excerpt); round-2.md F3"}
{"id": "competitors-partners/F1/01", "rule": "F1", "expect": "fire", "target": "copy", "text": "**Deliberately left out.** \"Kill / replace GoHighLevel\" or any competitor by name; \"replace your CRM\";", "source": "kit.md@662d63b:102 (v1, excerpt); round-1.md F23: rival framing on a page that may be public"}
{"id": "competitors-partners/F3/n01", "rule": "F3", "expect": "no_fire", "target": "copy", "text": "Already on Redtail or Wealthbox? Keep them for your book - bring any contact in with one click, as you do today.", "source": "kit.md final:35; crm-features-audit-2026-10-01.md section 4, 'matches reality' list"}
{"id": "competitors-partners/F2/n01", "rule": "F2", "expect": "no_fire", "target": "copy", "text": "- [Agents on an IMO's Enterprise account only] **Case Design with the whole story.** Click Request Case Design as you do today and [pick the emails and call notes that go with it] - [IMO name]'s desk designs for what the client actually asked. Nothing changes in the tools [IMO name] gives you.", "source": "kit.md final:28"}
{"id": "competitors-partners/F2/n02", "rule": "F2", "expect": "no_fire", "target": "copy", "text": "- Nothing changes in the tools you give your agents today. [You decide whether calling and texting are switched on for your agency's account, and who pays for them.]", "source": "kit.md final:127 (IMO note)"}
{"id": "competitors-partners/F1/n01", "rule": "F1", "expect": "no_fire", "target": "copy", "text": "Agents meet it under other names (Agent CRM, Quility's Switchboard), so the copy names no competitor; it answers the complaints component by component.", "source": "kit.md final:143 (how-made, excerpt)"}
{"id": "competitors-partners/F5/n01", "rule": "F5", "expect": "no_fire", "target": "copy", "text": "| 0:17 | Meeting booked → notes on the case → E-App prefilled (FireLight, where your IMO has it switched on) |", "source": "kit.md final:100"}
```
