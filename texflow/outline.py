"""Extract section outline from a LaTeX source file."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

SECTION_CMDS = [
    "part", "chapter", "section", "subsection", "subsubsection", "paragraph"
]

_PATTERN = re.compile(
    r"\\(" + "|".join(SECTION_CMDS) + r")\*?\{([^}]+)\}"
)


@dataclass
class OutlineEntry:
    level: str
    title: str
    line: int

    def depth(self) -> int:
        return SECTION_CMDS.index(self.level)

    def __str__(self) -> str:
        indent = "  " * self.depth()
        return f"{indent}{self.title}  [{self.level}, line {self.line}]"


@dataclass
class Outline:
    entries: List[OutlineEntry] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def summary(self) -> str:
        if self.is_empty():
            return "(no sections found)"
        return "\n".join(str(e) for e in self.entries)

    def filter_level(self, level: str) -> "Outline":
        return Outline([e for e in self.entries if e.level == level])


def extract_outline(path: Path) -> Outline:
    """Parse a .tex file and return its section outline."""
    if not path.exists():
        return Outline()
    entries: List[OutlineEntry] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith("%"):
            continue
        for m in _PATTERN.finditer(line):
            entries.append(OutlineEntry(level=m.group(1), title=m.group(2).strip(), line=lineno))
    return Outline(entries)
