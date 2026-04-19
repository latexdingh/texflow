"""Acronym checker: finds defined and used acronyms in LaTeX source."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict


@dataclass
class AcronymIssue:
    kind: str  # 'undefined' | 'unused'
    acronym: str
    line: int

    def __str__(self) -> str:
        return f"[{self.kind}] acronym '{self.acronym}' at line {self.line}"


@dataclass
class AcronymResult:
    issues: List[AcronymIssue] = field(default_factory=list)
    defined: Dict[str, int] = field(default_factory=dict)
    used: Dict[str, int] = field(default_factory=dict)

    def ok(self) -> bool:
        return len(self.issues) == 0

    def summary(self) -> str:
        if self.ok():
            return f"Acronyms OK ({len(self.defined)} defined, {len(self.used)} used)"
        undefined = sum(1 for i in self.issues if i.kind == "undefined")
        unused = sum(1 for i in self.issues if i.kind == "unused")
        parts = []
        if undefined:
            parts.append(f"{undefined} undefined")
        if unused:
            parts.append(f"{unused} unused")
        return "Acronym issues: " + ", ".join(parts)


_DEF_RE = re.compile(r"\\(?:newacronym|DeclareAcronym)\{([^}]+)\}")
_USE_RE = re.compile(r"\\(?:ac|acp|acl|acf|Ac|Acp|Acl|Acf)\{([^}]+)\}")


def check_acronyms(path: Path) -> AcronymResult:
    if not path.exists():
        return AcronymResult()

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    defined: Dict[str, int] = {}
    used: Dict[str, int] = {}

    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("%"):
            continue
        for m in _DEF_RE.finditer(line):
            key = m.group(1)
            if key not in defined:
                defined[key] = lineno
        for m in _USE_RE.finditer(line):
            key = m.group(1)
            if key not in used:
                used[key] = lineno

    issues: List[AcronymIssue] = []
    for key, lineno in used.items():
        if key not in defined:
            issues.append(AcronymIssue("undefined", key, lineno))
    for key, lineno in defined.items():
        if key not in used:
            issues.append(AcronymIssue("unused", key, lineno))

    return AcronymResult(issues=issues, defined=defined, used=used)
