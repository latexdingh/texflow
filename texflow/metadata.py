"""Extract and display LaTeX document metadata (title, author, date)."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class DocumentMetadata:
    title: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    document_class: Optional[str] = None
    packages: list[str] = field(default_factory=list)

    def ok(self) -> bool:
        return any([self.title, self.author, self.date])

    def summary(self) -> str:
        parts = []
        if self.title:
            parts.append(f"Title : {self.title}")
        if self.author:
            parts.append(f"Author: {self.author}")
        if self.date:
            parts.append(f"Date  : {self.date}")
        if self.document_class:
            parts.append(f"Class : {self.document_class}")
        if self.packages:
            parts.append(f"Packages ({len(self.packages)}): {', '.join(self.packages[:5])}")
        return "\n".join(parts) if parts else "No metadata found."


def _strip_braces(val: str) -> str:
    return val.strip().strip("{}")


def extract_metadata(path: Path) -> DocumentMetadata:
    if not path.exists():
        return DocumentMetadata()

    text = path.read_text(encoding="utf-8", errors="ignore")
    meta = DocumentMetadata()

    for key, attr in (("title", "title"), ("author", "author"), ("date", "date")):
        m = re.search(rf"\\{key}\{{([^}}]*)\}}", text)
        if m:
            setattr(meta, attr, _strip_braces(m.group(1)))

    m = re.search(r"\\documentclass(?:\[.*?\])?\{([^}]+)\}", text)
    if m:
        meta.document_class = m.group(1).strip()

    meta.packages = re.findall(r"\\usepackage(?:\[.*?\])?\{([^}]+)\}", text)

    return meta
