# tools/

Python 3.11, standard library only. `.github/workflows/check.yml` runs the same commands on Linux.

| file | what it does |
|---|---|
| `check.py` | step 5 (Lint) and the step 8 release checks on one piece, its page, numbers file, facts table, coverage map, decision log and claims ledger |
| `selftest.py` | every fixture fires or stays silent as recorded; every forbidden shape has a passing fire fixture |
| `fixtures/must_fire.jsonl` | 48 lines from real kit versions (and the templates' own ledger rows) that must fire |
| `fixtures/must_not_fire.jsonl` | 31 real clean lines that must stay silent |
| `fixtures/sample/` | what CI runs: `clean.md` with `claims.csv` (final-kit lines, must exit 0 against the shipped templates) and `v1-email.md` (v1 email, git 662d63b, must exit 1) |

## Run

```
python tools/selftest.py
python tools/check.py path/to/draft.md
python tools/check.py path/to/draft.md --html path/to/page.html --claims templates/claims.csv
python tools/check.py path/to/draft.md --html page.html --claims templates/claims.csv \
       --panel path/to/panel --reviewed-sha256 <hash> --stamp          # release (step 8)
python tools/check.py path/to/draft.md --json
```

Flags: `--numbers` (default `templates/numbers.json`), `--facts` (default `templates/facts.md`),
`--coverage` (default `templates/coverage.md`), `--decisions` (default `templates/decisions.md`),
`--claims`, `--landmines` (default `rules/landmines`), `--voice` (default `rules/voice.md`), `--html`,
`--panel` (folder of `round-*.md` reports), `--reviewed-sha256` (sha256 of the last reviewed version),
`--stamp` (append stage-1 stamps to `<piece>.stamps.jsonl`; shape in `rules/README.md`, Detection),
`--max-marks` (default 7), `--dotted-class` (default `tbc`), `--piece-type` (for a file that holds one
piece), `--require-all` (a check not requested also makes the exit 3), `--json`.

Exit codes: `0` clean · `1` findings · `2` bad invocation · `3` not run. 3 outranks 1. Exit 3 comes from a
missing required input (piece, landmines, voice, numbers, facts table when a landmine targets it, coverage
map when an ABSENT row names coverage, decisions file, a file named by `--html`, `--claims` or `--panel`),
a landmine with no cues, or a rule that does not compile. Parity, claims and release-hash are `not_run`
without `--html`, `--claims` or `--reviewed-sha256`; that moves the exit code only with `--require-all`.

Output: one line per finding, then a summary table.

```
CHECK | severity | file:line | quote | rule-id
time-promises | major | kit.md:32 | Pick a local number and start calling right away - or [bring your office line over]. | setup-timelines/F1
```

## The checks

| check | what fails it | rule ids |
|---|---|---|
| `landmines` | a cue from `rules/landmines/*.md` (all but `setup-timelines` and `plain-language`) matches and no rescue applies; research-absence F2/F4 and process-claims F3/F4 lookups | `<landmine>/F1` ... |
| `voice` | a banned word or shape from `rules/voice.md`, beyond its counted exception | `voice/VB3`, `voice/VN1` ... |
| `numbers` | a number with no record in `numbers.json` (F1); a value a record lists under `conflicts` (F4); a record that is not `exact` printed without its hedge in the line or an earlier line of the same section (F3) | `numbers-and-sources/F1`, `/F3`, `/F4` |
| `parity` | a sentence of 4+ words in the piece and not on the page, or the reverse | `parity/piece-only`, `parity/page-only` |
| `stray-labels` | a word printed twice in a row ("offer offer"); a label string in the rendered page text, unless its whole sentence is also in the markdown | `stray/doubled-word`, `stray/label:<s>` |
| `repeats` | any run of 8 words that appears twice in the piece; URLs and link targets are not counted | `repeats/8-words` |
| `time-promises` | a cue from `rules/landmines/setup-timelines.md` | `setup-timelines/F1` ... |
| `plain` | in email, social, webinar and imo-note: a sentence over 20 words (F1); a list item or agenda row with a semicolon, two dash asides, or more than three sentences after its label and over 30 words (F2); a 3-word phrase 3 times in one item or paragraph (F3); a term not in `voice.md` section 8 and not plain English with no plain words in its sentence or the one before, or an AG term in a heading with no plain words on the line (F4); a side-note title with `=`, "X, not Y" or "line" (F5); history or a reason in feature copy (F7). Flesch-Kincaid grade per `##` section, printed in the note: above 9 for the email body and the IMO note, above 11 for the how-made steps (F6). The email's hook and quoted speech are skipped. With `--html`, the tooltip (`title=`) of each dotted span on the page is also read for F4 and F5, reported at the span's line | `plain-language/F1` ... `/F7` |
| `claims` | a ledger row with status UNMARKED or blank; TO-CONFIRM with no owner (major), an owner written "proposed: ..." (minor), or no date (minor) | `claims/UNMARKED` ... |
| `mark-budget` | more than 7 marks in one `##` section. On the page every dotted span counts; in markdown a bracket of three words or fewer is a merge field and not counted | `marks/over-limit` |
| `killed-lines` | a pattern from the killed-lines table of `decisions.md` matches, brackets included, and its row names no reversing decision | `killed/K-01` ... |
| `release-hash` | the sha256 of the piece file differs from `--reviewed-sha256` | `release/hash-mismatch` |

How the piece is read. Markdown: as is, one line at a time. A page: as rendered text; `script`, `style`,
`head`, `svg` and `<sup>` footnote numbers are dropped, attributes such as `title=` are never text, block
tags end a line. For cues a dotted span (`<span class="tbc">`) reads as `[...]`; for parity and stray
labels it reads as plain text. Each `##` heading tags what follows as a piece: `email`, `social`,
`webinar`, `imo-note`, `how-made`.

How `plain` reads the markdown piece. Units are lines: paragraph lines, list items (`- `, `1. `), table rows,
bold-only lines and `###` headings (headings for F4), `**From:**`/`**To:**`/`**Subject:**`/`**Preview:**` fields
(Subject is a heading; From and To are skipped). A bold label at the start of an item is its own sentence. A
`**Side notes...**` line opens a side-notes block; `---` or the next `##` closes it. The hook is the first
paragraph after the greeting ("Hi ...,") of the email section, or after its header fields. Quoted text
(`"..."`) counts as one word; link targets, URLs, file-name link texts and hashtags are dropped. A grade counts
words with a letter (numbers are not words), syllables by vowel groups with a silent final e dropped; the email
and IMO note grade covers the body after the greeting and outside side notes, the how-made grade the numbered
steps. On a page given as the piece the check reads rendered lines, where inline tags glue words: run it on the
markdown, parity holds the page to it.

Numbers skipped as non-claims: years (19xx, 20xx), times of day and agenda minutes, phone numbers, dates,
list and heading numbers, "section 4", "round 3", "F8"-style ids, product versions ("GrantAI 2.0"),
anything inside quotation marks (a quote has its own row), prices inside brackets, hashtags, URLs.

## File formats the scripts read

### Cues: a fenced `cues` block in each landmine file

One cue per line, five columns split on the first four `|` (the pattern may contain `|`):

```cues
# rule | target | rescues | kind  | pattern
F1     | copy   | bracket | regex | (?i)\bright away\b|\bfrom day one\b
F2     | copy   | none    | topic | recording=(?i)\bcall recording\b
F2     | copy   | none    | rank  | (?i)\btop[- ](?:three|five|ten)\b
F1     | copy   | bracket | number| \b\d{1,3}(?:,\d{3})+\b|\b\d+\b
F1     | facts  | none    | regex | ^(?!.*\bCOV-\d+\b).*\|\s*ABSENT\s*\|
```

- `target`: `copy` runs on the piece and the page; `facts` runs on the data rows of every table with a
  `claim` column in the facts table (`--facts`), with the `refute` column blanked.
- `rescues`: `none`, or a comma list of `bracket` (the match lies wholly inside one `[...]` or dotted
  span), `proposal` (the line says "my proposal"), `question` (the line holds a `?`).
- `kind`: `regex` (a match is a hit); `topic` (`name=pattern`: matching lines are grouped by piece; fires
  when two pieces carry different clauses); `rank` (a hit unless `numbers.json` holds a computed record
  whose `phrase` is in the line and whose result recomputes from its table); `number` (run by the
  `numbers` check: the cue that matches "1,927" marks F1, the other is the hedge for F3).
- Patterns are Python `re`, case-sensitive unless they start with `(?i)`. A pattern that does not
  compile or matches the empty string is refused.
- Short form, also accepted: `F1: <pattern>` or a bare pattern per line (target copy, rescue bracket).
- Severity comes from `Severity: <level>` in the shape's bullet (`- **F1 Name.** ... Severity: major.`).
- Extra stray-label strings: a fenced `labels` block, one literal per line, in any landmine file or in
  `rules/voice.md`.

### Fixtures

In a landmine file, a fenced `fixtures` block, one JSON object per line:
`{"id", "rule", "expect": "fire"|"no_fire", "target", "text" | "texts": [{"piece", "text"}], "source", "needs"}`,
plus `coverage` (a coverage table, for research-absence F2), `panel_reports`, `piece_sha256` and
`reviewed_sha256` (for process-claims F3 and F4). `needs` lists the `numbers.json` record ids the fixture
runs with ("N-08", "R-mobile"); the fixture sees only those records. `numbers` (inline records) replaces
`needs` when the record the fixture needs differs from `templates/numbers.json`.

In `tools/fixtures/*.jsonl`, one object per line:
`{"id", "landmine", "rule", "text" | "texts" | "html", "why", "file", "version", "line"}`, plus optional
`needs`, `numbers` (inline records), `piece`, `limit`. `landmine` is a landmine id or a check name
(`voice`, `numbers`, `parity`, `stray-labels`, `repeats`, `claims`, `mark-budget`, `killed-lines`); `plain` is
read as `plain-language`. `piece` tags a one-piece fixture (`email`, `how-made` ...). The
file decides the expectation.

In `rules/examples/*.md`: front matter `landmine`, `rule`, `verdict`; the passage is the first `>`
block under `## Passage`. `remove` and `rewrite` must fire their rule; `keep` must fire no shape of its
landmine.

### numbers.json

A list of records. A record has `value`, and may have `id`, `unit`, `precision` (`exact | approximate |
double-counted | lane-stopped`) and `conflicts` (values other files give for the same quantity). Computed
rows:

```json
{"id": "T-ghl-modules", "kind": "table", "rows": {"Support": 309, "Billing, pricing, cancellation": 271, "Mobile app": 216}}
{"id": "R-mobile", "kind": "rank", "phrase": "third-largest complaint", "table": "T-ghl-modules", "row": "Mobile app", "result": 3}
{"id": "S-support-billing", "kind": "share", "phrase": "30% of all complaints", "table": "T-ghl-modules", "rows": ["Support", "Billing, pricing, cancellation"], "result": 30, "precision": "double-counted"}
```

A rank is the row's place by value, largest first; a share is the rows' sum over the table's sum, in
percent, within 0.5. A rank record whose table is missing makes the check `not_run`. Table rows are
inputs for ranks and shares, not records of printed counts.

### facts.md and coverage.md

`check_absence` reads every table with `claim` and `label` columns in the facts table. For each ABSENT
row it takes the `COV-n` ids in the row (outside `refute`) and looks them up in every table of
`coverage.md` whose first column holds `COV-n`. A row is uncovered when its `keyword-searched` cell is
blank, `0` or "none", and its `read fully` count is below `total`. It also counts rows whose `refute`
cell ends on `overturned`: the cell keeps its history, so only the last verdict word in it (`held`,
`overturned` or `unverifiable`) counts. A facts fixture may pin these counts with a `stats` field.

### decisions.md: killed lines

A table with a column whose header contains `pattern`. The pattern is a Python regex between backticks;
`\|` (a table's escaped pipe) is read as `|`. A row whose `reversed by` cell holds a `D-n` id is skipped.

### claims.csv

Columns found by name: `status`, `owner`, `due` (or `date`), `claim`. Statuses: `SOURCED`, `PROPOSAL`,
`TO-CONFIRM`, `UNMARKED`.

### voice.md

AG's own terms (check `plain`, F4): a fenced `terms` block, `term | count or source | plain words regex` (`-` for a
name). The term is matched case-sensitively.

Banned cues come from every table with a column whose header contains "cue": `` `phrase` `` is literal,
``regex `...` `` is a regex; a cell that says "case-sensitive" is matched case-sensitively; a cell that
ends "in email, social, ..." applies to those pieces only. Also accepted: a fenced `banned` block (one
regex per line) and a fenced `allowed` block (`<regex> | <max count per piece>`).

## What selftest refuses

A landmine with no cues; a cue that does not compile or matches the empty string; a forbidden shape with
no `Severity:` or with no passing fire fixture under its rule id; a landmine with zero fire fixtures; a
front-matter version that differs from `rules/manifest.json`; a fixture whose `needs` ids are not in
`templates/numbers.json`; a missing killed-lines table; a duplicate fixture id. Two twin runs show a
lookup is read: a `numbers-and-sources` no_fire fixture with records is run again without them and must
fire F1; a `process-claims` F4 fire fixture is run again with equal hashes and must not fire. Any
failure, or a fixture that could not run, gives exit 1. `selftest.py` writes no `__pycache__`.

## Known limits

- String checks catch words and numbers, not meaning. A false sentence with no number and no cue
  passes. Stage 2 and the review round carry the rest; they are agent steps (`rules/README.md`, Detection).
- The order-of-work and duration checks (process-claims F1, F6) need `git log` dates; the script does not
  read git. They are stage-2 steps.
- Stage 1 over-selects. On the final kit, `compliance-promises` F1 fires on bracketed promises by design
  (brackets do not rescue it), `voice` VB1 selects every list of three that does not open with a channel noun, `numbers` flags planned values
  such as "Day 0 / 2 / 5 / 10", and the `recording` topic matches "the recording is made up" in the
  social post.
- Label strings hit real sentence ends: the final page has three "number." hits, all genuine ends
  ("from your own number.").
- Line numbers on a page are the HTML source lines where the text starts.
- `claims` checks the ledger rows, not whether every claim in the piece has a row.
- F4 for numbers catches only the conflicting values a record lists; an unlisted second value is F1.
- Cue hits on the page repeat the hits on the markdown when both carry the same text.

## Last run on the real kit (2026-10-02)

On the 2026-10-01 version, before the fix pass. The fixes and the release (exit 0):
`process/runs/2026-10-02-ag-kit/README.md`.

On the 2026-10-01 version (sha256 `719d5a85...`), with `--html` and `--claims`: exit 1, 189 findings (32 critical, 79 major, 78 minor): [before.txt](../process/runs/2026-10-02-ag-kit/before.txt). Some that matter:

| check | where | finding |
|---|---|---|
| landmines | kit.md:140 | "four review rounds of six readers": process-claims F3 (no `--panel`), F5 (simulated readers), F6 ("in one night") |
| killed-lines | kit.md:42, 50, 70, 153, 192 | the export promise (K-02), "a person picks up" (K-06) and "Not another system to set up" (K-01) are back with no decision |
| time-promises | kit.md:31, 32 | "work right away", "start calling right away"; AG has no telephony (facts F-06) |
| landmines | kit.md:129 | text consent and call recording stated differently in the email and the IMO note |
| numbers | kit.md:147-153 | module counts 92, 168, 210, 50, 271, 216, 147 have no printed-count record |
| mark-budget | index.html:154 | 16 dotted spans in the email section, limit 7. `kit.md` gives 14: the merge-field rule drops `["Open in mail"]` and `[Client Conversations]`, the page dots the whole menu path where the markdown brackets only the name, and the markdown brackets a segment label the page does not dot |
| claims | templates/claims.csv:6, 7 | TO-CONFIRM rows with a proposed owner and no date |
| repeats | kit.md:186, 187, 189 | the To confirm list repeats the email's promises word for word |
| parity | index.html:173-178, 210 | the page carries side notes ("Calling starts with a new local number", "Twilio quotes up to 5 business days") that kit.md does not |
| stray-labels | index.html:145, 274 | three "number." hits, all real sentence ends (see limits) |

"third-largest complaint" (kit.md:165) and "the most frequent complaint" (kit.md:193) pass: the rank
records `R-mobile` and `R-support` recompute from `T-ghl-modules`.
