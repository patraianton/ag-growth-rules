---
id: numbers-and-sources
version: 1
changed: 2026-10-02
asked_by: Anton Patrai
strictness: cite-or-cut
applies_to: [email, social, webinar, imo-note, how-made]
---

# Landmine: numbers, ranks, shares, superlatives and quotes

## 1. What this landmine is

Every count, rank, share, superlative and quote put in front of a reader: "93 help-center articles",
"third-largest complaint", "30% of all complaints", "the most frequent complaint", "as one agent put it".

Strictness `cite-or-cut`: a number stays only with a record in `templates/numbers.json`, printed at the
precision that record allows.

## 2. What it is not (hand-offs)

- Prices, minutes, texts and plan limits → `pricing-plans`. Setup times → `setup-timelines`.
- Counts of the process itself ("four review rounds", "six readers", "seven fix scripts") → `process-claims`.
- "AG has no X" → `research-absence`. A zero inside a study ("None about e-applications") stays here and
  needs a record with value 0.

## 3. Source of truth (resolution order; stop at the first that resolves)

1. `templates/numbers.json`: `{id, value, unit, what, precision, source_file, source_line, caveat}`.
   `precision` is `exact | approximate | double-counted | lane-stopped`. `approximate` renders as
   "about N". `double-counted` and `lane-stopped` render with "about" or with the caveat, in the same
   sentence or in an earlier sentence of the same `##` section. When two files give different counts for
   one quantity, the record keeps the value it trusts and lists the others under `conflicts`.
2. Ranks and shares are computed by `tools/check.py` from a `kind: table` record (the 14 complaint modules
   are `T-ghl-modules`) and a `kind: rank | share` record that names the table, the row and the result. A
   rank holds on a double-counted table (the study: "the order of modules holds"); a share does not, so a
   share inherits the table's precision. Table rows are inputs: a module count printed in copy needs its
   own record.
3. Quotes are rows of the Quotes table in `templates/facts.md`: text, speaker and role, where, date,
   weight. The text may be shortened; the role and the weight travel with it.

Never a source: a number in an earlier draft, a reviewer's replacement text, a public page built from the
same research (a consumer of `numbers.json`), a number the writer remembers.

## 4. Forbidden shapes (banned by shape)

- **F1 Number with no record.** A count in the text that `numbers.json` does not hold. Class: invented-fact.
  Severity: major.
- **F2 Typed rank or superlative.** "top-ten", "third-largest", "most frequent", "number one" with no
  computed row, or a computed row that disagrees. Class: false-precision. Severity: critical.
- **F3 Precision dropped.** A record that is not `exact`, printed bare. Class: false-precision. Severity: major.
- **F4 Two values for one quantity.** A value that a record lists under `conflicts` ("30 Shorts" against
  a record of 38 Shorts that lists 30). Class: contradiction. Severity: major.
- **F5 Quote reframed.** The role in the text differs from the record ("one agent" for a team lead of 8).
  Class: invented-fact. Severity: major.
- **F6 Generalisation from n=1.** "Their posts open X" over a habit seen once. Class: false-precision.
  Severity: minor.

## 5. Allowed with a row

