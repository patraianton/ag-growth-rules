#!/usr/bin/env python3
"""Stage-1 checks for one piece of AG copy. Standard library only, Python 3.11.
Checks, flags, file formats and exit codes: tools/README.md."""
from __future__ import annotations

import argparse
import bisect
import csv
import datetime
import hashlib
import io
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

CHECKS = ["landmines", "voice", "numbers", "parity", "stray-labels", "repeats",
          "time-promises", "plain", "claims", "mark-budget", "killed-lines", "release-hash"]
PIECES = ["email", "social", "webinar", "imo-note", "how-made"]
SEVERITIES = ("critical", "major", "minor")
KINDS = ("regex", "topic", "number", "rank")
TARGETS = ("copy", "facts")
RESCUES = ("none", "bracket", "proposal", "question")
TIME_LANDMINE = "setup-timelines"
NUMBERS_LANDMINE = "numbers-and-sources"
ABSENCE_LANDMINE = "research-absence"
PROCESS_LANDMINE = "process-claims"
PLAIN_LANDMINE = "plain-language"
WORDNUM = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten".split())}

DEFAULT_SEVERITY = {"compliance-promises": "critical"}

# The ten strings round 4 searched the rendered v4 page for (kit panel/round-4.md line 57).
DEFAULT_LABELS = ["offer offer", "sync.", "export.", "Activity.", "number.", "wait.",
                  "switch.", "registration;", "shared.", "co-sign."]
DEFAULT_HEDGE = r"(?i)\b(?:about|around|roughly|nearly|almost|close, not exact|counted twice|double[- ]counted|stopped)\b|~\s?\d"
DOUBLED_OK = {"had", "that"}
MAX_MARKS = 7
REPEAT_N = 8


@dataclass
class Finding:
    check: str
    severity: str
    file: str
    line: int
    quote: str
    rule: str

    def row(self) -> str:
        q = self.quote.replace("|", "/")
        return f"{self.check} | {self.severity} | {self.file}:{self.line} | {q} | {self.rule}"


@dataclass
class CheckResult:
    result: str = "not_run"          # pass | fail | not_run | uncertain
    findings: int = 0
    note: str = ""
    required: bool = True             # False: not requested by the caller, does not move the exit code
    incomplete: bool = False          # part of the check did not run: exit 3 even with findings


@dataclass
class Cue:
    rule: str                         # "<landmine>/F1" or "voice/VB3"
    rx: re.Pattern
    severity: str
    rescues: frozenset = frozenset({"bracket"})
    kind: str = "regex"
    target: str = "copy"
    topic: str = ""
    scope: list[str] = field(default_factory=list)   # piece ids; empty = every piece
    source: str = ""                  # the pattern as written


@dataclass
class Landmine:
    id: str
    path: str
    strictness: str
    applies_to: list[str]
    cues: list[Cue]
    labels: list[str]
    fixtures: list[dict]
    errors: list[str]
    severities: dict[str, str] = field(default_factory=dict)   # shape id -> severity
    version: str = ""


@dataclass
class Voice:
    path: str
    banned: list[Cue]
    allowed: list[tuple[re.Pattern, int | None, str]]
    labels: list[str]
    errors: list[str]


class Doc:
    """Text of a piece with source line numbers, marked spans and the piece each offset belongs to."""

    def __init__(self, path: str, text: str, offsets: list[int], lines: list[int],
                 marked: list[tuple[int, int]], heads: list[tuple[int, str | None]], kind: str,
                 dotted: list[tuple[int, int]] | None = None):
        self.path, self.text, self.kind = path, text, kind
        self.dotted = sorted(dotted or [])
        self._offs, self._lines = offsets, lines
        self.marked = merge_spans(marked + bracket_spans(text))
        self._mstarts = [s for s, _ in self.marked]
        self.heads = sorted(heads or [(0, None)], key=lambda h: h[0])
        self._hoffs = [o for o, _ in self.heads]
        self._nl = [m.start() for m in re.finditer("\n", text)]

    def line_of(self, off: int) -> int:
        i = bisect.bisect_right(self._offs, off) - 1
        return self._lines[max(i, 0)] if self._lines else 1

    def is_marked(self, off: int) -> bool:
        i = bisect.bisect_right(self._mstarts, off) - 1
        return i >= 0 and self.marked[i][0] <= off < self.marked[i][1]

    def inside_mark(self, start: int, end: int) -> bool:
        """True when [start, end) lies wholly inside one marked span."""
        i = bisect.bisect_right(self._mstarts, start) - 1
        return i >= 0 and self.marked[i][0] <= start and end <= self.marked[i][1]

    def piece_at(self, off: int) -> str | None:
        i = bisect.bisect_right(self._hoffs, off) - 1
        return self.heads[i][1] if i >= 0 else None

    def section_start(self, off: int) -> int:
        i = bisect.bisect_right(self._hoffs, off) - 1
        return self.heads[i][0] if i >= 0 else 0

    def line_bounds(self, off: int) -> tuple[int, int]:
        i = bisect.bisect_left(self._nl, off)
        s = self._nl[i - 1] + 1 if i > 0 else 0
        e = self._nl[i] if i < len(self._nl) else len(self.text)
        return s, e

    def sentence_bounds(self, start: int, end: int | None = None) -> tuple[int, int]:
        end = start if end is None else end
        t = self.text
        s = start
        while s > 0:
            c = t[s - 1]
            if c == "\n" or (c in " \t" and s >= 2 and t[s - 2] in ".!?" and not _abbrev(t, s - 2)):
                break
            s -= 1
        e = max(end, s)
        n = len(t)
        while e < n:
            c = t[e]
            if c == "\n":
                break
            if c in ".!?" and (e + 1 >= n or t[e + 1] in " \t\n") and not _abbrev(t, e):
                e += 1
                break
            e += 1
        return s, e

    def sentence(self, start: int, end: int | None = None, limit: int = 160) -> str:
        s, e = self.sentence_bounds(start, end)
        q = re.sub(r"\s+", " ", self.text[s:e]).strip()
        if len(q) > limit:
            mid = max(0, start - s - limit // 3)
            q = ("..." if mid else "") + q[mid:mid + limit].strip() + "..."
        return q


ABBREV = {"e.g", "i.e", "vs", "etc", "mr", "ms", "dr", "no", "u.s"}


def _abbrev(t: str, dot: int) -> bool:
    if t[dot] != ".":
        return False
    w = re.search(r"([\w.]{1,4})$", t[max(0, dot - 4):dot])
    return bool(w) and w.group(1).lower().lstrip(".") in ABBREV


def merge_spans(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for s, e in sorted(spans):
        if out and s <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], e))
        else:
            out.append((s, e))
    return out


def bracket_spans(text: str) -> list[tuple[int, int]]:
    """[square brackets] are marks. Markdown link text [x](url) is not. A blank line resets."""
    spans, stack = [], []
    for i, c in enumerate(text):
        if c == "[":
            stack.append(i)
        elif c == "]" and stack:
            s = stack.pop()
            if not text.startswith("(", i + 1):
                spans.append((s, i + 1))
        elif c == "\n" and text.startswith("\n", i + 1):
            stack.clear()
    return spans


def classify_heading(h: str) -> str | None:
    h = h.strip().lower()
    if h in PIECES:
        return h
    if re.search(r"how (this|it) was made", h):
        return "how-made"
    if re.search(r"\bnote\b.*\bimo\b|\bimo\b.*\bnote\b", h):
        return "imo-note"
    if "webinar" in h or "agenda" in h:
        return "webinar"
    if "social" in h or "linkedin" in h:
        return "social"
    if "email" in h:
        return "email"
    return None


def md_doc(text: str, path: str = "<text>", piece: str | None = None) -> Doc:
    offs, lines = [0], [1]
    for m in re.finditer(r"\n", text):
        offs.append(m.end())
        lines.append(len(lines) + 1)
    heads: list[tuple[int, str | None]] = [(0, piece)]
    for m in re.finditer(r"^##(?!#)\s*(.+)$", text, re.M):
        heads.append((m.start(), classify_heading(m.group(1)) or piece))
    return Doc(path, text, offs, lines, [], heads, "md")


BLOCK = {"p", "li", "ul", "ol", "div", "section", "article", "aside", "header", "footer", "main",
         "h1", "h2", "h3", "h4", "h5", "h6", "tr", "td", "th", "table", "thead", "tbody", "br",
         "blockquote", "details", "summary", "figure", "figcaption", "nav", "dl", "dt", "dd", "hr", "pre"}
SKIP = {"script", "style", "head", "title", "svg", "noscript", "template", "sup"}
VOID = {"br", "img", "hr", "meta", "link", "input", "source", "wbr", "col", "area", "base", "embed", "track"}


class _Extract(HTMLParser):
    """Visible text of a page. With brackets=True a dotted span is also wrapped in [ ]."""

    def __init__(self, dotted: str, brackets: bool):
        super().__init__(convert_charrefs=True)
        self.dotted, self.brackets = dotted, brackets
        self.buf: list[str] = []
        self.size = 0
        self.offs: list[int] = []
        self.lines: list[int] = []
        self.marked: list[tuple[int, int]] = []
        self.stack: list[tuple[str, bool, int]] = []
        self.skip = 0
        self.heads: list[tuple[int, str | None]] = [(0, None)]
        self.h2_start: int | None = None

    def _emit(self, s: str):
        if not s:
            return
        self.offs.append(self.size)
        self.lines.append(self.getpos()[0])
        self.buf.append(s)
        self.size += len(s)

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
            return
        if self.skip:
            return
        if tag in BLOCK:
            self._emit("\n")
        if tag == "h2":
            self.h2_start = self.size
        if tag in VOID:
            return
        is_mark = self.dotted in (dict(attrs).get("class") or "").split()
        if is_mark and self.brackets:
            self._emit("[")
        self.stack.append((tag, is_mark, self.size))

    def handle_startendtag(self, tag, attrs):
        if not self.skip and tag in BLOCK:
            self._emit("\n")

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip or tag in VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                _, is_mark, start = self.stack[i]
                del self.stack[i:]
                if is_mark:
                    if self.brackets:
                        self._emit("]")
                    self.marked.append((start, self.size))
                break
        if tag == "h2" and self.h2_start is not None:
            self.heads.append((self.h2_start, classify_heading("".join(self.buf)[self.h2_start:])))
            self.h2_start = None
        if tag in BLOCK:
            self._emit("\n")

    def handle_data(self, data):
        if not self.skip:
            self._emit(re.sub(r"[ \t\r\n\f\v]+", " ", data))


