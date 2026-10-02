#!/usr/bin/env python3
"""Self-test of the rules and of tools/check.py. Standard library only, Python 3.11.
Usage: python tools/selftest.py [--verbose]. What it loads and refuses: tools/README.md."""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import check as C  # noqa: E402

ROOT = C.ROOT
FIXTURES = ROOT / "tools" / "fixtures"
CHECK_ALIASES = {"time-promises": C.TIME_LANDMINE, "plain": C.PLAIN_LANDMINE}
RULE_PREFIX = {"stray-labels": "stray", "mark-budget": "marks", "repeats": "repeats", "parity": "parity",
               "claims": "claims", "numbers": "numbers", "voice": "voice", "killed-lines": "killed"}


@dataclass
class Ctx:
    landmines: dict[str, C.Landmine]
    voice: C.Voice | None
    numbers: C.Numbers | None
    labels: list[str]
    problems: list[str] = field(default_factory=list)
    killed: list = field(default_factory=list)
    plain: C.PlainRules | None = None


def front_matter_and_passage(md: Path) -> tuple[dict, str | None]:
    text = md.read_text(encoding="utf-8")
    fm = C.front_matter(text)
    m = re.search(r"^## Passage[^\n]*\n\s*((?:>.*\n?)+)", text, re.M)
    passage = " ".join(ln.lstrip(">").strip() for ln in m.group(1).splitlines()).strip() if m else None
    return fm, passage


def load_examples(ctx: Ctx) -> list[dict]:
    out = []
    d = ROOT / "rules" / "examples"
    if not d.is_dir():
        return out
    for md in sorted(d.glob("*.md")):
        if md.name.upper() in ("README.MD", "TEMPLATE.MD"):
            continue
        fm, passage = front_matter_and_passage(md)
        verdict = fm.get("verdict", "")
        if not passage:
            ctx.problems.append(f"example {md.name}: no '> ' passage under '## Passage'")
            continue
        if verdict not in ("remove", "rewrite", "keep"):
            ctx.problems.append(f"example {md.name}: verdict must be remove | rewrite | keep, got {verdict!r}")
            continue
        out.append({"id": f"example:{md.name}", "landmine": fm.get("landmine", ""),
                    "rule": "" if verdict == "keep" else fm.get("rule", ""),
                    "text": passage, "piece": fm.get("piece") or None,
                    "expect": "no_fire" if verdict == "keep" else "fire", "_from": f"rules/examples/{md.name}"})
    return out


def load_jsonl(path: Path, expect: str, ctx: Ctx) -> list[dict]:
    out = []
    if not path.is_file():
        ctx.problems.append(f"{path.relative_to(ROOT)} missing")
        return out
    for k, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            fx = json.loads(line)
        except json.JSONDecodeError as e:
            ctx.problems.append(f"{path.name} line {k}: not JSON ({e})")
            continue
        missing = [key for key in ("id", "landmine", "rule", "why", "file", "version") if key not in fx]
        if not any(key in fx for key in ("text", "texts", "html")):
            missing.append("text|texts|html")
        if missing:
            ctx.problems.append(f"{path.name} line {k} ({fx.get('id')}): missing {missing}")
            continue
        fx["expect"] = expect
        fx["_from"] = f"tools/fixtures/{path.name} line {k}"
        out.append(fx)
    return out


def fixture_numbers(fx: dict, ctx: Ctx) -> tuple[C.Numbers, list[str], list[str]]:
    """Inline "numbers" records, else the "needs" ids from templates/numbers.json."""
    if isinstance(fx.get("numbers"), list):
        return C.numbers_from(fx["numbers"]), [], []
    needs = fx.get("needs") or []
    ids = [n for n in needs if isinstance(n, str) and re.fullmatch(r"[A-Z]+-[A-Za-z0-9-]+", n)]
    known = {r.get("id") for r in (ctx.numbers.records if ctx.numbers else [])} | \
            {r.get("id") for r in (ctx.numbers.computed if ctx.numbers else [])}
    missing = [i for i in ids if i not in known]
    probs = [f"needs {missing}, not in templates/numbers.json"] if missing else []
    # rank/share rows are looked up by phrase
    text = " ".join([fx.get("text", "")] + [t.get("text", "") for t in fx.get("texts") or []]).lower()
    phrased = [str(r.get("id")) for r in (ctx.numbers.computed if ctx.numbers else [])
               if str(r.get("phrase", "")).lower() and str(r["phrase"]).lower() in text]
    return C.numbers_subset(ctx.numbers, ids + phrased), ids, probs


