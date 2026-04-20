"""Word-wrap checker for LaTeX source files."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class WrapIssue:
    line: int
    text: str
    suggestion: str

    def __str__(self) -> str:
        return f"Line {self.line}: {self.suggestion!r} → {self.text!r}"


@dataclass
class WrapResult:
    issues: List[WrapIssue] = field(default_factory=list)
    error: str = ""

    def ok(self) -> bool:
        return not self.issues and not self.error

    def summary(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        if not self.issues:
            return "No wrap issues found."
        return f"{len(self.issues)} wrap issue(s) found."


def _should_wrap(line: str, max_len: int) -> bool:
    stripped = line.rstrip("\n")
    if stripped.lstrip().startswith("%"):
        return False
    return len(stripped) > max_len


def _suggest_break(text: str, max_len: int) -> str:
    """Return the text up to the last space before max_len."""
    candidate = text[:max_len]
    idx = candidate.rfind(" ")
    if idx == -1:
        return candidate
    return candidate[:idx] + " %"


def check_word_wrap(path: Path, max_len: int = 100) -> WrapResult:
    if not path.exists():
        return WrapResult(error=f"File not found: {path}")
    issues: List[WrapIssue] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if _should_wrap(raw, max_len):
            suggestion = _suggest_break(raw, max_len)
            issues.append(WrapIssue(line=lineno, text=raw, suggestion=suggestion))
    return WrapResult(issues=issues)
