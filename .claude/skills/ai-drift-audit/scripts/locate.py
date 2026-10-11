#!/usr/bin/env python3
"""Where does a term live in this repository, now and in its whole git history?

For each term, reports matches in the committed HEAD split into categories (code, tests, docs,
llm-log, other), and walks every commit on every branch to answer "was this ever in code?".
When a term is only in the history of a log or doc (e.g. an LLM output that was later overwritten),
the old text is printed so the original source can be quoted. External documents (reports and PDFs
that are not in the repo) can be searched too.

Usage (from the repository root):
    python .claude/skills/ai-drift-audit/scripts/locate.py ALLOW_LEGACY protocol_version
    python .claude/skills/ai-drift-audit/scripts/locate.py --external ~/Downloads/report.pdf ALLOW_LEGACY
    python .claude/skills/ai-drift-audit/scripts/locate.py --exact "handshakes_total"

Matching is case-insensitive. By default "_", "-" and " " are interchangeable, so ALLOW_LEGACY
also matches allow-legacy and "allow legacy"; use --exact to switch that off.
Only the standard library is required; PDFs are read with pypdf if it is installed.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

LOG_DIR_NAMES = {"llm-log", "llm-logs", "ai-log", "ai-logs", "prompt-log", "prompts", "prompt-logs"}
CODE_SUFFIXES = {".py", ".js", ".ts", ".go", ".rs", ".java", ".c", ".h", ".sh", ".yml", ".yaml",
                 ".toml", ".ini", ".cfg"}
DOC_SUFFIXES = {".md", ".rst", ".txt", ".adoc"}
MAX_BYTES = 2_000_000


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def category(path: str) -> str:
    p = Path(path)
    parts = {part.lower() for part in p.parts[:-1]}
    name = p.name.lower()
    if parts & LOG_DIR_NAMES:
        return "llm-log"
    if "audits" in parts:
        return "audit"  # this skill's own reports; never evidence
    if parts & {"tests", "test"} or name.startswith("test_") or name.endswith("_test.py"):
        return "tests"
    if (p.suffix.lower() in CODE_SUFFIXES or name.startswith("dockerfile") or name.startswith("requirements")
            or "compose" in name):
        return "code"
    if p.suffix.lower() in DOC_SUFFIXES:
        return "docs"
    return "other"


def _escape(text: str) -> str:
    """Escape so the result means the same in Python `re` and POSIX ERE (`git grep -E`)."""
    out = []
    for ch in text:
        if ch.isalnum():
            out.append(ch)
        elif ch in "]\\^":
            out.append("\\" + ch)
        else:
            out.append(f"[{ch}]")
    return "".join(out)


def pattern(term: str, exact: bool) -> tuple[re.Pattern, str]:
    """One pattern string, valid both as a Python regex and as a POSIX ERE for `git grep -E`."""
    if exact:
        expr = _escape(term)
    else:
        expr = "[_ -]?".join(_escape(piece) for piece in re.split(r"[_\- ]+", term) if piece)
    return re.compile(expr, re.IGNORECASE), expr


def grep_rev(ere: str, rev: str) -> list[tuple[str, str, str]]:
    """(path, line_no, text) for every match in a committed revision (not the working tree)."""
    out = subprocess.run(["git", "grep", "-n", "-I", "-i", "-E", ere, rev], capture_output=True, text=True).stdout
    rows = []
    for line in out.splitlines():
        parts = line.split(":", 3)  # rev:path:line:text
        if len(parts) == 4:
            rows.append((parts[1], parts[2], parts[3]))
    return rows


def search_head(ere: str, term: str, exact: bool) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for path, n, text in grep_rev(ere, "HEAD"):
        loose = "" if exact or term.lower() in text.lower() else " (loose match)"
        hits.setdefault(category(path), []).append(f"{path}:{n}: {text.strip()[:110]}{loose}")
    return hits


def search_history(ere: str) -> tuple[dict[str, list[str]], dict[str, str]]:
    """For every commit on every branch, which categories contained the term.
    Also returns, per category, the oldest commit that contained it (for quoting old sources)."""
    seen: dict[str, list[str]] = {}
    oldest: dict[str, str] = {}
    for line in git("log", "--all", "--format=%h %ad", "--date=short").splitlines():
        sha, date = line.split(" ", 1)
        out = subprocess.run(["git", "grep", "-l", "-I", "-i", "-E", ere, sha], capture_output=True, text=True).stdout
        cats = {category(p.split(":", 1)[1]) for p in out.splitlines() if ":" in p}
        for c in cats:
            seen.setdefault(c, []).append(f"{sha} ({date})")
            oldest[c] = sha  # log is newest-first, so the last assignment is the oldest commit
    return seen, oldest


def normalise(text: str) -> str:
    """Undo PDF line wrapping: join hyphenated breaks, collapse whitespace."""
    return re.sub(r"\s+", " ", re.sub(r"-\n", "", text))


def found_in(rx: re.Pattern, text: str) -> bool:
    """Match in normalised text, or with all whitespace removed (identifiers split across lines)."""
    return bool(rx.search(normalise(text)) or rx.search(re.sub(r"\s+", "", text)))


def read_external(path: Path) -> list[tuple[str, str]]:
    """Return (location, text) chunks: one per page for PDFs, one per line otherwise."""
    if path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader  # optional dependency
        except ImportError:
            return [("", f"[pypdf not installed: read {path.name} manually]")]
        return [(f"p.{i}", page.extract_text() or "") for i, page in enumerate(PdfReader(str(path)).pages, 1)]
    return [(f"line {i}", t) for i, t in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("terms", nargs="+")
    ap.add_argument("--exact", action="store_true", help="do not treat _ - and space as equivalent")
    ap.add_argument("--external", nargs="*", default=[], type=Path, help="reports/PDFs outside the repo")
    ap.add_argument("--max", type=int, default=6, help="locations shown per category")
    ap.add_argument("--no-history", action="store_true", help="skip the (slower) all-commits walk")
    args = ap.parse_args()

    head = git("rev-parse", "--short", "HEAD").strip()
    print(f"Repository HEAD: {head} ({git('branch', '--show-current').strip() or 'detached'})")
    dirty = git("status", "--porcelain").strip()
    if dirty:
        print(f"WARNING: working tree has {len(dirty.splitlines())} uncommitted change(s); "
              "results below are for the committed HEAD only. Record this in the report.")
    print()
    external = {p: read_external(p.expanduser()) for p in args.external}

    for term in args.terms:
        rx, ere = pattern(term, args.exact)
        hits = search_head(ere, term, args.exact)
        history, oldest = ({}, {}) if args.no_history else search_history(ere)
        print(f"## {term}\n")
        print("| Category | Matches at HEAD | Commits where present (any branch) | First seen |")
        print("|---|---|---|---|")
        for cat in ("code", "tests", "docs", "llm-log", "other"):
            h = history.get(cat, [])
            first = h[-1] if h else "-"
            print(f"| {cat} | {len(hits.get(cat, []))} | {len(h) if not args.no_history else 'n/a'} | {first} |")
        for p, chunks in external.items():
            n = [loc for loc, text in chunks if found_in(rx, text)]
            print(f"| external: {p.name} | {len(n)} | n/a | {', '.join(n[:8]) or '-'} |")
        print()
        for cat in ("code", "tests", "docs", "llm-log", "other"):
            for loc in hits.get(cat, [])[: args.max]:
                print(f"- [{cat}] {loc}")
        for cat in ("llm-log", "docs"):
            if cat in oldest and not hits.get(cat):
                print(f"- [{cat}, history only] not at HEAD; oldest version containing it ({oldest[cat]}):")
                for path, n, text in grep_rev(ere, oldest[cat])[: args.max]:
                    if category(path) == cat:
                        print(f"    `git show {oldest[cat]}:{path}` line {n}: {text.strip()[:110]}")
        in_code_now = bool(hits.get("code") or hits.get("tests"))
        in_code_ever = bool(history.get("code") or history.get("tests"))
        described = bool(hits.get("docs") or hits.get("llm-log") or history.get("llm-log") or any(
            found_in(rx, t) for c in external.values() for _, t in c))
        if described and not in_code_now and not args.no_history:
            hint = "described but NEVER in code in any commit" if not in_code_ever else "was in code earlier, removed"
            print(f"\n> Hint (mechanical, applies only if this term names a feature): {hint}. "
                  "Confirm by reading the code before reporting.")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
