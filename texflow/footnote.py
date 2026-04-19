"""Footnote analysis for LaTeX documents."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class FootnoteItem:
    line: int
    text: str

    def __str__(self) -> str:
        preview = self.text[:60] + "..." if len(self.text) > 60 else self.text
        return f"  line {self.line}: {preview}"


@dataclass
class FootnoteResult:
    items: List[FootnoteItem] = field(default_factory=list)
    error: str = ""

    def ok(self) -> bool:
        return not self.error

    def summary(self) -> str:
        if self.error:
            return f"error: {self.error}"
        n = len(self.items)
        if n == 0:
            return "No footnotes found."
        return f"{n} footnote{'s' if n != 1 else ''} found."

    def long_footnotes(self, threshold: int = 200) -> List[FootnoteItem]:
        return [f for f in self.items if len(f.text) > threshold]


_FOOTNOTE_RE = re.compile(r"\\footnote\{")


def _extract_footnote_text(line: str, start: int) -> str:
    """Extract balanced-brace content starting after the opening brace."""
    depth = 1
    buf: list[str] = []
    for ch in line[start:]:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
        buf.append(ch)
    return "".join(buf)


def extract_footnotes(path: Path) -> FootnoteResult:
    if not path.exists():
        return FootnoteResult(error=f"File not found: {path}")
    items: List[FootnoteItem] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return FootnoteResult(error=str(exc))
    for lineno, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("%"):
            continue
        for m in _FOOTNOTE_RE.finditer(line):
            text = _extract_footnote_text(line, m.end())
            items.append(FootnoteItem(line=lineno, text=text.strip()))
    return FootnoteResult(items=items)
