---
landmine: compliance-promises
rule: F1
verdict: remove
slop_class: invented-fact
severity: critical
piece: email
source: kit.md@662d63b:25
verdict_by: panel round 1, all six lenses
verdict_ref: panel/round-1.md F2
date: 2026-09-30
---

## Passage (verbatim, as it stood in that version)

> - **One timeline.** Quote → email → call → meeting → e-app. The audit trail writes itself.

The same sentence closed a bullet of the social post (`kit.md@662d63b:57`).

## Why

Round 1, F2, "All six lenses": "a compliance promise the kit itself says it avoids." To a compliance team
it reads as "AG keeps the records the regulator asks for", and no AG document says so. The kit's own research
listed "Compliance is covered" without "your firm's policies still apply" under lines it must not write
(`crm-module-brief-2026-09-30.md` line 349).

## What happened after

Cut in v2 (git fceca84). The bullet became "One client profile, one timeline", and by v5 "every step sits on
the case, dated". Record keeping came back only as a bracketed TO-CONFIRM in the IMO note: "[every message is
kept on the case]" (kit.md line 129), with "retention period and export for audits" in the To confirm list
(kit.md line 190). That line still has no owner (`templates/decisions.md` has no closed row for it).