def html_doc(html_text: str, path: str = "<html>", dotted: str = "tbc", brackets: bool = False) -> Doc:
    p = _Extract(dotted, brackets)
    p.feed(html_text)
    p.close()
    text = "".join(p.buf)
    return Doc(path, text, p.offs or [0], p.lines or [1], p.marked, p.heads, "html", p.marked)


def facts_doc(text: str, path: str = "<facts>") -> Doc:
    """Data rows of every table with a "claim" column, refute column blanked; other lines blanked,
    line numbers kept. A text with no such table (one fixture row) is used whole."""
    lines = text.split("\n")
    keep = [False] * len(lines)
    i = 0
    while i < len(lines) - 1:
        if lines[i].lstrip().startswith("|") and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            head = _split_row(lines[i])
            is_facts = any("claim" in h.lower() for h in head)
            blank = [k for k, h in enumerate(head) if "refute" in h.lower()]
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                keep[j] = is_facts
                if is_facts and blank:
                    cells = _split_row(lines[j])
                    for k in blank:
                        if k < len(cells):
                            cells[k] = ""
                    lines[j] = "| " + " | ".join(cells) + " |"
                j += 1
            i = j
        else:
            i += 1
    if any(keep):
        text = "\n".join(ln if k else "" for ln, k in zip(lines, keep))
    return md_doc(text, path)


def load_doc(path: Path, dotted: str = "tbc", piece: str | None = None, brackets: bool = False) -> Doc:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".html", ".htm"):
        return html_doc(text, str(path), dotted, brackets)
    return md_doc(text, str(path), piece)


FENCE = re.compile(r"^```[ \t]*([A-Za-z][\w-]*)[^\n]*\n(.*?)^```[ \t]*$", re.M | re.S)
FM = re.compile(r"\A---[ \t]*\n(.*?)\n---[ \t]*\n", re.S)
ID_PREFIX = re.compile(r"^(?P<id>[A-Z][A-Za-z]{0,2}\d+[a-z]?)\s*(?:[:|]\s+|\t+)(?P<rest>.+)$")


def front_matter(text: str) -> dict[str, str]:
    m = FM.match(text)
    fm: dict[str, str] = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line and not line.startswith((" ", "\t", "#")):
                k, v = line.split(":", 1)
                fm[k.strip()] = v.split(" #")[0].strip().strip("'\"")
    return fm


def fenced(text: str, name: str) -> list[str]:
    return [m.group(2) for m in FENCE.finditer(text) if m.group(1).lower() == name]


def block_lines(block: str) -> list[str]:
    out = []
    for line in block.splitlines():
        s = line.strip()
        if not s or s.startswith("#") and (len(s) == 1 or s[1] == " "):
            continue
        out.append(s)
    return out


def compile_rx(pat: str, where: str, errors: list[str], flags: int = re.MULTILINE) -> re.Pattern | None:
    if CONTROL.search(pat):
        errors.append(f"{where}: control character in pattern {pat!r}")
        return None
    try:
        rx = re.compile(pat, flags)
    except re.error as e:
        errors.append(f"{where}: does not compile ({e}): {pat!r}")
        return None
    if rx.search("") is not None:
        errors.append(f"{where}: matches the empty string: {pat!r}")
        return None
    return rx


def machine_spans(clause: str) -> list[tuple[str, bool]]:
    """Backticked spans that stand alone in a prose cue clause: only separators (·  ,  ;  |  or) or
    "regex" before, a separator, "(", "." or the end after. Returns (pattern, marked 'regex')."""
    out: list[tuple[str, bool]] = []
    pos = 0
    for m in re.finditer(r"`([^`\n]+)`", clause):
        b = re.sub(r"[·,;|]|\bor\b", " ", clause[pos:m.start()]).strip().lower()
        regex_marked = b.endswith("regex")
        if regex_marked:
            b = b[: -len("regex")].strip()
        a = clause[m.end():].lstrip()
        ok_after = a == "" or a[0] in "·,;|(." or a.lower().startswith(("or ", "regex "))
        if b == "" and ok_after:
            out.append((m.group(1), regex_marked))
        pos = m.end()
    return out


def scope_from(text: str) -> list[str]:
    m = re.search(r"\bin\s+((?:[\w-]+(?:,\s*|\s+and\s+|\s+or\s+)?)+)", text)
    if not m:
        return []
    return [p for p in PIECES if re.search(r"(?<![\w-])" + re.escape(p) + r"(?![\w-])", m.group(1))]


def never_rescued(text: str) -> set[str]:
    ids: set[str] = set()
    for p in (r"brackets do not rescue ((?:F\d+(?:,\s*|\s+and\s+|\s+or\s+)?)+)",
              r"((?:F\d+(?:,\s*|\s+and\s+)?)+)\s+(?:are|is)\s+never rescued"):
        for m in re.finditer(p, text, re.I):
            ids.update(re.findall(r"F\d+", m.group(1)))
    return ids


def rule_severities(body: str) -> dict[str, str]:
    """'Severity: major' inside an F-bullet ("- **F1 ...** ... Severity: major.")."""
    out: dict[str, str] = {}
    for m in re.finditer(r"^[ \t]*[-*][ \t]+\*\*(F\d+)\b([^\n]*(?:\n[ \t]+\S[^\n]*)*)", body, re.M):
        s = re.search(r"Severity:\s*(critical|major|minor)", m.group(2), re.I)
        if s:
            out[m.group(1)] = s.group(1).lower()
    return out


def parse_cue_row(line: str, lid: str, n: int, sev: dict[str, str], default_sev: str, applies: list[str],
                  errors: list[str]) -> Cue | None:
    """One line of a ```cues``` block (format: tools/README.md)."""
    parts = [p.strip() for p in line.split("|", 4)]
    if len(parts) == 5 and parts[1] in TARGETS and parts[3] in KINDS:
        rid, target, resc, kind, pat = parts
        rescues = frozenset(r.strip() for r in resc.split(",") if r.strip() and r.strip() != "none")
        bad = [r for r in rescues if r not in RESCUES]
        if bad:
            errors.append(f"{lid}/{rid}: unknown rescue {bad}")
    else:
        m = ID_PREFIX.match(line)
        rid, pat = (m.group("id"), m.group("rest").strip()) if m else (f"cue{n}", line)
        target, kind, rescues = "copy", "regex", frozenset({"bracket"})
    topic = ""
    if kind == "topic":
        if "=" not in pat:
            errors.append(f"{lid}/{rid}: kind topic needs name=pattern")
            return None
        topic, pat = pat.split("=", 1)
        topic = topic.strip()
    rx = compile_rx(pat, f"{lid}/{rid}", errors)
    if not rx:
        return None
    return Cue(f"{lid}/{rid}", rx, sev.get(rid, default_sev), rescues, kind, target, topic, applies, pat)


def load_landmine(path: Path) -> Landmine:
    text = path.read_text(encoding="utf-8")
    fm = front_matter(text)
    lid = fm.get("id") or path.stem
    errors: list[str] = []
    strict = fm.get("strictness", "remove").strip()
    applies = [p.strip() for p in fm.get("applies_to", "").strip("[]").split(",") if p.strip()]
    fm_sev = fm.get("severity", "").lower()
    default_sev = fm_sev if fm_sev in SEVERITIES else DEFAULT_SEVERITY.get(lid, "major")
    body = FM.sub("", text, count=1)
    sev = rule_severities(body)
    no_rescue = never_rescued(text)
    cues: list[Cue] = []

    blocks = fenced(text, "cues")
    n = 0
    for block in blocks:
        for line in block_lines(block):
            n += 1
            cue = parse_cue_row(line, lid, n, sev, default_sev, applies, errors)
            if cue:
                cues.append(cue)

    if not any(block_lines(b) for b in blocks):
        # fallback: prose "Cues: `rx` · `rx`" inside an F-bullet; case-insensitive
        for m in re.finditer(r"^[ \t]*[-*][ \t]+\*\*(?P<id>F\d+)\b(?P<b>[^\n]*(?:\n[ \t]+\S[^\n]*)*)", body, re.M):
            rid, bullet = m.group("id"), m.group("b")
            cm = re.search(r"\bCues?:\s*(.*)", bullet, re.I | re.S)
            if not cm:
                continue
            clause = re.split(r"\b(?:Class|Severity|Strictness):", re.sub(r"\s*\n\s*", " ", cm.group(1)))[0]
            for pat, _ in machine_spans(clause):
                rx = compile_rx(pat, f"{lid}/{rid}", errors, re.IGNORECASE | re.MULTILINE)
                if rx:
                    resc = frozenset() if rid in no_rescue else frozenset({"bracket"})
                    cues.append(Cue(f"{lid}/{rid}", rx, sev.get(rid, default_sev), resc, "regex", "copy",
                                    "", applies, pat))

    fixtures: list[dict] = []
    for block in fenced(text, "fixtures"):
        for k, line in enumerate(block_lines(block), start=1):
            try:
                fx = json.loads(line)
                fx.setdefault("landmine", lid)
                fx["_from"] = f"{path.name} fixtures line {k}"
                fixtures.append(fx)
            except json.JSONDecodeError as e:
                errors.append(f"{lid}: fixtures line {k} is not JSON ({e})")
    labels = [x for b in fenced(text, "labels") for x in block_lines(b)]
    if strict not in ("remove", "cite-or-cut", "rewrite"):
        errors.append(f"{lid}: strictness must be remove | cite-or-cut | rewrite, got {strict!r}")
    return Landmine(lid, str(path), strict, applies, cues, labels, fixtures, errors, sev,
                    fm.get("version", ""))


def shape_ids(lm: Landmine) -> list[str]:
    """F-ids of the '- **F1 ...' bullets."""
    body = FM.sub("", Path(lm.path).read_text(encoding="utf-8"), count=1)
    return sorted(set(re.findall(r"^[ \t]*[-*][ \t]+\*\*(F\d+)\b", body, re.M)), key=lambda s: int(s[1:]))


def load_landmines(directory: Path) -> list[Landmine]:
    if not directory.is_dir():
        return []
    return [load_landmine(p) for p in sorted(directory.glob("*.md")) if p.name.lower() != "readme.md"]


