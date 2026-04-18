"""Basic LaTeX linting: detect common style and structure issues."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class LintIssue:
    line: int
    code: str
    message: str

    def __str__(self) -> str:
        return f"  L{self.line} [{self.code}] {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0

    def summary(self) -> str:
        if self.ok:
            return "No lint issues found."
        return f"{len(self.issues)} lint issue(s) found."


_CHECKS = [
    ("W001", re.compile(r"\\\\\s*$"), "Trailing double-backslash at end of line (use sparingly)"),
    ("W002", re.compile(r"  +"), "Multiple consecutive spaces (use LaTeX spacing commands)"),
    ("W003", re.compile(r"\$\$"), "Display math via $$ (prefer \\[ ... \\])"),
    ("W004", re.compile(r"(?<!\\)%.*TODO", re.IGNORECASE), "TODO comment left in source"),
    ("W005", re.compile(r"\\footnote\{[^}]{120,}\}"), "Very long footnote — consider trimming"),
    ("E001", re.compile(r"\\begin\{center\}\s*\\includegraphics"), "Use \\centering inside figure instead of center env"),
]


def lint_file(path: Path) -> LintResult:
    """Run all lint checks against a single .tex file."""
    if not path.exists():
        return LintResult(issues=[LintIssue(0, "E999", f"File not found: {path}")])

    issues: List[LintIssue] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    for lineno, line in enumerate(lines, start=1):
        # skip pure comment lines
        stripped = line.lstrip()
        if stripped.startswith("%"):
            continue
        for code, pattern, message in _CHECKS:
            if pattern.search(line):
                issues.append(LintIssue(lineno, code, message))

    return LintResult(issues=issues)
