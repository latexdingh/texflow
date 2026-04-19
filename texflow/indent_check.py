"""Check for inconsistent indentation in LaTeX environments."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List
import re


@dataclass
class IndentIssue:
    line: int
    message: str
    text: str

    def __str__(self) -> str:
        return f"Line {self.line}: {self.message} — {self.text!r}"


@dataclass
class IndentCheckResult:
    issues: List[IndentIssue] = field(default_factory=list)
    error: str = ""

    def ok(self) -> bool:
        return not self.issues and not self.error

    def summary(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        if not self.issues:
            return "No indentation issues found."
        return f"{len(self.issues)} indentation issue(s) found."


_BEGIN = re.compile(r"^(\s*)\\begin\{(\w+)\}")
_END = re.compile(r"^(\s*)\\end\{(\w+)\}")


def check_indent(path: Path) -> IndentCheckResult:
    if not path.exists():
        return IndentCheckResult(error=f"File not found: {path}")

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    issues: List[IndentIssue] = []
    stack: list[tuple[str, str, int]] = []  # (env, indent, line_no)

    for lineno, raw in enumerate(lines, 1):
        bm = _BEGIN.match(raw)
        if bm:
            stack.append((bm.group(2), bm.group(1), lineno))
            continue

        em = _END.match(raw)
        if em:
            env_name = em.group(2)
            end_indent = em.group(1)
            if stack and stack[-1][0] == env_name:
                _, begin_indent, _ = stack.pop()
                if begin_indent != end_indent:
                    issues.append(IndentIssue(
                        line=lineno,
                        message=f"Mismatched indent for \\end{{{env_name}}}",
                        text=raw.strip(),
                    ))
            # unmatched \end is handled by ref_check; skip here

    return IndentCheckResult(issues=issues)
