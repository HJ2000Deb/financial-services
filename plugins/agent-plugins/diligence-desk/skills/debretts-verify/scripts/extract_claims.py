#!/usr/bin/env python3
"""Extract verifiable claims from a draft so they can be sourced one by one.

Pulls every currency amount, percentage, multiple, basis-point figure, date and bare
number out of a document, with its location, and writes a verification checklist.
For workbooks it also lists hardcoded numeric cells — constants with no formula behind
them, which is where model errors hide.

Supports .md, .txt, .docx, .pptx, .xlsx. Standard library only.

Usage:
    python3 extract_claims.py DRAFT [--csv OUT.csv] [--kinds currency,multiple]
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

# --- claim patterns --------------------------------------------------------
# Ordered: the first pattern to match a span wins, so currency beats bare number.
PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("currency", re.compile(r"(?:[£$€]|US\$|GBP|EUR|USD)\s?\d[\d,]*(?:\.\d+)?\s?(?:bn|billion|m|million|k|000s)?\b", re.I)),
    ("multiple", re.compile(r"\b\d+(?:\.\d+)?\s?x\b", re.I)),
    ("basis_points", re.compile(r"\b\d+(?:\.\d+)?\s?bps?\b", re.I)),
    ("percentage", re.compile(r"\b\d+(?:\.\d+)?\s?%")),
    ("date", re.compile(
        r"\b(?:\d{1,2}\s+)?(?:January|February|March|April|May|June|July|August|September|"
        r"October|November|December)\s+\d{4}\b|\b(?:FY|H[12]|Q[1-4]|LTM)\s?\d{2,4}\b|"
        r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b", re.I)),
    ("number", re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?(?:bn|billion|m|million|k)?(?![\w%.])", re.I)),
]

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
}


def _xml_text(zf: zipfile.ZipFile, member: str, tag: str) -> list[str]:
    """Concatenated text of every `tag` element in an OOXML part."""
    try:
        root = ET.fromstring(zf.read(member))
    except (KeyError, ET.ParseError):
        return []
    return ["".join(n.itertext()) for n in root.iter(tag)]


def read_units(path: Path) -> list[tuple[str, str]]:
    """Return [(location, text)] for the document, one entry per logical unit."""
    ext = path.suffix.lower()
    if ext in (".md", ".txt", ".markdown"):
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return [(f"line {i}", ln) for i, ln in enumerate(lines, 1) if ln.strip()]

    if ext == ".docx":
        with zipfile.ZipFile(path) as zf:
            paras = _xml_text(zf, "word/document.xml", f"{{{NS['w']}}}p")
        return [(f"para {i}", t) for i, t in enumerate(paras, 1) if t.strip()]

    if ext == ".pptx":
        out: list[tuple[str, str]] = []
        with zipfile.ZipFile(path) as zf:
            slides = sorted(
                (n for n in zf.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                key=lambda n: int(re.findall(r"\d+", n)[-1]),
            )
            for n in slides:
                idx = int(re.findall(r"\d+", n)[-1])
                for t in _xml_text(zf, n, f"{{{NS['a']}}}p"):
                    if t.strip():
                        out.append((f"slide {idx}", t))
        return out

    if ext in (".xlsx", ".xlsm"):
        return read_workbook(path)

    raise SystemExit(f"unsupported file type: {ext}")


def read_workbook(path: Path) -> list[tuple[str, str]]:
    """Sheet text plus a hardcode audit: constant cells with no formula behind them."""
    out: list[tuple[str, str]] = []
    with zipfile.ZipFile(path) as zf:
        shared: list[str] = []
        try:
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            shared = ["".join(si.itertext()) for si in root.iter(f"{{{NS['s']}}}si")]
        except (KeyError, ET.ParseError):
            pass

        names: dict[str, str] = {}
        try:
            wb = ET.fromstring(zf.read("xl/workbook.xml"))
            for i, sh in enumerate(wb.iter(f"{{{NS['s']}}}sheet"), 1):
                names[f"sheet{i}"] = sh.get("name", f"sheet{i}")
        except (KeyError, ET.ParseError):
            pass

        sheets = sorted(
            (n for n in zf.namelist() if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n)),
            key=lambda n: int(re.findall(r"\d+", n)[-1]),
        )
        for member in sheets:
            key = f"sheet{int(re.findall(r'[0-9]+', member)[-1])}"
            sheet = names.get(key, key)
            try:
                root = ET.fromstring(zf.read(member))
            except ET.ParseError:
                continue
            for c in root.iter(f"{{{NS['s']}}}c"):
                ref = c.get("r", "?")
                has_formula = c.find(f"{{{NS['s']}}}f") is not None
                v = c.find(f"{{{NS['s']}}}v")
                if v is None or v.text is None:
                    continue
                if c.get("t") == "s":  # shared string index
                    try:
                        text = shared[int(v.text)]
                    except (ValueError, IndexError):
                        continue
                    out.append((f"{sheet}!{ref}", text))
                elif not has_formula:
                    out.append((f"{sheet}!{ref} [hardcode]", v.text))
    return out


def find_claims(units: list[tuple[str, str]], kinds: set[str] | None) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for loc, text in units:
        taken: list[tuple[int, int]] = []
        for kind, pat in PATTERNS:
            if kinds and kind not in kinds:
                continue
            for m in pat.finditer(text):
                if any(m.start() < e and s < m.end() for s, e in taken):
                    continue  # already claimed by a higher-priority pattern
                taken.append((m.start(), m.end()))
                snippet = text[max(0, m.start() - 60): m.end() + 60].strip()
                rows.append({
                    "location": loc,
                    "kind": kind,
                    "claim": m.group(0).strip(),
                    "context": re.sub(r"\s+", " ", snippet),
                    "class": "",          # Given / Sourced / Derived / Unverified
                    "source": "",         # document + page, or system + field + date
                })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("draft", type=Path)
    ap.add_argument("--csv", type=Path, help="write the verification log here")
    ap.add_argument("--kinds", help="comma-separated subset: "
                                    + ",".join(k for k, _ in PATTERNS))
    args = ap.parse_args()

    if not args.draft.is_file():
        raise SystemExit(f"not found: {args.draft}")

    kinds = {k.strip() for k in args.kinds.split(",")} if args.kinds else None
    rows = find_claims(read_units(args.draft), kinds)

    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["location", "kind", "claim", "context",
                                              "class", "source"])
            w.writeheader()
            w.writerows(rows)
        print(f"{len(rows)} claim(s) -> {args.csv}")
    else:
        for r in rows:
            print(f"{r['location']:<28} {r['kind']:<12} {r['claim']}")
        print(f"\n{len(rows)} claim(s) to verify", file=sys.stderr)

    by_kind: dict[str, int] = {}
    for r in rows:
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1
    if by_kind:
        print("  " + "  ".join(f"{k}={v}" for k, v in sorted(by_kind.items())),
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
