#!/usr/bin/env python3
"""Code-verified Zero-Leak check for Sfumato Track B (Blind Isomorphic Masking).

Scans a masked scenario for banned original-domain terms before it is handed to
a Blind solver. Pure Python stdlib, zero network calls, zero file writes.

Matching rules (case-insensitive):
  * Pure-ASCII terms (``app``, ``PR``, ``chat filter``) match on word
    boundaries, so ``app`` matches ``app`` / ``apps`` / ``app's`` but not
    ``approach`` or ``apple``. Whitespace inside a multi-word term matches any
    run of whitespace.
  * Terms containing non-ASCII characters (Korean, CJK, Cyrillic, ...) match as
    substrings, because agglutinative particles attach without spaces.

Exit codes: 0 = PASS (no leaks), 1 = FAIL (>=1 leaked term),
2 = invalid arguments / unreadable input.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Simple plural / possessive suffixes allowed after an ASCII term.
_ASCII_SUFFIX = r"(?:'s|’s|s|es)?"


def parse_terms(raw: str) -> list[str]:
    """Split comma- and newline-separated terms; drop blanks and duplicates."""
    out: list[str] = []
    seen: set[str] = set()
    for line in raw.splitlines():
        for part in line.split(","):
            term = " ".join(part.split())
            key = term.casefold()
            if term and key not in seen:
                seen.add(key)
                out.append(term)
    return out


def compile_term(term: str) -> tuple[str, "re.Pattern[str] | None"]:
    """Return ("word", regex) for ASCII terms or ("substring", None) otherwise."""
    if term.isascii():
        body = r"\s+".join(re.escape(w) for w in term.split())
        pattern = r"(?<![A-Za-z0-9_])" + body + _ASCII_SUFFIX + r"(?![A-Za-z0-9_])"
        return "word", re.compile(pattern, re.IGNORECASE)
    return "substring", None


def find_leaks(text: str, terms: list[str]) -> list[dict]:
    """Return one entry per leaked term: {"term", "mode", "count", "lines"}."""
    lines = text.splitlines() or [""]
    leaks = []
    for term in terms:
        mode, regex = compile_term(term)
        needle = term.casefold()
        hit_lines: list[int] = []
        count = 0
        for lineno, line in enumerate(lines, start=1):
            if regex is not None:
                n = len(regex.findall(line))
            else:
                n = line.casefold().count(needle)
            if n:
                count += n
                hit_lines.append(lineno)
        if count:
            leaks.append({"term": term, "mode": mode, "count": count, "lines": hit_lines})
    return leaks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail if a masked Track B scenario leaks banned original-domain terms."
    )
    parser.add_argument("--terms", default="", help="Comma-separated banned terms")
    parser.add_argument("--terms-file", help="File with banned terms (one per line or comma-separated)")
    src = parser.add_mutually_exclusive_group()
    src.add_argument("--text", help="Masked scenario text to check")
    src.add_argument("--file", help="File containing the masked scenario (default: stdin)")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args(argv)

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    raw_terms = args.terms
    if args.terms_file:
        try:
            raw_terms += "\n" + Path(args.terms_file).read_text(encoding="utf-8-sig")
        except OSError as exc:
            parser.error(f"cannot read --terms-file: {exc}")
    terms = parse_terms(raw_terms)
    if not terms:
        parser.error("at least one non-empty banned term is required (--terms / --terms-file)")

    if args.text is not None:
        text = args.text
    elif args.file:
        try:
            text = Path(args.file).read_text(encoding="utf-8-sig")
        except OSError as exc:
            parser.error(f"cannot read --file: {exc}")
    else:
        if hasattr(sys.stdin, "reconfigure"):
            sys.stdin.reconfigure(encoding="utf-8")
        text = sys.stdin.read()

    leaks = find_leaks(text, terms)
    if args.json:
        print(json.dumps({
            "status": "FAIL" if leaks else "PASS",
            "leaked_count": len(leaks),
            "terms_checked": len(terms),
            "leaks": leaks,
        }, ensure_ascii=False, indent=2))
    elif leaks:
        print(f"FAIL: {len(leaks)} leaked term(s)")
        for leak in leaks:
            line_list = ", ".join(str(n) for n in leak["lines"])
            print(f"  - {leak['term']!r} x{leak['count']} (line {line_list})")
    else:
        print("PASS: 0 leaked terms")
    return 1 if leaks else 0


if __name__ == "__main__":
    raise SystemExit(main())
