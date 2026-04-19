"""Macro/command definition checker for LaTeX files."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

_DEF_PATTERN = re.compile(
    r"\\(?:newcommand|renewcommand|providecommand)\*?\{\\(\w+)\}"
)
_USE_PATTERN = re.compile(r"\\(\w+)")
_SKIP = {"begin", "end", "usepackage", "documentclass", "newcommand",
         "renewcommand", "providecommand", "item", "label", "ref",
         "cite", "text", "textbf", "textit", "emph"}


@dataclass
class MacroIssue:
    name: str
    kind: str  # 'unused' | 'duplicate'
    line: Optional[int] = None

    def __str__(self) -> str:
        loc = f" (line {self.line})" if self.line else ""
        return f"{self.kind.upper()}: \\{self.name}{loc}"


@dataclass
class MacroResult:
    defined: List[str] = field(default_factory=list)
    issues: List[MacroIssue] = field(default_factory=list)

    def ok(self) -> bool:
        return len(self.issues) == 0

    def summary(self) -> str:
        if self.ok():
            return f"{len(self.defined)} macro(s) defined, no issues."
        return f"{len(self.defined)} macro(s) defined, {len(self.issues)} issue(s)."


def check_macros(path: Path) -> MacroResult:
    if not path.exists():
        return MacroResult()

    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    defined: dict[str, int] = {}
    duplicates: list[MacroIssue] = []
    used: set[str] = set()

    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("%"):
            continue
        for m in _DEF_PATTERN.finditer(line):
            name = m.group(1)
            if name in defined:
                duplicates.append(MacroIssue(name=name, kind="duplicate", line=lineno))
            else:
                defined[name] = lineno
        for m in _USE_PATTERN.finditer(line):
            name = m.group(1)
            if name not in _SKIP:
                used.add(name)

    issues = list(duplicates)
    for name in defined:
        if name not in used:
            issues.append(MacroIssue(name=name, kind="unused", line=defined[name]))

    return MacroResult(defined=list(defined.keys()), issues=issues)