def _split_row(line: str) -> list[str]:
    """Split a table row on | outside backticks (regexes carry | inside backticks)."""
    s = line.strip()
    s = s[1:] if s.startswith("|") else s
    s = s[:-1] if s.endswith("|") else s
    cells, cur, tick = [], [], False
    for ch in s:
        if ch == "`":
            tick = not tick
        if ch == "|" and not tick:
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    cells.append("".join(cur).strip())
    return cells


def md_tables(text: str):
    """Yield (header cells, rows of cells) for each pipe table."""
    lines = text.splitlines()
    i = 0
    while i < len(lines) - 1:
        if lines[i].lstrip().startswith("|") and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            head = _split_row(lines[i])
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                rows.append(_split_row(lines[j]))
                j += 1
            yield head, rows
            i = j
        else:
            i += 1


def _phrase_rx(phrase: str) -> str:
    esc = re.escape(phrase)
    if re.match(r"\w", phrase):
        esc = r"\b" + esc
    if re.search(r"\w$", phrase):
        esc += r"\b"
    return esc


def load_voice(path: Path) -> Voice:
    """Banned cues and counted exceptions (format: tools/README.md, voice.md)."""
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    banned: list[Cue] = []
    allowed: list[tuple[re.Pattern, int | None, str]] = []
    ci = re.IGNORECASE | re.MULTILINE
    for n, line in enumerate((x for b in fenced(text, "banned") for x in block_lines(b)), start=1):
        m = ID_PREFIX.match(line)
        rid, pat = (m.group("id"), m.group("rest").strip()) if m else (f"banned{n}", line)
        rx = compile_rx(pat, f"voice/{rid}", errors, ci)
        if rx:
            banned.append(Cue(f"voice/{rid}", rx, "minor", frozenset(), source=pat))
    for head, rows in md_tables(text):
        cols = [i for i, h in enumerate(head) if "cue" in h.lower()]
        if not cols:
            continue
        c = cols[0]
        for k, row in enumerate(rows, start=1):
            if c >= len(row):
                continue
            rid = row[0].strip("*` ") or f"row{k}"
            cell = row[c]
            scope = scope_from(cell.split("`")[-1]) if "`" in cell else []
            if re.search(r"allowed in AG-voice pieces", " ".join(row), re.I):
                scope = ["how-made"]
            flags = re.MULTILINE if "case-sensitive" in cell.lower() else ci
            for pat, is_rx in machine_spans(cell):
                rx = compile_rx(pat if is_rx else _phrase_rx(pat), f"voice/{rid}", errors, flags)
                if rx:
                    banned.append(Cue(f"voice/{rid}", rx, "minor", frozenset(), scope=scope, source=pat))
    for line in (x for b in fenced(text, "allowed") for x in block_lines(b)):
        cnt: int | None = None
        pat = line
        for form in (r"^(?P<n>\d+)\s*[|:]\s*(?P<p>.+)$", r"^(?P<p>.+?)\s*\|\s*(?:max\s*)?(?P<n>\d+)\s*$",
                     r"^(?P<p>.+?)\s+\((?:max\s*)?(?P<n>\d+)\)\s*$"):
            m = re.match(form, line)
            if m:
                cnt, pat = int(m.group("n")), m.group("p").strip()
                break
        rx = compile_rx(pat, "voice/allowed", errors, ci)
        if rx:
            allowed.append((rx, cnt, pat))
    labels = [x for b in fenced(text, "labels") for x in block_lines(b)]
    return Voice(str(path), banned, allowed, labels, errors)


@dataclass
class Numbers:
    records: list[dict]                   # {id, value, unit, precision, ...}
    values: dict[float, list[dict]]       # value -> records
    computed: list[dict]                  # {kind: rank|share, phrase, table, row(s), result}
    tables: dict[str, dict[str, float]]   # table id -> {row: value}
    strings: list[str]                    # text/phrase strings, lowercased


def parse_number(s: str) -> float | None:
    m = re.fullmatch(r"[~≈]?\s*\$?\s*(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d+))?\s*(%|[kKM]|\+)?", s)
    if not m:
        return None
    v = float(m.group(1).replace(",", "") + ("." + m.group(2) if m.group(2) else ""))
    suf = m.group(3) or ""
    return v * 1000 if suf in ("k", "K") else v * 1_000_000 if suf == "M" else v


def numbers_from(data) -> Numbers:
    """A list of records or an object holding lists of records. Without any "value" key the file is
    walked and every bare number counts."""
    records: list[dict] = []
    computed: list[dict] = []
    tables: dict[str, dict[str, float]] = {}
    strings: list[str] = []

    def walk(node):
        if isinstance(node, dict):
            kind = str(node.get("kind", "")).lower()
            if kind == "table" and "rows" in node:
                rows = node["rows"]
                if isinstance(rows, list):
                    rows = {str(r.get("row", r.get("name", i))): r.get("value") for i, r in enumerate(rows)
                            if isinstance(r, dict)}
                tables[str(node.get("id"))] = {str(k): float(v) for k, v in rows.items()
                                               if isinstance(v, (int, float)) and not isinstance(v, bool)}
                return
            if kind in ("rank", "share"):
                computed.append(node)
                if node.get("phrase"):
                    strings.append(str(node["phrase"]).lower())
                return
            if "value" in node:
                v = node["value"]
                fv = float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else \
                    parse_number(v.strip()) if isinstance(v, str) else None
                if fv is not None:
                    rec = dict(node)
                    rec["_value"] = round(fv, 6)
                    rec["precision"] = str(node.get("precision", "exact")).lower()
                    records.append(rec)
                for k in ("text", "phrase"):
                    if isinstance(node.get(k), str) and len(node[k]) >= 6:
                        strings.append(node[k].lower())
                return
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(data)
    if not records and not computed and not tables:
        def bare(node, key=""):
            if isinstance(node, dict):
                for k, v in node.items():
                    bare(v, str(k).lower())
            elif isinstance(node, list):
                for v in node:
                    bare(v, key)
            elif isinstance(node, (int, float)) and not isinstance(node, bool):
                if not (key.endswith("line") or key in ("version", "year", "page", "id")):
                    records.append({"id": key, "_value": round(float(node), 6), "precision": "exact"})
        bare(data)
    values: dict[float, list[dict]] = {}
    for r in records:
        values.setdefault(r["_value"], []).append(r)
    return Numbers(records, values, computed, tables, strings)


def load_numbers(path: Path) -> Numbers:
    return numbers_from(json.loads(path.read_text(encoding="utf-8")))


def numbers_subset(numbers: Numbers | None, ids: list[str]) -> Numbers:
    recs = [r for r in (numbers.records if numbers else []) if r.get("id") in ids]
    comp = [r for r in (numbers.computed if numbers else []) if r.get("id") in ids]
    return numbers_from(recs + comp + [{"kind": "table", "id": k, "rows": v}
                                       for k, v in (numbers.tables.items() if numbers else [])])


def recompute(rec: dict, tables: dict[str, dict[str, float]]) -> bool | None:
    """True when a rank/share record's result follows from its table; None when the table is missing."""
    t = tables.get(str(rec.get("table")))
    if not t:
        return None
    try:
        if str(rec.get("kind")).lower() == "rank":
            order = sorted(t, key=lambda k: -t[k])
            return order.index(str(rec["row"])) + 1 == int(rec["result"])
        rows = rec.get("rows") or [rec.get("row")]
        share = 100.0 * sum(t[str(r)] for r in rows) / sum(t.values())
        return abs(share - float(rec["result"])) < 0.5
    except (KeyError, ValueError, ZeroDivisionError):
        return False


MONTHS = (r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?"
          r"|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)")
NOT_CLAIMS = [
    r"https?://\S+", r"\]\([^)]*\)", r"`[^`\n]*`", r"<[^>\n]+>",
    r"\"[^\"\n]*\"", r"“[^”\n]*”",                 # inside quotation marks: a quote record
    r"\(?\b\d{3}\)?[ .-]\d{3}-\d{4}\b",                          # phone numbers
    r"\b\d{4}-\d{2}-\d{2}\b", r"\b\d{1,2}\.\d{1,2}\.\d{4}\b",       # ISO and dotted dates
    r"\b\d{1,2}:\d{2}\b", r"\b\d{1,2}\s?(?:AM|PM|a\.m\.|p\.m\.)",  # times of day, agenda minutes
    MONTHS + r"\.?\s+\d{1,2}(?:st|nd|rd|th)?\b", r"\b\d{1,2}(?:st|nd|rd|th)?\s+" + MONTHS + r"\b",
    r"(?m)^[ \t>]*(?:#+[ \t]*)?\d+[.)][ \t]",                    # list and heading numbering
    r"(?m)^#+[ \t]*\d+\b",
    r"(?i)\b(?:section|step|question|round|side note|note|bullet|part|chapter|figure|table|row|lines?"
    r"|page|version|lane|item)\s*\d+(?:\s*(?:-|to|and)\s*\d+)?\b",
    r"\b[FPDNAv]\d+\b", r"#\w+",
    r"\b[A-Z][A-Za-z]+\s\d+\.\d+\b",                          # product versions ("GrantAI 2.0")
]
NUM = re.compile(r"(?<![\w.,/#$-])(\$?)(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d+))?(%|[kKM](?![A-Za-z])|\+)?(?![\w])")


def number_tokens(doc: Doc):
    """Yield (offset, raw, value) for every number that is a claim."""
    work = list(doc.text)
    for pat in NOT_CLAIMS:
        for m in re.finditer(pat, doc.text):
            for i in range(m.start(), m.end()):
                if work[i] != "\n":
                    work[i] = " "
    t = "".join(work)
    for m in NUM.finditer(t):
        raw, digits = m.group(0), m.group(2)
        if not (m.group(1) or m.group(3) or m.group(4)) and "," not in digits \
                and len(digits) == 4 and digits[:2] in ("19", "20"):
            continue
        if m.group(1) and doc.is_marked(m.start()):
            continue
        v = parse_number(raw)
        if v is not None:
            yield m.start(), raw, v


def read_claims(text: str) -> list[dict]:
    lines = [ln for ln in text.splitlines() if not ln.lstrip().startswith("#")]
    rows = []
    for i, r in enumerate(csv.DictReader(io.StringIO("\n".join(lines))), start=2):
        rows.append({"_line": i, **{(k or "").strip().lower(): (v or "").strip()
                                    for k, v in r.items() if isinstance(v, str) or v is None}})
    return rows


def _col(row: dict, *names: str) -> str:
    for n in names:
        for k, v in row.items():
            if k != "_line" and n in k:
                return v if isinstance(v, str) else ""
    return ""