def build_docs(fx: dict):
    target = fx.get("target", "copy")
    if fx.get("texts"):
        text = "\n".join(f"## {t.get('piece', '')}\n{t['text']}" for t in fx["texts"])
        doc = C.md_doc(text, "<fixture>")
    elif target == "facts":
        doc = C.facts_doc(fx.get("text", ""), "<fixture>")
    else:
        doc = C.md_doc(fx.get("text", ""), "<fixture>", fx.get("piece"))
    plain = cues = None
    if fx.get("html"):
        plain = C.html_doc(fx["html"], "<fixture.html>")
        cues = C.html_doc(fx["html"], "<fixture.html>", brackets=True)
    return doc, plain, cues


def findings_for(fx: dict, ctx: Ctx, numbers: C.Numbers) -> tuple[list[C.Finding], str | None]:
    """Returns (findings, reason it could not run)."""
    name = CHECK_ALIASES.get(fx["landmine"], fx["landmine"])
    doc, plain, cue_page = build_docs(fx)
    target = fx.get("target", "copy")
    if name in ctx.landmines:
        lm = ctx.landmines[name]
        if not lm.cues:
            return [], f"landmine {name} has no cues"
        if name == C.PLAIN_LANDMINE:
            if not ctx.plain or ctx.plain.errors:
                return [], f"plain rules not loaded: {ctx.plain.errors if ctx.plain else 'none'}"
            fs = C.check_plain(doc, ctx.plain)[0]
            if fx.get("html"):                     # tooltips of the page's dotted spans
                fs += C.check_plain_titles(fx["html"], "<fixture.html>", ctx.plain)[0]
            return fs, None
        fs: list[C.Finding] = []
        docs = [doc] + ([cue_page] if cue_page else []) if fx.get("text") or fx.get("texts") else [cue_page]
        for d in docs:
            if d is None:
                continue
            fs += C.check_cues(d, [lm], "fixture", numbers, target)[0]
            if name == C.NUMBERS_LANDMINE and target == "copy":
                fs += C.check_numbers(d, numbers, lm)
        if name == C.ABSENCE_LANDMINE and target == "facts":
            cov = C.coverage_rows(fx["coverage"]) if fx.get("coverage") else None
            fs += C.check_absence(fx.get("text", ""), "<fixture>", cov, lm)[0]
        if name == C.PROCESS_LANDMINE:
            fs = C.process_record(fs, lm, fx.get("panel_reports"), fx.get("piece_sha256"),
                                  fx.get("reviewed_sha256"))
        return fs, None
    if name in C.CHECKS or name == "numbers":
        if name == "voice":
            return (C.check_voice(doc, ctx.voice), None) if ctx.voice else ([], "rules/voice.md missing")
        if name == "numbers":
            return C.check_numbers(doc, numbers, None), None
        if name == "stray-labels":
            return C.check_stray(plain or doc, ctx.labels, doc if plain and fx.get("text") else None), None
        if name == "repeats":
            return C.check_repeats(doc), None
        if name == "parity":
            return (C.check_parity(doc, plain), None) if plain else ([], "parity fixture needs text and html")
        if name == "mark-budget":
            return C.check_marks(doc, int(fx.get("limit", C.MAX_MARKS))), None
        if name == "claims":
            return C.check_claims(C.read_claims(fx.get("text", "")), "<fixture>"), None
        if name == "killed-lines":
            if not ctx.killed:
                return [], "no killed-lines table in templates/decisions.md"
            return C.check_killed(doc, ctx.killed), None
    return [], f"unknown landmine or check {fx['landmine']!r}"


def rule_matches(f: C.Finding, fx: dict) -> bool:
    name = CHECK_ALIASES.get(fx["landmine"], fx["landmine"])
    rule = (fx.get("rule") or "").strip()
    if name in ctx_landmine_ids:
        return f.rule == f"{name}/{rule}" if rule else f.rule.startswith(name + "/")
    prefix = RULE_PREFIX.get(name, name)
    if not f.rule.startswith(prefix + "/") and f.check != name:
        return False
    if not rule:
        return True
    tail = f.rule.split("/", 1)[-1]
    return tail == rule or tail.startswith(rule + ":") or f.rule == rule


