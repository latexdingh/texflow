"""Check for duplicate and unused \label{} definitions in LaTeX files."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class LabelIssue:
    kind: str  # 'duplicate' | 'unused'
    label: str
    file: str
    line: int

    def __str__(self) -> str:
        return f"[{self.kind}] \\label{{{self.label}}} at {self.file}:{self.line}"


@dataclass
class LabelCheckResult:
    issues: List[LabelIssue] = field(default_factory=list)

    def ok(self) -> bool:
        return len(self.issues) == 0

    def summary(self) -> str:
        if self.ok():
            return "No label issues found."
        dup = sum(1 for i in self.issues if i.kind == "duplicate")
        unused = sum(1 for i in self.issues if i.kind == "unused")
        parts = []
        if dup:
            parts.append(f"{dup} duplicate(s)")
        if unused:
            parts.append(f"{unused} unused")
        return "Label issues: " + ", ".join(parts) + "."


def _extract_labels(path: Path) -> list[tuple[str, int]]:
    labels = []
    try:
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip().startswith("%"):
                continue
            for m in re.finditer(r"\\label\{([^}]+)\}", line):
                labels.append((m.group(1), lineno))
    except OSError:
        pass
    return labels


def _extract_refs(path: Path) -> set[str]:
    refs: set[str] = set()
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("%"):
                continue
            for m in re.finditer(r"\\(?:ref|eqref|pageref|cref|Cref)\{([^}]+)\}", line):
                refs.add(m.group(1))
    except OSError:
        pass
    return refs


def check_labels(files: list[Path]) -> LabelCheckResult:
    all_labels: list[tuple[str, str, int]] = []  # (label, file, line)
    all_refs: set[str] = set()

    for f in files:
        for label, lineno in _extract_labels(f):
            all_labels.append((label, str(f), lineno))
        all_refs |= _extract_refs(f)

    issues: list[LabelIssue] = []
    seen: dict[str, tuple[str, int]] = {}
    for label, fname, lineno in all_labels:
        if label in seen:
            issues.append(LabelIssue("duplicate", label, fname, lineno))
        else:
            seen[label] = (fname, lineno)

    for label, (fname, lineno) in seen.items():
        if label not in all_refs:
            issues.append(LabelIssue("unused", label, fname, lineno))

    return LabelCheckResult(issues=issues)
