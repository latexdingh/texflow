"""Full-text search across LaTeX project files."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class SearchMatch:
    file: Path
    line_number: int
    line: str
    column: int = 0

    def __str__(self) -> str:
        return f"{self.file}:{self.line_number}:{self.column}: {self.line.strip()}"


@dataclass
class SearchResult:
    query: str
    matches: List[SearchMatch] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.matches) > 0

    def summary(self) -> str:
        if not self.matches:
            return f"No matches for '{self.query}'."
        return f"{len(self.matches)} match(es) for '{self.query}'."


def search_files(
    paths: List[Path],
    query: str,
    *,
    case_sensitive: bool = False,
    regex: bool = False,
) -> SearchResult:
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        pattern = re.compile(query if regex else re.escape(query), flags)
    except re.error as exc:
        raise ValueError(f"Invalid regex: {exc}") from exc

    result = SearchResult(query=query)
    for path in paths:
        if not path.is_file():
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for lineno, line in enumerate(lines, 1):
            m = pattern.search(line)
            if m:
                result.matches.append(
                    SearchMatch(file=path, line_number=lineno, line=line, column=m.start())
                )
    return result