ctx_landmine_ids: set[str] = set()


def evaluate(fx: dict, ctx: Ctx) -> tuple[str, str]:
    """Returns (status, detail): status ok | FAIL | NOT_RUN."""
    numbers, ids, probs = fixture_numbers(fx, ctx)
    if probs:
        return "NOT_RUN", "; ".join(probs)
    fs, why = findings_for(fx, ctx, numbers)
    if why:
        return "NOT_RUN", why
    # a facts fixture may also pin the counts check_absence prints ("N overturned")
    if isinstance(fx.get("stats"), dict):
        st = C.check_absence(fx.get("text", ""), "<fixture>", None, None)[1]
        bad = {k: (v, st.get(k)) for k, v in fx["stats"].items() if st.get(k) != v}
        if bad:
            return "FAIL", "stats " + ", ".join(f"{k}: expected {e}, got {g}" for k, (e, g) in bad.items())
    hits = [f for f in fs if rule_matches(f, fx)]
    # "needs" in words: a record numbers.json does not hold; a failure then means not run
    worded = [n for n in (fx.get("needs") or []) if isinstance(n, str) and not re.fullmatch(r"[A-Z]+-[A-Za-z0-9-]+", n)]
    if fx["expect"] == "fire" and not hits:
        if worded:
            return "NOT_RUN", f"needs a record templates/numbers.json does not hold: {worded}"
        other = sorted({f.rule for f in fs})
        return "FAIL", "did not fire" + (f" (fired instead: {', '.join(other)})" if other else "")
    if fx["expect"] == "no_fire" and hits:
        if worded:
            return "NOT_RUN", f"needs a record templates/numbers.json does not hold: {worded}"
        return "FAIL", f"fired: {hits[0].rule} on {hits[0].quote[:90]!r}"
    # twin: without its records a numbers no_fire fixture must fire F1
    name = CHECK_ALIASES.get(fx["landmine"], fx["landmine"])
    if fx["expect"] == "no_fire" and ids and name == C.NUMBERS_LANDMINE and fx.get("rule") in ("F1", "F3"):
        bare, _ = findings_for(fx, ctx, C.numbers_from([]))
        if not any(f.rule == f"{name}/F1" for f in bare):
            return "FAIL", "with its numbers.json records removed it still does not fire F1: the check is not reading the file"
    # twin: with equal hashes a process-claims F4 fire fixture must go silent
    if fx["expect"] == "fire" and name == C.PROCESS_LANDMINE and fx.get("rule") == "F4":
        same = dict(fx, reviewed_sha256=fx.get("piece_sha256"))
        again, _ = findings_for(same, ctx, numbers)
        if any(f.rule == f"{name}/F4" for f in again):
            return "FAIL", "with equal hashes it still fires F4: the check is not comparing hashes"
    return "ok", ""


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    lms = C.load_landmines(ROOT / "rules" / "landmines")
    voice_path = ROOT / "rules" / "voice.md"
    voice = C.load_voice(voice_path) if voice_path.is_file() else None
    numbers = None
    np_ = ROOT / "templates" / "numbers.json"
    problems: list[str] = []
    if np_.is_file():
        try:
            numbers = C.load_numbers(np_)
        except json.JSONDecodeError as e:
            problems.append(f"templates/numbers.json: not JSON ({e})")
    else:
        problems.append("templates/numbers.json missing")
    labels = list(C.DEFAULT_LABELS)
    for lm in lms:
        labels += [x for x in lm.labels if x not in labels]
    ctx = Ctx({lm.id: lm for lm in lms}, voice, numbers, labels, problems)
    if C.PLAIN_LANDMINE in ctx.landmines:
        ctx.plain = C.plain_rules(ctx.landmines[C.PLAIN_LANDMINE], voice_path)
        problems += [e for e in ctx.plain.errors if e not in ctx.landmines[C.PLAIN_LANDMINE].errors]
    ctx_landmine_ids.update(ctx.landmines)
    dp = ROOT / "templates" / "decisions.md"
    if dp.is_file():
        ctx.killed, kerr = C.load_killed(dp.read_text(encoding="utf-8"))
        problems += kerr
        if not ctx.killed:
            problems.append("templates/decisions.md: no killed-lines table")
    else:
        problems.append("templates/decisions.md missing")

    if not lms:
        problems.append("no landmine files in rules/landmines")
    manifest = {}
    mp = ROOT / "rules" / "manifest.json"
    if mp.is_file():
        manifest = json.loads(mp.read_text(encoding="utf-8")).get("landmines", {})
    else:
        problems.append("rules/manifest.json missing")
    for lm in lms:
        problems += [f"{lm.id}: {e}" for e in lm.errors]
        if not lm.cues:
            problems.append(f"{lm.id}: no cues (the landmine would be not_run)")
        fm = C.front_matter(Path(lm.path).read_text(encoding="utf-8"))
        if manifest and str(manifest.get(lm.id)) != fm.get("version"):
            problems.append(f"{lm.id}: version {fm.get('version')!r} in front matter, {manifest.get(lm.id)!r} in manifest")
    for lid in manifest:
        if lid not in ctx.landmines:
            problems.append(f"manifest lists {lid}, no rules/landmines/{lid}.md")
    if voice is None:
        problems.append("rules/voice.md missing")
    else:
        problems += voice.errors
        if not voice.banned:
            problems.append("rules/voice.md: no machine-readable banned cues")

    fixtures = load_jsonl(FIXTURES / "must_fire.jsonl", "fire", ctx)
    fixtures += load_jsonl(FIXTURES / "must_not_fire.jsonl", "no_fire", ctx)
    for lm in lms:
        for fx in lm.fixtures:
            if fx.get("expect") not in ("fire", "no_fire"):
                problems.append(f"{fx.get('id')} ({fx['_from']}): expect must be fire | no_fire")
                continue
            fixtures.append(fx)
    fixtures += load_examples(ctx)
    seen: dict[str, str] = {}
    for fx in fixtures:
        if fx["id"] in seen and seen[fx["id"]] != fx["_from"]:
            problems.append(f"duplicate fixture id {fx['id']} ({seen[fx['id']]} and {fx['_from']})")
        seen[fx["id"]] = fx["_from"]

    counts: dict[str, list[int]] = {}
    fired_shapes: set[tuple[str, str]] = set()
    failures: list[str] = []
    not_run: list[str] = []
    for fx in fixtures:
        status, detail = evaluate(fx, ctx)
        name = CHECK_ALIASES.get(fx["landmine"], fx["landmine"])
        c = counts.setdefault(name, [0, 0, 0])
        c[0 if fx["expect"] == "fire" else 1] += 1
        if fx["expect"] == "fire" and status == "ok":
            fired_shapes.add((name, (fx.get("rule") or "").strip()))
        line = f"{status:<8} {fx['expect']:<8} {fx['id']}  [{fx['_from']}]  {detail}"
        if status == "FAIL":
            failures.append(line)
            c[2] += 1
        elif status == "NOT_RUN":
            not_run.append(line)
            c[2] += 1
        elif args.verbose:
            print(line)

    for lid, lm in ctx.landmines.items():
        if counts.get(lid, [0])[0] == 0:
            problems.append(f"{lid}: zero fire fixtures; a rule that has never fired has not been tested")
        for sid in C.shape_ids(lm):
            if sid not in lm.severities:
                problems.append(f"{lid}/{sid}: no 'Severity: critical|major|minor' in the shape bullet")
            if (lid, sid) not in fired_shapes:
                problems.append(f"{lid}/{sid}: no passing fire fixture for this shape")

    for p in problems:
        print(f"PROBLEM  {p}")
    for line in failures + not_run:
        print(line)
    print()
    print(f"{'landmine or check':<22} {'fire':>5} {'no_fire':>8} {'bad':>4}")
    for name in sorted(counts):
        f, n, bad = counts[name]
        print(f"{name:<22} {f:>5} {n:>8} {bad:>4}")
    total = len(fixtures)
    print(f"\n{total} fixtures, {len(failures)} failed, {len(not_run)} not run, {len(problems)} problems")
    ok = not (failures or not_run or problems)
    print("selftest: pass" if ok else "selftest: fail")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
