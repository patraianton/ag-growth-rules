---
landmine: product-claims
rule: A1
verdict: keep
slop_class: invented-fact
severity:
piece: email
source: kit.md@816d805:32
verdict_by: panel round 4 ("do not change"); the 01.10 audit, section 4
verdict_ref: panel/round-4.md section 4; crm-features-audit-2026-10-01.md line 137
date: 2026-10-01
---

## Passage (verbatim, as it stood in that version)

> **Getting started.** Every client you've quoted in Annuities Genius is already here.

Unchanged in the final kit (kit.md line 30).

## Why

Round 4 listed it under "Do not change (the panel agreed these are strong)". The audit, which did not
trust the panel, listed it under what in the kit matches reality. Help article 25: "Any analysis, reports,
or notes you create while that client is selected will automatically be saved".

## What it shows

An unbracketed product sentence is fine when a CONFIRMED row backs it: `F-09` in `templates/facts.md`,
`CL-01` (SOURCED) in `templates/claims.csv`. It has no cue words, so a cue that fires on it is wrong.