- **A1** An exact count with its record ("all 93 help-center articles", "98 IMO sites").
- **A2** An approximate count as "about N" ("about 60 insurance-forum threads").
- **A3** A double-counted total with its caveat ("counts are close, not exact: two lanes read the same
  review sites").
- **A4** A rank that matches its computed row ("GoHighLevel's third-largest complaint is its mobile app").
- **A5** A quote with its recorded role ("as one team lead put it").

## 6. Detection

**Stage 1.** `number` cues: `tools/check.py` takes each number in the line, skipping placeholders (`[N]`,
`$X`), years, times of day, a list number at line start, and anything inside quotation marks. It looks the
number up in `numbers.json` by value (the unit word after it picks between records with the same value).
No record: F1, or F4 when a record lists the value under `conflicts`. A record that is not `exact` and no
hedge in the line or in an earlier line of the same `##` section: F3. A number right after "about",
"around", "roughly" or "~" is hedged on its own. `rank` cues: a hit unless a computed record whose `phrase`
occurs in the line recomputes from its table. A percentage needs a record with unit `%` or a computed
`share` record whose phrase is in the line. No `numbers.json`, or a rank record whose table is missing:
`not_run`.

```cues
# rule | target | rescues | kind   | pattern
F1     | copy   | bracket | number | \b\d{1,3}(?:,\d{3})+\b|\b\d+(?:\.\d+)?\b
F3     | copy   | bracket | number | (?i)\bclose, not exact\b|\bcounted twice\b|\bdouble[- ]counted\b|\blane (?:was )?stopped\b
F2     | copy   | none    | rank   | (?i)\btop[- ](?:three|five|ten|\d+)\b
F2     | copy   | none    | rank   | (?i)\b(?:second|third|fourth|fifth)[- ]largest\b
F2     | copy   | none    | rank   | (?i)\bmost (?:frequent|common|named|cited)\b
F2     | copy   | none    | rank   | (?i)\b(?:number one|no\. ?1|#1)\b
F5     | copy   | none    | regex  | (?i)\b(?:as )?(?:one|an?) (?:agent|advisor|producer) (?:put it|said|wrote)\b
F6     | copy   | none    | regex  | (?i)\btheir (?:posts|emails|launches) (?:open|start|end)\b
```

**Stage 2** (`rules/README.md`) gets the sentence, the matched record and its source line. It answers:
same quantity or not, precision kept or not, role kept or not.

## 7. Fixtures

`must_fire` rows are real lines of the kit at v9 (01.10.2026, before the 23:41 correction) or earlier,
with the fix script that wrote them (in the author's private working folder). `needs` lists the records the row is judged
against. With the records present, every `no_fire` row passes; remove N-10 and the first one must fire.

```fixtures
{"id": "numbers-and-sources/F1/01", "rule": "F1", "expect": "fire", "target": "copy", "text": "The agent portrait I built from about 600 Reddit posts, insurance-forum threads, and 98 IMO sites", "source": "kit.md v9:156 (excerpt), written by apply-v9.py:63; no file holds 600 (agent-portrait-v3 header: 155 threads, 7,627 comments)", "needs": ["N-14"]}
{"id": "numbers-and-sources/F1/02", "rule": "F1", "expect": "fire", "target": "copy", "text": "593 Reddit posts and ~20 forum threads where agents discuss CRMs and follow-ups; 100 IMO websites for free tools", "source": "kit.md@662d63b:91 (v1, excerpt); 593 is in no file and became ~600 in v2", "needs": []}
{"id": "numbers-and-sources/F2/01", "rule": "F2", "expect": "fire", "target": "copy", "text": "Export: clients, messages, and recordings export any time, and nothing is held back if an agent leaves (data lock-in is a top-ten complaint about GoHighLevel).", "source": "kit.md v9:192, written by apply-v8.py:46; ghl-complaints-2026-10-01.md line 58: 47 records, 14th of 14", "needs": ["N-09"]}
{"id": "numbers-and-sources/F4/01", "rule": "F4", "expect": "fire", "target": "copy", "text": "Channel tab Shorts: 30 shorts listed", "source": "not kit text: crm-research/raw/audit-youtube.md line 8 (excerpt), the audit note; the raw tab list has 38 (N-03). The kit's v9 line 142 printed 38, which was right. Inline record: templates/numbers.json N-03 does not list 30 under conflicts", "numbers": [{"id": "N-03", "value": 38, "unit": "Shorts", "precision": "exact", "conflicts": [30]}]}
{"id": "numbers-and-sources/F3/01", "rule": "F3", "expect": "fire", "target": "copy", "text": "I read 3,803 public reviews, posts, and feature requests about it from eight source types and sorted 1,927 complaints by module:", "source": "kit.md v9:143, old string in anti-slop/fix-kit-how-made.py:9; ghl-complaints-2026-10-01.md section 2: two lanes read the same Trustpilot and G2", "needs": ["N-07", "N-08"]}
{"id": "numbers-and-sources/F5/01", "rule": "F5", "expect": "fire", "target": "copy", "text": "the rule that every feature line says where it's saved, because, as one agent put it in an r/InsuranceAgent thread, \"A CRM that's 60% current is worse than a spreadsheet everyone trusts.\"", "source": "kit.md v9:156 (excerpt, quote markup dropped), written by apply-v9.py:65; crm-module-brief-2026-09-30.md line 183: 'I run a team of 8 producers', weight low", "needs": []}
{"id": "numbers-and-sources/F6/01", "rule": "F6", "expect": "fire", "target": "copy", "text": "their posts open \"New in Annuities Genius:\" and end on a link or a question", "source": "kit.md final:157 (excerpt); the opener appears once, LinkedIn 29.09.2026 (rules/voice.md section 3)", "needs": []}
{"id": "numbers-and-sources/F1/n01", "rule": "F1", "expect": "no_fire", "target": "copy", "text": "the agent portrait I built from 155 Reddit threads, about 60 insurance-forum threads, 769 Indeed reviews, and 98 IMO sites matched it", "source": "kit.md final:156 (excerpt); agent-portrait-v3 header; imo-interview-brief-2026-09-30.md line 19 (100 viewed, 98 parsed)", "needs": ["N-10", "N-12", "N-13", "N-14"]}
{"id": "numbers-and-sources/F1/n02", "rule": "F1", "expect": "no_fire", "target": "copy", "text": "I went through the public record: all 93 help-center articles", "source": "kit.md final:142 (excerpt); crm-features-audit-2026-10-01.md line 169", "needs": ["N-01"]}
{"id": "numbers-and-sources/F1/n03", "rule": "F1", "expect": "no_fire", "target": "copy", "text": "Users blame the company before the features: support and billing are 30% of all complaints", "source": "kit.md final:155 (excerpt); share computed from T-ghl-modules: (309 + 271) / 1,927 = 30.1%", "needs": ["S-support-billing"]}
{"id": "numbers-and-sources/F4/n01", "rule": "F4", "expect": "no_fire", "target": "copy", "text": "all 93 help-center articles, the 103 videos and the Shorts on AG's channel, 166 site pages and 65 snapshots of the pricing page since 2019", "source": "kit.md final:142 (excerpt), after the 2026-10-01 23:41 correction", "needs": ["N-01", "N-02", "N-03", "N-04", "N-05"]}
{"id": "numbers-and-sources/F3/n01", "rule": "F3", "expect": "no_fire", "target": "copy", "text": "sorted 1,927 complaints by module (counts are close, not exact: two lanes read the same review sites):", "source": "kit.md final:143 (excerpt)", "needs": ["N-08"]}
{"id": "numbers-and-sources/F2/n01", "rule": "F2", "expect": "no_fire", "target": "copy", "text": "4. GoHighLevel's third-largest complaint is its mobile app, and AG has no app at all.", "source": "kit.md final:165 (excerpt); computed rank 3 of 14 (216 records)", "needs": ["R-mobile"]}
{"id": "numbers-and-sources/F5/n01", "rule": "F5", "expect": "no_fire", "target": "copy", "text": "because, as one team lead put it in an r/InsuranceAgent thread, _\"A CRM that's 60% current is worse than a spreadsheet everyone trusts.\"_", "source": "kit.md final:156 (excerpt); templates/facts.md Q-01; crm-module-brief-2026-09-30.md line 183", "needs": []}
```

In the final kit, the module counts at lines 147-150 and 153 (92, 168, 210, 50, 271, 216, 147) fire F1:
they are rows of `T-ghl-modules` and have no printed-count record. 309, 47, 1,927 and the 30% share
(lines 153, 155, 192) have records that are not exact; they pass only through the caveat at line 143 in
the same `##` section. Moved to another section, they fire F3.
