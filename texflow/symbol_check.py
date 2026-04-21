"""Check for common LaTeX symbol usage issues and suggest alternatives."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

# (pattern, suggestion, description)
_SYMBOL_RULES: list[tuple[str, str, str]] = [
    (r"(?<!\\)--(?![-])", r"\\textendash{} or ---", "Use -- for en-dash or --- for em-dash"),
    (r"(?<!\\)---", r"\\textemdash{}", "Em-dash detected; ensure intentional"),
    (r"(?<!\\)\.\.\.", r"\\ldots{}", "Use \\ldots{} instead of three dots"),
    (r"(?<!\\)<\s*=", r"\\leq", "Use \\leq for less-than-or-equal in math"),
    (r"(?<!\\)>\s*=", r"\\geq", "Use \\geq for greater-than-or-equal in math"),
    (r"(?<!\\)!=\b", r"\\neq", "Use \\neq for not-equal in math"),
    (r"\\textbf\{([^}]{1,3})\}", None, "Very short bold text; possibly use \\emph{}"),
    (r"~{2,}", r"\\quad or \\qquad", "Multiple tildes; use \\quad for spacing"),
]


@dataclass
class SymbolIssue:
    file: str
    line: int
    text: str
    suggestion: Optional[str]
    description: str

    def __str__(self) -> str:
        sug = f" → {self.suggestion}" if self.suggestion else ""
        return f"{self.file}:{self.line}: {self.description}{sug} (found: {self.text!r})"


@dataclass
class SymbolCheckResult:
    issues: List[SymbolIssue] = field(default_factory=list)
    error: Optional[str] = None

    def ok(self) -> bool:
        return self.error is None and len(self.issues) == 0

    def summary(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        if not self.issues:
            return "No symbol issues found."
        return f"{len(self.issues)} symbol issue(s) found."


def check_symbols(path: Path) -> SymbolCheckResult:
    """Scan a .tex file for common symbol misuse patterns."""
    if not path.exists():
        return SymbolCheckResult(error=f"File not found: {path}")

    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return SymbolCheckResult(error=str(exc))

    issues: list[SymbolIssue] = []
    for lineno, raw in enumerate(lines, start=1):
        # Skip pure comment lines
        stripped = raw.lstrip()
        if stripped.startswith("%"):
            continue
        # Remove inline comments before checking
        code = re.sub(r"(?<!\\)%.*", "", raw)
        for pattern, suggestion, description in _SYMBOL_RULES:
            for m in re.finditer(pattern, code):
                issues.append(
                    SymbolIssue(
                        file=str(path),
                        line=lineno,
                        text=m.group(0),
                        suggestion=suggestion,
                        description=description,
                    )
                )

    return SymbolCheckResult(issues=issues)
