"""Whitespace issue detection for LaTeX source files."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class WhitespaceIssue:
    line: int
    kind: str  # 'trailing', 'tab', 'multiple_blank', 'mixed_indent'
    text: str

    def __str__(self) -> str:
        return f"Line {self.line}: [{self.kind}] {self.text!r}"


@dataclass
class WhitespaceResult:
    issues: List[WhitespaceIssue] = field(default_factory=list)
    missing: bool = False

    def ok(self) -> bool:
        return not self.missing and len(self.issues) == 0

    def summary(self) -> str:
        if self.missing:
            return "File not found."
        if self.ok():
            return "No whitespace issues found."
        kinds = {i.kind for i in self.issues}
        return f"{len(self.issues)} issue(s) found: {', '.join(sorted(kinds))}."


def check_whitespace(
    path: Path,
    *,
    check_trailing: bool = True,
    check_tabs: bool = True,
    check_multiple_blank: bool = True,
) -> WhitespaceResult:
    if not path.exists():
        return WhitespaceResult(missing=True)

    issues: List[WhitespaceIssue] = []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

    blank_run = 0
    for lineno, raw in enumerate(lines, start=1):
        if check_trailing and raw != raw.rstrip():
            issues.append(WhitespaceIssue(lineno, "trailing", raw))

        if check_tabs and "\t" in raw:
            issues.append(WhitespaceIssue(lineno, "tab", raw))

        if check_multiple_blank:
            stripped = raw.strip()
            if stripped == "":
                blank_run += 1
                if blank_run > 1:
                    issues.append(WhitespaceIssue(lineno, "multiple_blank", raw))
            else:
                blank_run = 0

    return WhitespaceResult(issues=issues)