def norm_status(s: str) -> str:
    return re.sub(r"[\s_]+", "-", s.strip().upper())


def _in_scope(doc: Doc, off: int, scope: list[str]) -> bool:
    if not scope:
        return True
    p = doc.piece_at(off)
    return p is None or p in scope


def _rescued(doc: Doc, cue: Cue, m: re.Match) -> bool:
    ls, le = doc.line_bounds(m.start())
    line = doc.text[ls:le]
    if "bracket" in cue.rescues and doc.inside_mark(m.start(), m.end()):
        return True
    if "proposal" in cue.rescues and re.search(r"\bmy proposal\b", line, re.I):
        return True
    if "question" in cue.rescues and "?" in line:
        return True
    return False


def _clause(doc: Doc, m: re.Match) -> str:
    ls, le = doc.line_bounds(m.start())
    line = doc.text[ls:le]
    a, b = m.start() - ls, m.end() - ls
    s = max(line.rfind(c, 0, a) for c in ";.:") + 1
    ends = [i for i in (line.find(c, b) for c in ";.") if i >= 0]
    e = min(ends) if ends else len(line)
    c = re.sub(r"[\[\]*_`>]", "", line[s:e]).lower()
    return re.sub(r"[^a-z0-9' ]+", " ", c).split("- ")[-1].strip()


def check_cues(doc: Doc, landmines: list[Landmine], check: str, numbers: Numbers | None = None,
               target: str = "copy") -> tuple[list[Finding], list[str]]:
    """Regex, rank and topic cues of the given target. Returns (findings, notes)."""
    out: list[Finding] = []
    notes: list[str] = []
    seen: set[tuple[str, int]] = set()
    for lm in landmines:
        topics: dict[str, list[tuple[str | None, str, int, re.Match]]] = {}
        topic_cue: dict[str, Cue] = {}
        for cue in lm.cues:
            if cue.target != target or cue.kind == "number":
                continue
            for m in cue.rx.finditer(doc.text):
                if m.start() == m.end() or not _in_scope(doc, m.start(), cue.scope):
                    continue
                if cue.kind == "topic":
                    topics.setdefault(cue.topic, []).append((doc.piece_at(m.start()), _clause(doc, m),
                                                             m.start(), m))
                    topic_cue[cue.topic] = cue
                    continue
                if _rescued(doc, cue, m):
                    continue
                ls, le = doc.line_bounds(m.start())
                if cue.kind == "rank":
                    line = doc.text[ls:le].lower()
                    recs = [r for r in (numbers.computed if numbers else [])
                            if str(r.get("phrase", "")).lower() and str(r["phrase"]).lower() in line]
                    if recs:
                        ok = recompute(recs[0], numbers.tables)
                        if ok:
                            continue
                        if ok is None:
                            notes.append(f"{cue.rule}: table {recs[0].get('table')!r} missing for "
                                         f"rank record {recs[0].get('id', recs[0].get('phrase'))}")
                key = (cue.rule, ls)
                if key in seen:
                    continue
                seen.add(key)
                out.append(Finding(check, cue.severity, doc.path, doc.line_of(m.start()),
                                   doc.sentence(m.start(), m.end()), cue.rule))
        for name, hits in topics.items():
            pieces = {p for p, _, _, _ in hits}
            clauses = {c for _, c, _, _ in hits}
            if len(pieces) >= 2 and len(clauses) >= 2:
                cue = topic_cue[name]
                first = {}
                for p, c, off, m in hits:
                    first.setdefault(p, (c, off))
                desc = " vs ".join(f"{p or '?'}:{doc.line_of(off)} '{c[:60]}'" for p, (c, off) in first.items())
                off = sorted(o for _, o in first.values())[1]
                out.append(Finding(check, cue.severity, doc.path, doc.line_of(off),
                                   f"topic {name}: {desc}", cue.rule))
    return out, notes


def check_numbers(doc: Doc, numbers: Numbers, landmine: Landmine | None = None) -> list[Finding]:
    """F1 no record; F4 a value a record lists under "conflicts" ("30 Shorts" against a record of 38 that lists 30);
    F3 not exact and no hedge in the line or earlier in the section."""
    f1, f3, hedge, sev1, sev3 = "numbers/no-record", "numbers/precision", None, "major", "major"
    f4, sev4 = "numbers/two-values", "major"
    if landmine:
        f4, sev4 = f"{landmine.id}/F4", landmine.severities.get("F4", "major")
        for c in landmine.cues:
            if c.kind != "number":
                continue
            if c.rx.search("1,927 and 93"):
                f1, sev1 = c.rule, c.severity
            else:
                f3, sev3, hedge = c.rule, c.severity, c.rx
    hedge = hedge or re.compile(DEFAULT_HEDGE)
    out: list[Finding] = []
    for off, raw, v in number_tokens(doc):
        cands = [round(v, 6)] + ([round(v / 1000, 6)] if raw.lower().endswith("k") else [])
        recs = next((numbers.values[c] for c in cands if c in numbers.values), None)
        if raw.endswith("%"):
            # a percentage is a share: a record with unit %, or a computed share whose phrase is in the line
            recs = [r for r in recs or [] if str(r.get("unit", "")).strip() in ("%", "percent")] or None
            ls, le = doc.line_bounds(off)
            line = doc.text[ls:le].lower()
            for c in numbers.computed:
                if str(c.get("kind")).lower() == "share" and str(c.get("phrase", "")).lower() in line \
                        and recompute(c, numbers.tables) and abs(float(c.get("result", -1)) - v) < 0.5:
                    recs = [{"id": c.get("id"), "precision": str(c.get("precision", "approximate")).lower(),
                             "unit": "%", "_value": v}]
                    break
        sent = doc.sentence(off)
        if not recs:
            same = [r for r in numbers.records
                    if any(isinstance(c, (int, float)) and round(float(c), 6) in cands for c in r.get("conflicts") or [])]
            if same:
                held = ", ".join(f"{r['_value']:g} {r.get('unit', '')} ({r.get('id', '?')})" for r in same[:3])
                out.append(Finding("numbers", sev4, doc.path, doc.line_of(off),
                                   f"{raw} printed; the record says {held}: {sent}", f4))
            else:
                out.append(Finding("numbers", sev1, doc.path, doc.line_of(off),
                                   f"{raw} not in numbers.json: {sent}", f1))
            continue
        ls, le = doc.line_bounds(off)
        after = doc.text[off:le].lower()[:40]
        rec = next((r for r in recs if str(r.get("unit", "")).lower()
                    and str(r["unit"]).lower().rstrip("s") in after), recs[0])
        if rec["precision"] == "exact":
            continue
        if hedge.search(doc.text[ls:le]) or hedge.search(doc.text[doc.section_start(off):ls]):
            continue
        out.append(Finding("numbers", sev3, doc.path, doc.line_of(off),
                           f"{raw} is {rec['precision']} ({rec.get('id', '?')}), printed without its hedge: {sent}", f3))
    return out


def check_voice(doc: Doc, voice: Voice) -> list[Finding]:
    out: list[Finding] = []
    used = [0] * len(voice.allowed)
    seen: set[tuple[str, int]] = set()
    # blank URLs and link targets, keep offsets
    text = re.sub(r"https?://\S+|\]\([^)]*\)", lambda m: " " * len(m.group(0)), doc.text)
    for cue in voice.banned:
        for m in cue.rx.finditer(text):
            if m.start() == m.end() or not _in_scope(doc, m.start(), cue.scope):
                continue
            s0, s1 = doc.sentence_bounds(m.start(), m.end())
            exc = next((i for i, (arx, _, _) in enumerate(voice.allowed)
                        if any(a.start() < m.end() and m.start() < a.end() for a in arx.finditer(doc.text, s0, s1))),
                       None)
            rule = cue.rule
            if exc is not None:
                used[exc] += 1
                cnt = voice.allowed[exc][1]
                if cnt is None or used[exc] <= cnt:
                    continue
                rule = f"voice/allowed-over-count:{voice.allowed[exc][2]}"
            if (rule, s0) in seen:                 # one finding per rule per sentence
                continue
            seen.add((rule, s0))
            out.append(Finding("voice", cue.severity, doc.path, doc.line_of(m.start()),
                               f"{m.group(0)!r} in: {doc.sentence(m.start(), m.end())}", rule))
    return out


PUNCT_MAP = str.maketrans({"—": "-", "–": "-", "’": "'", "‘": "'", "“": '"',
                           "”": '"', " ": " ", "→": "->", "·": " "})


