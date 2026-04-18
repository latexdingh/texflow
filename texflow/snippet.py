"""Named snippet extraction from LaTeX source files."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Snippet:
    label: str
    content: str
    source_file: str
    start_line: int

    def __str__(self) -> str:
        return f"[{self.label}] ({self.source_file}:{self.start_line})\n{self.content.strip()}"


@dataclass
class SnippetResult:
    snippets: list[Snippet] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def get(self, label: str) -> Optional[Snippet]:
        for s in self.snippets:
            if s.label == label:
                return s
        return None


_BEGIN = re.compile(r"%\s*snippet:\s*(\S+)")
_END = re.compile(r"%\s*end-snippet")


def extract_snippets(path: Path) -> SnippetResult:
    result = SnippetResult()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        result.errors.append(str(e))
        return result

    i = 0
    while i < len(lines):
        m = _BEGIN.search(lines[i])
        if m:
            label = m.group(1)
            start = i + 1
            body_lines = []
            i += 1
            while i < len(lines) and not _END.search(lines[i]):
                body_lines.append(lines[i])
                i += 1
            if i >= len(lines):
                result.errors.append(f"Unclosed snippet '{label}' starting at line {start}")
            else:
                result.snippets.append(Snippet(
                    label=label,
                    content="\n".join(body_lines),
                    source_file=str(path),
                    start_line=start,
                ))
        i += 1
    return result
