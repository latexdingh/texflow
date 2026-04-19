"""Bibliography analysis: extract and validate bibliography entries."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class BibEntry:
    """A single bibliography entry parsed from a .bib file."""

    key: str
    entry_type: str  # article, book, inproceedings, etc.
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[str] = None
    fields: dict = field(default_factory=dict)

    def __str__(self) -> str:
        parts = [f"@{self.entry_type}{{{self.key}"]
        if self.author:
            parts.append(f"  author = {self.author}")
        if self.title:
            parts.append(f"  title  = {self.title}")
        if self.year:
            parts.append(f"  year   = {self.year}")
        return "\n".join(parts) + "\n}"


@dataclass
class BibResult:
    """Result of parsing a .bib file."""

    entries: List[BibEntry] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    source: str = ""

    def ok(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        n = len(self.entries)
        if not self.entries:
            return "No bibliography entries found."
        types: dict[str, int] = {}
        for e in self.entries:
            types[e.entry_type] = types.get(e.entry_type, 0) + 1
        breakdown = ", ".join(f"{v} {k}" for k, v in sorted(types.items()))
        return f"{n} entr{'y' if n == 1 else 'ies'} ({breakdown})"

    def get(self, key: str) -> Optional[BibEntry]:
        for entry in self.entries:
            if entry.key == key:
                return entry
        return None


def _strip_braces(value: str) -> str:
    """Remove surrounding braces or quotes from a field value."""
    value = value.strip().rstrip(",").strip()
    if (value.startswith("{") and value.endswith("}")) or (
        value.startswith('"') and value.endswith('"')
    ):
        return value[1:-1].strip()
    return value


def parse_bib(path: Path) -> BibResult:
    """Parse a .bib file and return all entries found."""
    if not path.exists():
        return BibResult(errors=[f"File not found: {path}"], source=str(path))

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return BibResult(errors=[str(exc)], source=str(path))

    entries: List[BibEntry] = []
    errors: List[str] = []

    # Match @type{key, ... } blocks (simplified, handles common cases)
    block_re = re.compile(
        r"@(\w+)\s*\{\s*([^,]+),([^@]*?)\}",
        re.DOTALL | re.IGNORECASE,
    )
    field_re = re.compile(r"(\w+)\s*=\s*([^=]+?)(?=,\s*\w+\s*=|\s*$)", re.DOTALL)

    for match in block_re.finditer(text):
        entry_type = match.group(1).lower()
        key = match.group(2).strip()
        body = match.group(3)

        if entry_type == "comment" or entry_type == "preamble":
            continue

        parsed_fields: dict[str, str] = {}
        for fm in field_re.finditer(body):
            fname = fm.group(1).lower()
            fval = _strip_braces(fm.group(2))
            parsed_fields[fname] = fval

        entry = BibEntry(
            key=key,
            entry_type=entry_type,
            title=parsed_fields.get("title"),
            author=parsed_fields.get("author"),
            year=parsed_fields.get("year"),
            fields=parsed_fields,
        )
        entries.append(entry)

    return BibResult(entries=entries, errors=errors, source=str(path))
