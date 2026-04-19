"""Check for common math environment issues in LaTeX files."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class MathIssue:
    line: int
    message: str
    context: str = ""

    def __str__(self) -> str:
        return f"Line {self.line}: {self.message}" + (f" — {self.context}" if self.context else "")


@dataclass
class MathCheckResult:
    issues: List[MathIssue] = field(default_factory=list)

    def ok(self) -> bool:
        return len(self.issues) == 0

    def summary(self) -> str:
        if self.ok():
            return "No math issues found."
        return f"{len(self.issues)} math issue(s) found."


_UNCLOSED_INLINE = re.compile(r'(?<!\\)\$[^$\n]+$')
_DOUBLE_DOLLAR = re.compile(r'(?<!\\)\$\$')
_EMPTY_ENV = re.compile(r'\\begin\{(equation|align|gather)\*?\}\s*\\end\{\1\*?\}')
_FRAC_NO_BRACES = re.compile(r'\\frac[^{]')


def check_math(path: Path) -> MathCheckResult:
    if not path.exists():
        return MathCheckResult()

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    issues: List[MathIssue] = []

    dollar_count = 0
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("%"):
            continue

        # Track unmatched inline $ (simple heuristic)
        inline_dollars = len(re.findall(r'(?<!\\)\$(?!\$)', line))
        dollar_count += inline_dollars

        if _FRAC_NO_BRACES.search(line):
            issues.append(MathIssue(i, r"\frac not followed by braces", stripped[:60]))

    if dollar_count % 2 != 0:
        issues.append(MathIssue(0, "Unmatched inline $ detected across file"))

    for m in _EMPTY_ENV.finditer(text):
        lineno = text[: m.start()].count("\n") + 1
        issues.append(MathIssue(lineno, f"Empty math environment: {m.group()[:40]}"))

    return MathCheckResult(issues=issues)
