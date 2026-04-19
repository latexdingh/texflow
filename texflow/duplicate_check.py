"""Detect duplicate words and repeated phrases in LaTeX source files."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import re


@dataclass
class DuplicateIssue:
    line: int
    word: str
    context: str

    def __str__(self) -> str:
        return f"Line {self.line}: repeated word '{self.word}' — {self.context.strip()}"


@dataclass
class DuplicateCheckResult:
    issues: list[DuplicateIssue] = field(default_factory=list)
    error: str = ""

    def ok(self) -> bool:
        return not self.issues and not self.error

    def summary(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        if not self.issues:
            return "No duplicate words found."
        return f"{len(self.issues)} duplicate word(s) detected."


_STRIP_CMD = re.compile(r"\\[a-zA-Z]+\*?\{[^}]*\}|\\[a-zA-Z]+\*?|%.*")
_WORD_RE = re.compile(r"\b([a-zA-Z]{2,})\b")


def _clean_line(line: str) -> str:
    return _STRIP_CMD.sub(" ", line)


def check_duplicates(path: Path) -> DuplicateCheckResult:
    if not path.exists():
        return DuplicateCheckResult(error=f"File not found: {path}")

    issues: list[DuplicateIssue] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return DuplicateCheckResult(error=str(exc))

    for lineno, raw in enumerate(lines, start=1):
        cleaned = _clean_line(raw)
        words = _WORD_RE.findall(cleaned.lower())
        seen: set[str] = set()
        for i in range(len(words) - 1):
            if words[i] == words[i + 1] and words[i] not in seen:
                seen.add(words[i])
                issues.append(DuplicateIssue(line=lineno, word=words[i], context=raw))

    return DuplicateCheckResult(issues=issues)
