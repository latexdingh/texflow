"""Check for mismatched \\begin{} / \\end{} environment pairs in LaTeX files."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class EnvIssue:
    kind: str  # 'unmatched_begin' | 'unmatched_end' | 'mismatch'
    env_name: str
    line: int
    detail: str = ""

    def __str__(self) -> str:
        return f"Line {self.line}: [{self.kind}] \\{{}}{self.env_name}{{}} — {self.detail}"


@dataclass
class EnvCheckResult:
    issues: List[EnvIssue] = field(default_factory=list)
    missing: bool = False

    def ok(self) -> bool:
        return not self.missing and len(self.issues) == 0

    def summary(self) -> str:
        if self.missing:
            return "File not found."
        if self.ok():
            return "All environments matched."
        return f"{len(self.issues)} environment issue(s) found."

    def __str__(self) -> str:
        if self.ok():
            return self.summary()
        return "\n".join([self.summary()] + [str(i) for i in self.issues])


_ENV_RE = re.compile(r"\\(begin|end)\{([^}]+)\}")


def check_environments(path: Path) -> EnvCheckResult:
    if not path.exists():
        return EnvCheckResult(missing=True)

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    stack: list[tuple[str, int]] = []  # (env_name, line_number)
    issues: list[EnvIssue] = []

    for lineno, line in enumerate(lines, start=1):
        # Strip comments
        stripped = re.sub(r"(?<!\\)%.*", "", line)
        for match in _ENV_RE.finditer(stripped):
            cmd, env = match.group(1), match.group(2)
            if cmd == "begin":
                stack.append((env, lineno))
            else:  # end
                if not stack:
                    issues.append(EnvIssue(
                        kind="unmatched_end",
                        env_name=env,
                        line=lineno,
                        detail=f"\\end{{{env}}} has no matching \\begin",
                    ))
                elif stack[-1][0] != env:
                    open_env, open_line = stack[-1]
                    issues.append(EnvIssue(
                        kind="mismatch",
                        env_name=env,
                        line=lineno,
                        detail=(
                            f"\\end{{{env}}} closes \\begin{{{open_env}}} "
                            f"opened at line {open_line}"
                        ),
                    ))
                    stack.pop()
                else:
                    stack.pop()

    for env_name, open_line in stack:
        issues.append(EnvIssue(
            kind="unmatched_begin",
            env_name=env_name,
            line=open_line,
            detail=f"\\begin{{{env_name}}} was never closed",
        ))

    return EnvCheckResult(issues=issues)