def norm_parity(s: str) -> str:
    """Letters and digits only: the page glues inline elements ("0:00Welcome") and drops markdown."""
    s = s.translate(PUNCT_MAP)
    s = re.sub(r"\]\([^)]*\)", "]", s)
    s = re.sub(r"(?m)^[ \t]*(?:#+|[-*>]|\d+[.)])[ \t]+", " ", s)
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def doc_sentences(doc: Doc, min_words: int = 4):
    t, i, n = doc.text, 0, len(doc.text)
    while i < n:
        while i < n and t[i].isspace():
            i += 1
        if i >= n:
            break
        s, e = doc.sentence_bounds(i)
        e = max(e, i + 1)
        raw = t[s:e]
        if not (doc.kind == "md" and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", raw)) \
                and len(re.findall(r"[A-Za-z]{2,}", raw)) >= min_words:
            yield s, raw
        i = e


def check_parity(piece: Doc, page: Doc) -> list[Finding]:
    out: list[Finding] = []
    pt, gt = norm_parity(piece.text), norm_parity(page.text)
    for doc, other, where in ((piece, gt, "piece-only"), (page, pt, "page-only")):
        for off, raw in doc_sentences(doc):
            ns = norm_parity(raw)
            if ns and ns not in other:
                out.append(Finding("parity", "minor", doc.path, doc.line_of(off),
                                   re.sub(r"\s+", " ", raw).strip()[:160], f"parity/{where}"))
    return out


def check_stray(doc: Doc, labels: list[str], source: Doc | None = None) -> list[Finding]:
    """Doubled words; on a page, the label strings. A label hit whose whole sentence is also written in the
    markdown source (`source`, parity-normalised) is the author's sentence end, not a printed label."""
    out: list[Finding] = []
    src = norm_parity(source.text) if source is not None else ""
    for m in re.finditer(r"\b([A-Za-z][A-Za-z'-]*)[ \t]+\1\b", doc.text, re.I):
        if m.group(1).lower() not in DOUBLED_OK:
            out.append(Finding("stray-labels", "major", doc.path, doc.line_of(m.start()),
                               f"{m.group(0)!r} in: {doc.sentence(m.start(), m.end())}", "stray/doubled-word"))
    if doc.kind == "html":
        for lab in labels:
            for m in re.finditer(re.escape(lab), doc.text):
                s, e = doc.sentence_bounds(m.start(), m.end())
                ns = norm_parity(doc.text[s:e])
                if src and ns and ns in src:
                    continue
                out.append(Finding("stray-labels", "major", doc.path, doc.line_of(m.start()),
                                   f"{lab!r} in: {doc.sentence(m.start(), m.end())}", f"stray/label:{lab}"))
    return out


def check_repeats(doc: Doc, n: int = REPEAT_N) -> list[Finding]:
    # URLs and link targets are not prose: two links to pages on one site share the address (same blanking as voice)
    text = re.sub(r"https?://\S+|\]\([^)]*\)", lambda m: " " * len(m.group(0)), doc.text)
    words = [(m.start(), m.group(0).lower()) for m in re.finditer(r"[A-Za-z0-9$%']+", text)]
    first: dict[tuple[str, ...], int] = {}
    hits: dict[int, int] = {}
    for j in range(len(words) - n + 1):
        g = tuple(w for _, w in words[j:j + n])
        if g not in first:
            first[g] = j
        elif j >= first[g] + n:
            hits[j] = first[g]
    out: list[Finding] = []
    js = sorted(hits)
    k = 0
    while k < len(js):
        j = end = js[k]
        while k + 1 < len(js) and js[k + 1] == end + 1 and hits[js[k + 1]] == hits[end] + 1:
            k += 1
            end = js[k]
        run = " ".join(w for _, w in words[j:end + n])
        out.append(Finding("repeats", "minor", doc.path, doc.line_of(words[j][0]),
                           f"{run[:150]} (first at line {doc.line_of(words[hits[j]][0])})", f"repeats/{n}-words"))
        k += 1
    return out


def _table_blocks(text: str):
    """Yield (header line index, header cells, [(line index, cells)])."""
    lines = text.split("\n")
    i = 0
    while i < len(lines) - 1:
        if lines[i].lstrip().startswith("|") and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                rows.append((j, _split_row(lines[j])))
                j += 1
            yield i, _split_row(lines[i]), rows
            i = j
        else:
            i += 1


def coverage_rows(text: str) -> dict[str, dict[str, str]]:
    """COV-n -> {lowercased header: cell} from every table in coverage.md."""
    out: dict[str, dict[str, str]] = {}
    for _, head, rows in _table_blocks(text):
        h = [x.strip().lower() for x in head]
        for _, cells in rows:
            if cells and re.fullmatch(r"COV-\d+", cells[0].strip()):
                out[cells[0].strip()] = {h[k]: (cells[k] if k < len(cells) else "") for k in range(len(h))}
    return out


def _cell(row: dict[str, str], word: str) -> str:
    return next((v for k, v in row.items() if word in k), "")


def _lead_int(s: str) -> int | None:
    m = re.match(r"\s*(\d[\d,]*)", s)
    return int(m.group(1).replace(",", "")) if m else None


def uncovered(row: dict[str, str]) -> bool:
    """Nothing keyword-searched, and not every item read in full."""
    searched = _cell(row, "search").strip().lower()
    if searched and not re.match(r"^(?:0(?!\d)|none\b|no\b|-$)", searched):
        return False
    read, total = _lead_int(_cell(row, "read")), _lead_int(_cell(row, "total"))
    return not (read is not None and total is not None and read >= total > 0)


VERDICT_RE = re.compile(r"\b(held|overturned|unverifiable)\b", re.I)


def refute_verdict(cell: str) -> str:
    """The last verdict word in a refute cell (held | overturned | unverifiable), or "" if none.
    A cell keeps its history ("overturned 01.10 ... 2026-10-02: held"); only the latest verdict counts."""
    found = VERDICT_RE.findall(cell or "")
    return found[-1].lower() if found else ""


def check_absence(text: str, path: str, coverage: dict | None, lm: Landmine | None) -> tuple[list[Finding], dict]:
    """research-absence F2 (coverage row missing or empty) and F4 (refute cell empty) on ABSENT rows."""
    lid = lm.id if lm else ABSENCE_LANDMINE
    sev = lm.severities if lm else {}
    out: list[Finding] = []
    stats = {"rows": 0, "absent": 0, "overturned": 0, "f2_not_run": 0}
    for _, head, rows in _table_blocks(text):
        h = [x.strip().lower() for x in head]
        if "label" not in h or not any("claim" in x for x in h):
            continue
        li = h.index("label")
        rf = next((k for k, x in enumerate(h) if "refute" in x), None)
        for ln, cells in rows:
            stats["rows"] += 1
            refute = cells[rf] if rf is not None and rf < len(cells) else ""
            if refute_verdict(refute) == "overturned":
                stats["overturned"] += 1
            if li >= len(cells) or cells[li].strip().upper() != "ABSENT":
                continue
            stats["absent"] += 1
            claim = re.sub(r"\s+", " ", " | ".join(cells[:li]))[:120]
            ids = sorted(set(re.findall(r"\bCOV-\d+\b", " ".join(c for k, c in enumerate(cells) if k != rf))))
            if ids and coverage is None:
                stats["f2_not_run"] += 1
            elif ids:
                bad = [x for x in ids if x not in coverage or uncovered(coverage[x])]
                if bad:
                    out.append(Finding("landmines", sev.get("F2", "critical"), path, ln + 1,
                                       f"{claim} (names {', '.join(bad)}: missing or nothing searched)", f"{lid}/F2"))
            if not refute.strip():
                out.append(Finding("landmines", sev.get("F4", "major"), path, ln + 1,
                                   f"{claim} (refute cell empty)", f"{lid}/F4"))
    return out, stats


def claimed_rounds(quote: str) -> int | None:
    m = re.search(r"(?i)\b(\d+|" + "|".join(WORDNUM) + r") (?:review |panel )?rounds?\b", quote)
    if not m:
        return None
    w = m.group(1).lower()
    return int(w) if w.isdigit() else WORDNUM[w]


def process_record(findings: list[Finding], lm: Landmine | None, panel_count: int | None,
                   piece_sha: str | None, reviewed_sha: str | None) -> list[Finding]:
    """process-claims F3 and F4 after the cues: F4 when the hashes differ; F3 cleared when the claimed
    round count is at most the number of round-*.md reports."""
    lid = lm.id if lm else PROCESS_LANDMINE
    out: list[Finding] = []
    for f in findings:
        if f.rule != f"{lid}/F3":
            out.append(f)
            continue
        if reviewed_sha and piece_sha and piece_sha.lower() != reviewed_sha.lower():
            out.append(Finding(f.check, (lm.severities.get("F4") if lm else None) or "critical", f.file, f.line,
                               f"{f.quote} (piece sha256 {piece_sha[:12]}, reviewed {reviewed_sha[:12]})",
                               f"{lid}/F4"))
        n = claimed_rounds(f.quote)
        if panel_count is not None and n is not None:
            if n <= panel_count:
                continue
            f.quote = f"{f.quote} ({n} rounds claimed, {panel_count} round-*.md reports)"
        out.append(f)
    return out


def load_killed(text: str) -> tuple[list[tuple[str, re.Pattern, str]], list[str]]:
    """Returns ([(id, regex, reversed-by cell)], errors)."""
    out, errors = [], []
    for _, head, rows in _table_blocks(text):
        h = [x.strip().lower() for x in head]
        pc = next((k for k, x in enumerate(h) if "pattern" in x), None)
        if pc is None:
            continue
        rc = next((k for k, x in enumerate(h) if "reversed" in x), None)
        for _, cells in rows:
            if pc >= len(cells):
                continue
            kid = cells[0].strip()
            pat = cells[pc].strip().strip("`").replace(r"\|", "|")
            rx = compile_rx(pat, f"killed/{kid}", errors)
            if rx:
                out.append((kid, rx, cells[rc].strip() if rc is not None and rc < len(cells) else ""))
    return out, errors


def check_killed(doc: Doc, killed: list[tuple[str, re.Pattern, str]]) -> list[Finding]:
    out: list[Finding] = []
    for kid, rx, reversed_by in killed:
        if re.search(r"\bD-\d+\b", reversed_by):
            continue
        seen = set()
        for m in rx.finditer(doc.text):
            ln = doc.line_of(m.start())
            if ln in seen:
                continue
            seen.add(ln)
            out.append(Finding("killed-lines", "major", doc.path, ln,
                               f"{m.group(0)!r} in: {doc.sentence(m.start(), m.end())}", f"killed/{kid}"))
    return out


def check_claims(rows: list[dict], path: str) -> list[Finding]:
    out: list[Finding] = []
    vocab = {"SOURCED", "PROPOSAL", "TO-CONFIRM", "UNMARKED"}
    for r in rows:
        st = norm_status(_col(r, "status"))
        claim = _col(r, "claim", "text", "quote", "sentence")[:120] or "(no claim text)"
        ln = r["_line"]
        if st in ("", "UNMARKED"):
            out.append(Finding("claims", "major", path, ln, claim, "claims/UNMARKED"))
        elif st not in vocab:
            out.append(Finding("claims", "major", path, ln, f"status {st!r}: {claim}", "claims/unknown-status"))
        elif st == "TO-CONFIRM":
            owner = _col(r, "owner")
            if not owner:
                out.append(Finding("claims", "major", path, ln, claim, "claims/TO-CONFIRM-no-owner"))
            elif owner.lower().startswith("proposed"):
                out.append(Finding("claims", "minor", path, ln, f"owner {owner!r}, not accepted: {claim}",
                                   "claims/TO-CONFIRM-owner-proposed"))
            if not _col(r, "date", "due"):
                out.append(Finding("claims", "minor", path, ln, claim, "claims/TO-CONFIRM-no-date"))
    return out


def is_merge_field(content: str) -> bool:
    """[First name], [date], [IMO name], [Save My Seat]: three words or fewer."""
    return len(re.findall(r"[\w'$-]+", content.strip().strip('"“”*'))) <= 3


def check_marks(doc: Doc, limit: int = MAX_MARKS) -> list[Finding]:
    out: list[Finding] = []
    bounds = [o for o, _ in doc.heads] + [len(doc.text)]
    for a, b in zip(bounds, bounds[1:]):
        if doc.kind == "html":
            marks = [(s, e) for s, e in doc.dotted if a <= s < b]
        else:
            marks = [(s, e) for s, e in doc.marked if a <= s < b and not is_merge_field(doc.text[s + 1:e - 1])]
        if len(marks) > limit:
            s, e = marks[limit]
            snippet = re.sub(r"\s+", " ", doc.text[s:e])[:100]
            out.append(Finding("mark-budget", "minor", doc.path, doc.line_of(s),
                               f"{len(marks)} TO-CONFIRM marks in this section (limit {limit}); "
                               f"mark {limit + 1}: {snippet}", "marks/over-limit"))
    return out

# ---- plain: rules/landmines/plain-language.md (F1-F7) ------------------------------------------------

PLAIN_PIECES = ("email", "social", "webinar", "imo-note")
PLAIN_MAX_WORDS = 20            # F1: words in one sentence
PLAIN_MAX_SENTENCES = 3         # F2: sentences in one list item, after its bold label
PLAIN_SHORT = 30                # F2: more sentences are fine while the item is this many words or fewer
PLAIN_NGRAM, PLAIN_TIMES = 3, 3  # F3: a phrase of 3 words, 3 times in one item or paragraph
PLAIN_PREPS = {"on", "from", "in", "at", "to", "into", "onto", "with", "for", "of", "by"}  # F3: "on/from the case" is one phrase
GRADE_MAX = {"email": 9.0, "imo-note": 9.0, "how-made": 11.0}   # F6
PLAIN_SEV = {"F1": "major", "F2": "major", "F3": "minor", "F4": "minor", "F5": "major", "F6": "major",
             "F7": "major"}

SIDE_HEAD = re.compile(r"^\*\*Side notes?\b[^*]*\*\*:?\s*$", re.I)
HEADER_FIELD = re.compile(r"^\*\*(From|To|Subject|Preview):\*\*\s*(.*)$", re.I)
GREETING = re.compile(r"^(?:Hi|Hello|Dear)\b[^.!?]*,\s*$")
LIST_ITEM = re.compile(r"^(?:[-*+]|\d+[.)])\s+(.*)$")
LEAD_LABEL = re.compile(r"^(?:\([^)]*\)\s*)?\*\*(.+?)\*\*\s*(.*)$")
BOLD_ONLY = re.compile(r"^\*\*([^*]+)\*\*\s*$")
TABLE_RULE = re.compile(r"\|?[\s:|-]+\|?")
PWORD = re.compile(r"[A-Za-z0-9$]+(?:['’&+.,:-][A-Za-z0-9]+)*\+?")
JARGON_SHAPE = re.compile(r"(?<![\w$#/.-])(?:[A-Z][A-Za-z]*[A-Z][A-Za-z0-9]*|[A-Za-z]+\d[A-Za-z0-9]*"
                          r"|\d+[A-Za-z][A-Za-z0-9]*)(?![\w-])")


@dataclass
class Term:
    term: str
    rx: re.Pattern
    gloss: re.Pattern | None          # None: a name, needs no plain words


@dataclass
class PlainRules:
    lm: Landmine
    terms: list[Term]
    plain_ok: set[str]
    jargon: list[re.Pattern]
    errors: list[str]

    def cues(self, rid: str) -> list[Cue]:
        return [c for c in self.lm.cues if c.rule == f"{self.lm.id}/{rid}"]

    def sev(self, rid: str) -> str:
        return self.lm.severities.get(rid, PLAIN_SEV.get(rid, "major"))


@dataclass
class PUnit:
    off: int                          # offset of the line in doc.text
    kind: str                         # para | item | row | heading | header | greeting
    piece: str | None
    sec: int                          # offset of the section heading
    label: str                        # bold label at the start, cleaned
    body: str                         # the rest, cleaned
    group: int                        # paragraph group (F3)
    side: bool = False                # inside a side-notes block
    hook: bool = False                # the email's first paragraph after the greeting
    graded: bool = False              # counted for the F6 grade
    field: str = ""                   # header field: from | to | subject | preview


def load_terms(path: Path) -> tuple[list[Term], list[str]]:
    """AG's own terms: the fenced ```terms``` block of rules/voice.md, `term | count | plain words regex or -`."""
    if not path.is_file():
        return [], [f"voice file not found: {path}"]
    errors: list[str] = []
    out: list[Term] = []
    for line in (x for b in fenced(path.read_text(encoding="utf-8"), "terms") for x in block_lines(b)):
        parts = [p.strip() for p in line.split("|", 2)]
        if len(parts) != 3:
            errors.append(f"voice/terms: want 'term | count | plain words', got {line!r}")
            continue
        rx = compile_rx(_phrase_rx(parts[0]), f"voice/terms/{parts[0]}", errors, 0)
        gloss = None if parts[2] in ("", "-") else compile_rx(parts[2], f"voice/terms/{parts[0]}", errors, re.I)
        if rx:
            out.append(Term(parts[0], rx, gloss))
    if not out:
        errors.append(f"{path}: no ```terms``` block (AG's own terms)")
    return out, errors


def plain_rules(lm: Landmine, voice_path: Path) -> PlainRules:
    text = Path(lm.path).read_text(encoding="utf-8")
    errors = list(lm.errors)
    terms, terr = load_terms(voice_path)
    errors += terr
    ok = {w for b in fenced(text, "plain-ok") for ln in block_lines(b) for w in ln.split()}
    jargon = []
    for ln in (x for b in fenced(text, "jargon") for x in block_lines(b)):
        rx = compile_rx(ln, f"{lm.id}/jargon", errors, re.I | re.M)
        if rx:
            jargon.append(rx)
    for rid in ("F2", "F5", "F7"):
        if not [c for c in lm.cues if c.rule == f"{lm.id}/{rid}"]:
            errors.append(f"{lm.id}/{rid}: no cue")
    return PlainRules(lm, terms, ok, jargon, errors)


def plain_clean(s: str) -> str:
    """Prose only: link text kept unless it is a file name; URLs, code, tags and hashtags dropped;
    quoted speech and quoted names read as one word ("x"); markdown emphasis dropped."""
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", lambda m: m.group(1) if " " in m.group(1) else " ", s)
    s = re.sub(r"https?://\S+|`[^`\n]*`|<[^>\n]+>|(?<![\w&])#\w+", " ", s)
    s = re.sub("\"[^\"\n]*\"|“[^”\n]*”", " x ", s)
    s = re.sub(r"\*\*|__|(?<![\w*])\*(?=\S)|(?<=\S)\*(?![\w*])", "", s)
    return re.sub(r"\s+", " ", s).strip()


def plain_sentences(s: str) -> list[str]:
    out, start = [], 0
    for m in re.finditer("[.!?]+[\"'\u201d\\])]*(?=\\s)", s):
        if _abbrev(s, m.start()):
            continue
        part = s[start:m.end()].strip()
        if part:
            out.append(part)
        start = m.end()
    if s[start:].strip():
        out.append(s[start:].strip())
    return [x for x in out if PWORD.search(x)]


def plain_words(s: str) -> list[str]:
    return PWORD.findall(s)


def syllables(word: str) -> int:
    """Vowel groups, a silent final e dropped; at least one per hyphen part; apostrophes dropped."""
    n = 0
    for part in re.sub("['’]", "", word.lower()).split("-"):
        w = re.sub(r"[^a-z]", "", part)
        if not w:
            continue
        if len(w) > 3:
            w = re.sub(r"(?:[^laeiouy]es|[^laeiouy]ed|[^laeiouy]e)$", lambda m: m.group(0)[0], w)
        w = re.sub(r"^y", "", w)
        n += max(1, len(re.findall(r"[aeiouy]+", w)))
    return max(1, n)


def fk_grade(sentences: list[str]) -> tuple[float, int, int]:
    """Flesch-Kincaid grade: 0.39 words/sentence + 11.8 syllables/word - 15.59. A word has a letter."""
    words = [w for s in sentences for w in plain_words(s) if re.search(r"[A-Za-z]", w)]
    sents = [s for s in sentences if any(re.search(r"[A-Za-z]", w) for w in plain_words(s))]
    if not words or not sents:
        return 0.0, 0, 0
    syl = sum(syllables(w) for w in words)
    return 0.39 * len(words) / len(sents) + 11.8 * syl / len(words) - 15.59, len(words), len(sents)


def unit_sentences(u: PUnit) -> list[str]:
    if u.label and re.search(r"[.!?]$", u.label):
        return [u.label] + plain_sentences(u.body)
    return plain_sentences((u.label + " " + u.body).strip())


def plain_units(doc: Doc) -> list[PUnit]:
    """Lines of the piece as units: paragraph lines, list items, table rows, bold-only headings,
    header fields, greetings. A ## heading starts a section; '---' ends a side-notes block."""
    units: list[PUnit] = []
    lines = doc.text.split("\n")
    offs, o = [], 0
    for ln in lines:
        offs.append(o)
        o += len(ln) + 1
    group, sec, st, blank = 0, None, {}, True
    for i, raw in enumerate(lines):
        off = offs[i]
        s = raw.strip()
        if doc.section_start(off) != sec:
            sec = doc.section_start(off)
            st = {"side": False, "header": False, "greet": False, "hook": False}
        piece = doc.piece_at(off)
        if s.startswith(">"):
            s = s[1:].strip()
        if re.match(r"^#{1,2}(?!#)", s):
            blank = True
            continue
        if not s or s == "---" or (s.startswith("|") and TABLE_RULE.fullmatch(s)):
            if s == "---":
                st["side"] = False
            blank = True
            continue
        if piece is None:
            blank = False
            continue
        if SIDE_HEAD.match(s):
            st["side"], blank = True, True
            continue
        kind, field, label, body = "para", "", "", s
        m = HEADER_FIELD.match(s)
        if re.match(r"^#{3,}\s", s):
            kind, body = "heading", s.lstrip("#").strip()
        elif m:
            kind, field, body = "header", m.group(1).lower(), m.group(2)
            st["header"] = True
        elif GREETING.match(s):
            kind = "greeting"
            st["greet"] = True
        elif s.startswith("|"):
            nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if TABLE_RULE.fullmatch(nxt) and "-" in nxt:
                blank = True
                continue
            kind = "row"
            body = " ".join(c for c in _split_row(s) if c and not re.fullmatch(r"[\d:.\s]+", c))
        elif LIST_ITEM.match(s):
            kind, body = "item", LIST_ITEM.match(s).group(1)
        elif BOLD_ONLY.match(s):
            kind, body = "heading", BOLD_ONLY.match(s).group(1)
        if kind in ("item", "para"):
            lead = LEAD_LABEL.match(body)
            if lead:
                label, body = plain_clean(lead.group(1)), lead.group(2)
        if kind != "para" or blank:
            group += 1
        blank = kind != "para"
        u = PUnit(off, kind, piece, sec, label, plain_clean(body), group, side=st["side"], field=field)
        if piece == "email" and kind == "para" and not u.side and not st["hook"] and (st["greet"] or st["header"]):
            u.hook = st["hook"] = True
        if piece in ("email", "imo-note"):
            u.graded = bool(st["greet"] or st["header"]) and not u.side and not u.hook \
                and kind not in ("header", "greeting")
        elif piece == "how-made":
            u.graded = kind == "item"
        elif piece in PLAIN_PIECES:
            u.graded = not u.side and kind not in ("header", "greeting")
        units.append(u)
    return units


def _explained(tok: str, sent: str) -> bool:
    """The term sits inside parentheses next to its plain words, or is followed by (, :, ", a/the", is, means."""
    t = re.escape(tok)
    return bool(re.search(r"\([^()]*(?<![\w-])" + t + r"(?![\w-])[^()]*\)", sent) or
                re.search(r"(?<![\w-])" + t + r"(?:'s)?\s*(?:\(|:|,\s+(?:a|an|the)\b|\s+(?:is|are|means|stands for)\b)",
                          sent))


def unexplained_terms(sents: list[str], rules: PlainRules) -> list[tuple[str, str]]:
    """F4: (term, sentence) for each abbreviation-shaped word or `jargon` word with no plain words
    in its sentence or the one before. AG's own terms and `plain-ok` words pass."""
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for k, snt in enumerate(sents):
        spans = [(m.start(), m.end()) for t in rules.terms for m in t.rx.finditer(snt)]
        cands = [(m.start(), m.group(0)) for m in JARGON_SHAPE.finditer(snt)]
        cands += [(m.start(), m.group(0)) for rx in rules.jargon for m in rx.finditer(snt)]
        for pos, tok in cands:
            base = re.sub("['’]s$", "", tok)
            if base in rules.plain_ok or base in seen or any(a <= pos < b for a, b in spans) \
                    or re.fullmatch(r"\d+(?:st|nd|rd|th|s)", base, re.I):
                continue
            if _explained(base, snt) or (k and _explained(base, sents[k - 1])):
                continue
            seen.add(base)
            out.append((base, snt))
    return out


class _Titles(HTMLParser):
    """(title, line) of every element whose class holds the dotted class."""

    def __init__(self, dotted: str):
        super().__init__(convert_charrefs=True)
        self.dotted = dotted
        self.found: list[tuple[str, int]] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.dotted in (a.get("class") or "").split() and (a.get("title") or "").strip():
            self.found.append((a["title"].strip(), self.getpos()[0]))

    handle_startendtag = handle_starttag


def dotted_titles(html_text: str, dotted: str = "tbc") -> list[tuple[str, int]]:
    p = _Titles(dotted)
    p.feed(html_text)
    p.close()
    return p.found


def check_plain_titles(html_text: str, path: str, rules: PlainRules,
                       dotted: str = "tbc") -> tuple[list[Finding], int]:
    """F4 and F5 of plain-language on the tooltip (title attribute) of each dotted span of the page.
    Returns (findings at the span's line, number of titles read)."""
    lid = rules.lm.id
    out: list[Finding] = []
    titles = dotted_titles(html_text, dotted)
    for title, line in titles:
        for base, _ in unexplained_terms(plain_sentences(plain_clean(title)), rules):
            out.append(Finding("plain", rules.sev("F4"), path, line,
                               f"tooltip '{title}': '{base}' not explained"[:220], f"{lid}/F4"))
        why = [c.source for c in rules.cues("F5") if c.rx.search(title)]
        if why:
            out.append(Finding("plain", rules.sev("F5"), path, line,
                               f"tooltip '{title}' matches {' / '.join(why)}"[:220], f"{lid}/F5"))
    return out, len(titles)


def check_plain(doc: Doc, rules: PlainRules) -> tuple[list[Finding], dict]:
    """F1-F7 of plain-language. Returns (findings, {"shapes": {F1: n, ...}, "grades": [(piece, grade, max, line)]})."""
    lid = rules.lm.id
    out: list[Finding] = []
    shapes = {f"F{k}": 0 for k in range(1, 8)}

    def hit(rid: str, off: int, quote: str):
        shapes[rid] += 1
        out.append(Finding("plain", rules.sev(rid), doc.path, doc.line_of(off), quote[:220], f"{lid}/{rid}"))

    units = plain_units(doc)
    semi = [c for c in rules.cues("F2") if c.rx.search(";")]
    dash = [c for c in rules.cues("F2") if not c.rx.search(";")]
    copy = [u for u in units if u.piece in PLAIN_PIECES and not u.hook and u.kind != "greeting"
            and u.field not in ("from", "to")]
    for u in copy:
        sents = unit_sentences(u)
        text = (u.label + " " + u.body).strip()
        for snt in sents:                                          # F1 long sentence
            n = len(plain_words(snt))
            if n > PLAIN_MAX_WORDS:
                hit("F1", u.off, f"{n} words: {snt}")
        if u.kind in ("item", "row"):                              # F2 overloaded item (agenda rows too)
            body = plain_sentences(u.body)
            why = []
            if any(c.rx.search(text) for c in semi):
                why.append("semicolon")
            asides = sum((len([m for c in dash for m in c.rx.finditer(x)]) + 1) // 2 for x in body)
            if asides > 1:
                why.append(f"{asides} dash asides")
            if len(body) > PLAIN_MAX_SENTENCES and len(plain_words(u.body)) > PLAIN_SHORT:
                why.append(f"{len(body)} sentences after the label")
            if why:
                hit("F2", u.off, f"{', '.join(why)}: {text}")
        if u.side and u.label:                                     # F5 side-note title
            why = [c.source for c in rules.cues("F5") if c.rx.search(u.label)]
            if why:
                hit("F5", u.off, f"title '{u.label}' matches {' / '.join(why)}")
        if not u.side:                                             # F7 feature with history or reason
            for snt in sents:
                m = next((m for c in rules.cues("F7") for m in [c.rx.search(snt)] if m), None)
                if m:
                    hit("F7", u.off, f"'{m.group(0).strip(', ')}' in: {snt}")
        if u.kind == "heading" or u.field == "subject":            # F4 heading with an AG term
            for t in rules.terms:
                if t.gloss and t.rx.search(text) and not t.gloss.search(t.rx.sub(" ", text)):
                    hit("F4", u.off, f"heading uses {t.term} with no plain words: {text}")
        for base, snt in unexplained_terms(sents, rules):          # F4 term not explained
            hit("F4", u.off, f"'{base}' not explained: {snt}")
    groups: dict[int, list[PUnit]] = {}                            # F3 repeated phrase
    for u in copy:
        groups.setdefault(u.group, []).append(u)
    for g in groups.values():
        toks = [w.lower() for u in g for w in re.findall("[A-Za-z][A-Za-z'’]*", u.label + " " + u.body)]
        toks = ["(prep)" if w in PLAIN_PREPS else w for w in toks]
        grams: dict[tuple[str, ...], int] = {}
        for j in range(len(toks) - PLAIN_NGRAM + 1):
            key = tuple(toks[j:j + PLAIN_NGRAM])
            grams[key] = grams.get(key, 0) + 1
        top = [k for k, v in grams.items() if v >= PLAIN_TIMES]
        if top:
            hit("F3", g[0].off, f"'{' '.join(top[0])}' {grams[top[0]]} times in: "
                                f"{' '.join((u.label + ' ' + u.body).strip() for u in g)}")
    grades = []                                                    # F6 grade per ## section
    secs: dict[int, list[PUnit]] = {}
    for u in units:
        if u.graded:
            secs.setdefault(u.sec, []).append(u)
    for sec, us in secs.items():
        g, nw, ns = fk_grade([x for u in us for x in unit_sentences(u)])
        if not nw:
            continue
        piece = us[0].piece
        lim = GRADE_MAX.get(piece or "")
        grades.append((piece, round(g, 1), lim, doc.line_of(sec)))
        if lim is not None and g > lim:
            hit("F6", sec, f"{piece} grade {g:.1f} (max {lim:g}): {nw} words, {ns} sentences")
    return out, {"shapes": shapes, "grades": grades}


def plain_note(stats: dict) -> str:
    shapes = ", ".join(f"{k} {v}" for k, v in stats["shapes"].items() if v) or "no shape fired"
    grades = ", ".join(f"{p} {g:g}" + (f" (max {m:g})" if m is not None else "") for p, g, m, _ in stats["grades"])
    return f"{shapes}; grade {grades or 'none'}"


def write_stamps(path: Path, lms: list[Landmine], findings: list[Finding], res: dict[str, CheckResult],
                 piece_sha: str) -> int:
    today = datetime.date.today().isoformat()
    n = 0
    with path.open("a", encoding="utf-8") as fh:
        for lm in lms:
            group = res["time-promises" if lm.id == TIME_LANDMINE else "plain" if lm.id == PLAIN_LANDMINE
                        else "landmines"]
            hits = sum(1 for f in findings if f.rule.startswith(lm.id + "/"))
            result = "uncertain" if lm.errors else "not_run" if not lm.cues else \
                "fail" if hits else "not_run" if group.incomplete or group.result == "not_run" else "pass"
            fh.write(json.dumps({"landmine": lm.id, "version": lm.version, "date": today, "result": result,
                                 "hits": hits, "by": "tools/check.py stage 1", "piece_sha256": piece_sha},
                                ensure_ascii=False) + "\n")
            n += 1
    return n


def run(args) -> tuple[list[Finding], dict[str, CheckResult], int]:
    res = {c: CheckResult() for c in CHECKS}
    findings: list[Finding] = []
    piece_path = Path(args.piece)
    if not piece_path.is_file():
        for c in res.values():
            c.note = f"piece not found: {args.piece}"
        return findings, res, 3
    piece = load_doc(piece_path, args.dotted_class, args.piece_type, brackets=True)
    plain = load_doc(piece_path, args.dotted_class, args.piece_type) if piece.kind == "html" else piece
    piece_sha = hashlib.sha256(piece_path.read_bytes()).hexdigest()

    def done(name: str, fs: list[Finding], note: str = "", uncertain: bool = False):
        findings.extend(fs)
        r = res[name]
        r.findings = len(fs)
        r.result = "uncertain" if uncertain else ("fail" if fs else "pass")
        r.note = note

    page = page_cues = None
    if args.html:
        hp = Path(args.html)
        if hp.is_file():
            page = load_doc(hp, args.dotted_class)
            page_cues = load_doc(hp, args.dotted_class, brackets=True)
        else:
            res["parity"].note = f"--html not found: {args.html}"
    else:
        res["parity"].required = False
        res["parity"].note = "not requested (--html not given)"

    numbers = None
    np_ = Path(args.numbers)
    if np_.is_file():
        try:
            numbers = load_numbers(np_)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            res["numbers"].result = "uncertain"
            res["numbers"].note = f"numbers file unreadable: {e}"
    else:
        res["numbers"].note = f"numbers file not found: {np_}"

    claims_rows = None
    if args.claims:
        cp = Path(args.claims)
        if cp.is_file():
            claims_rows = read_claims(cp.read_text(encoding="utf-8"))
        else:
            res["claims"].note = f"--claims not found: {args.claims}"
    else:
        res["claims"].required = False
        res["claims"].note = "not requested (--claims not given)"

    facts = facts_text = None
    fp = Path(args.facts)
    if fp.is_file():
        facts_text = fp.read_text(encoding="utf-8")
        facts = facts_doc(facts_text, str(fp))
    cov = None
    cvp = Path(args.coverage)
    if cvp.is_file():
        cov = coverage_rows(cvp.read_text(encoding="utf-8"))
    panel_count = None
    if args.panel:
        pd = Path(args.panel)
        panel_count = len(list(pd.glob("round-*.md"))) if pd.is_dir() else None

    lms = load_landmines(Path(args.landmines))
    num_lm = next((lm for lm in lms if lm.id == NUMBERS_LANDMINE), None)

    def run_cues(name: str, group: list[Landmine]):
        fs: list[Finding] = []
        notes: list[str] = []
        notes_info: list[str] = []
        for doc in (piece, page_cues):
            if doc:
                f, n = check_cues(doc, group, name, numbers, "copy")
                fs += f
                notes += n
        needs_facts = [c.rule for lm in group for c in lm.cues if c.target == "facts"]
        incomplete = []
        if needs_facts:
            if facts:
                f, n = check_cues(facts, group, name, numbers, "facts")
                fs += f
                notes += n
            else:
                incomplete.append(f"facts table not found ({fp}): {', '.join(sorted(set(needs_facts)))} not run")
        abs_lm = next((lm for lm in group if lm.id == ABSENCE_LANDMINE), None)
        if abs_lm and facts_text is not None:
            f, st = check_absence(facts_text, str(fp), cov, abs_lm)
            fs += f
            stats = f"facts: {st['rows']} rows, {st['absent']} ABSENT, {st['overturned']} overturned"
            notes_info.append(stats)
            if st["f2_not_run"]:
                incomplete.append(f"coverage not found ({cvp}): research-absence/F2 not run")
        proc_lm = next((lm for lm in group if lm.id == PROCESS_LANDMINE), None)
        if proc_lm:
            fs = process_record(fs, proc_lm, panel_count, piece_sha, args.reviewed_sha256)
            if args.panel and panel_count is None:
                incomplete.append(f"--panel not a folder: {args.panel}")
        no_cues = [lm.id for lm in group if not lm.cues]
        if no_cues:
            incomplete.append(f"no cues: {', '.join(no_cues)}")
        errs = [e for lm in group for e in lm.errors]
        note = f"{len(group)} landmine(s), {sum(len(lm.cues) for lm in group)} cues"
        for part in notes_info + incomplete + notes:
            note += "; " + part
        if errs:
            note += "; rule errors: " + "; ".join(errs)[:400]
        done(name, fs, note, uncertain=bool(errs))
        if incomplete or notes:
            res[name].incomplete = True
            if not fs and not errs:
                res[name].result = "not_run"

    if not lms:
        res["landmines"].note = f"no landmine files in {args.landmines}"
        res["time-promises"].note = res["landmines"].note
    else:
        run_cues("landmines", [lm for lm in lms if lm.id not in (TIME_LANDMINE, PLAIN_LANDMINE)])
        tl = [lm for lm in lms if lm.id == TIME_LANDMINE]
        if tl:
            run_cues("time-promises", tl)
        else:
            res["time-promises"].note = f"{TIME_LANDMINE}.md missing"

    pl = next((lm for lm in lms if lm.id == PLAIN_LANDMINE), None)
    if pl:
        prules = plain_rules(pl, Path(args.voice))
        fs, pst = check_plain(piece, prules)
        tnote = ""
        if page:
            tfs, nt = check_plain_titles(Path(args.html).read_text(encoding="utf-8"), args.html, prules,
                                         args.dotted_class)
            fs += tfs
            tnote = f"; {nt} page tooltips read (F4, F5)"
        done("plain", fs, plain_note(pst) + tnote + ("; rule errors: " + "; ".join(prules.errors)[:300]
                                             if prules.errors else ""), uncertain=bool(prules.errors))
    elif lms:
        res["plain"].note = f"{PLAIN_LANDMINE}.md missing"
    else:
        res["plain"].note = f"no landmine files in {args.landmines}"

    vp = Path(args.voice)
    voice = None
    if vp.is_file():
        voice = load_voice(vp)
        if not voice.banned:
            res["voice"].note = f"{vp} has no machine-readable banned cues"
        else:
            done("voice", check_voice(piece, voice),
                 f"{len(voice.banned)} banned cues, {len(voice.allowed)} exceptions", uncertain=bool(voice.errors))
            if voice.errors:
                res["voice"].note += "; rule errors: " + "; ".join(voice.errors)[:300]
    else:
        res["voice"].note = f"voice file not found: {vp}"

    if numbers is not None:
        done("numbers", check_numbers(piece, numbers, num_lm), f"{len(numbers.records)} records")

    if page:
        done("parity", check_parity(plain, page))

    labels = list(DEFAULT_LABELS)
    for extra in [lm.labels for lm in lms] + ([voice.labels] if voice else []):
        labels += [x for x in extra if x not in labels]
    fs = check_stray(plain, labels) + (
        check_stray(page, labels, plain if plain.kind == 'md' else None) if page else [])
    done("stray-labels", fs, f"{len(labels)} labels" +
         ("" if page or piece.kind == "html" else "; label search needs the rendered page (--html)"))

    done("repeats", check_repeats(piece))
    if claims_rows is not None:
        done("claims", check_claims(claims_rows, str(args.claims)), f"{len(claims_rows)} rows")
    marks = check_marks(piece, args.max_marks) + (check_marks(page, args.max_marks) if page else [])
    done("mark-budget", marks, "page: dotted spans; markdown: brackets of 4+ words" if page else
         "markdown: brackets of 4+ words (dotted spans are counted with --html)")

    dp = Path(args.decisions)
    if dp.is_file():
        killed, kerr = load_killed(dp.read_text(encoding="utf-8"))
        if killed:
            done("killed-lines", check_killed(plain, killed) + (check_killed(page, killed) if page else []),
                 f"{len(killed)} killed lines", uncertain=bool(kerr))
        else:
            res["killed-lines"].note = f"no killed-lines table in {dp}"
        if kerr:
            res["killed-lines"].note += "; rule errors: " + "; ".join(kerr)[:300]
    else:
        res["killed-lines"].note = f"decisions file not found: {dp}"

    if args.reviewed_sha256:
        same = piece_sha.lower() == args.reviewed_sha256.strip().lower()
        done("release-hash", [] if same else
             [Finding("release-hash", "critical", str(piece_path), 1,
                      f"piece sha256 {piece_sha} differs from reviewed {args.reviewed_sha256.strip()}",
                      "release/hash-mismatch")], f"piece sha256 {piece_sha}")
    else:
        res["release-hash"].required = False
        res["release-hash"].note = f"not requested; piece sha256 {piece_sha}"

    if args.stamp:
        sp = Path(str(piece_path) + ".stamps.jsonl")
        n = write_stamps(sp, lms, findings, res, piece_sha)
        res["landmines"].note += f"; {n} stamps appended to {sp.name}"

    code = 0
    for r in res.values():
        if (r.result in ("not_run", "uncertain") or r.incomplete) and (r.required or args.require_all):
            code = 3
    if code != 3 and findings:
        code = 1
    return findings, res, code


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Stage-1 checks for AG copy (see tools/README.md).")
    p.add_argument("piece")
    p.add_argument("--html")
    p.add_argument("--numbers", default=str(ROOT / "templates" / "numbers.json"))
    p.add_argument("--claims")
    p.add_argument("--facts", default=str(ROOT / "templates" / "facts.md"))
    p.add_argument("--coverage", default=str(ROOT / "templates" / "coverage.md"))
    p.add_argument("--decisions", default=str(ROOT / "templates" / "decisions.md"))
    p.add_argument("--panel", help="folder of round-*.md review reports (process-claims F3)")
    p.add_argument("--reviewed-sha256", help="sha256 of the last reviewed version (release-hash, process-claims F4)")
    p.add_argument("--stamp", action="store_true", help="append stage-1 stamps to <piece>.stamps.jsonl")
    p.add_argument("--landmines", default=str(ROOT / "rules" / "landmines"))
    p.add_argument("--voice", default=str(ROOT / "rules" / "voice.md"))
    p.add_argument("--json", action="store_true")
    p.add_argument("--require-all", action="store_true",
                   help="a check not requested (no --html, no --claims) also makes the exit 3")
    p.add_argument("--max-marks", type=int, default=MAX_MARKS)
    p.add_argument("--dotted-class", default="tbc", help="HTML class of a dotted (TO-CONFIRM) span")
    p.add_argument("--piece-type", choices=PIECES, help="tag for a file that holds one piece")
    return p


def main(argv: list[str] | None = None) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    findings, res, code = run(args)
    if args.json:
        print(json.dumps({"piece": args.piece, "exit": code, "checks": {k: asdict(v) for k, v in res.items()},
                          "findings": [asdict(f) for f in findings]}, ensure_ascii=False, indent=1))
        return code
    for f in findings:
        print(f.row())
    print()
    print(f"{'check':<14} {'result':<10} {'findings':>8}  note")
    for k, v in res.items():
        print(f"{k:<14} {v.result:<10} {v.findings:>8}  {v.note}")
    print(f"exit {code}")
    return code


if __name__ == "__main__":
    sys.exit(main())
