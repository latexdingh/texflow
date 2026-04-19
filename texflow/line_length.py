"""Check for overly long lines in LaTeX source files."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

DEFAULT_MAX_LENGTH = 120


@dataclass
class LineLengthIssue:
    line_number: int
    length: int
    content: str
    max_allowed: int

    def __str__(self) -> str:
        preview = self.content[:60] + "..." if len(self.content) > 60 else self.content
        return f"Line {self.line_number}: {self.length} chars (max {self.max_allowed}): {preview}"


@dataclass
class LineLengthResult:
    issues: List[LineLengthIssue] = field(default_factory=list)
    error: str = ""

    def ok(self) -> bool:
        return not self.issues and not self.error

    def summary(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        if not self.issues:
            return "All lines within length limit."
        return f"{len(self.issues)} line(s) exceed the length limit."


def check_line_length(
    path: Path,
    max_length: int = DEFAULT_MAX_LENGTH,
    skip_comments: bool = True,
) -> LineLengthResult:
    if not path.exists():
        return LineLengthResult(error=f"File not found: {path}")

    issues: List[LineLengthIssue] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return LineLengthResult(error=str(exc))

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if skip_comments and stripped.startswith("%"):
            continue
        if len(line.rstrip("\n")) > max_length:
            issues.append(
                LineLengthIssue(
                    line_number=i,
                    length=len(line.rstrip("\n")),
                    content=line.rstrip("\n"),
                    max_allowed=max_length,
                )
            )
    return LineLengthResult(issues=issues)
