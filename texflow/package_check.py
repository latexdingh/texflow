"""Check for undeclared or unused \usepackage{} entries in a LaTeX file."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class PackageIssue:
    kind: str  # 'unused' | 'duplicate'
    package: str
    line: int

    def __str__(self) -> str:
        return f"[{self.kind}] \\usepackage{{{self.package}}} (line {self.line})"


@dataclass
class PackageCheckResult:
    issues: List[PackageIssue] = field(default_factory=list)
    packages: List[str] = field(default_factory=list)
    error: str = ""

    def ok(self) -> bool:
        return not self.issues and not self.error

    def summary(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        if not self.issues:
            return f"{len(self.packages)} package(s) declared, no issues found."
        return f"{len(self.issues)} issue(s): " + "; ".join(str(i) for i in self.issues)


_PKG_RE = re.compile(r"^\s*\\usepackage(?:\[.*?\])?\{([^}]+)\}", re.MULTILINE)
_CMD_RE = re.compile(r"\\([a-zA-Z]+)")

# Map packages to commands they provide (subset for heuristic checking)
_PACKAGE_COMMANDS: dict[str, list[str]] = {
    "amsmath": ["align", "equation", "gather", "dfrac", "text"],
    "graphicx": ["includegraphics"],
    "hyperref": ["href", "url", "hypersetup"],
    "xcolor": ["textcolor", "colorbox", "color"],
    "booktabs": ["toprule", "midrule", "bottomrule"],
    "geometry": ["geometry"],
    "listings": ["lstinputlisting", "lstlisting"],
    "tikz": ["tikzpicture", "draw"],
}


def check_packages(path: Path) -> PackageCheckResult:
    if not path.exists():
        return PackageCheckResult(error=f"File not found: {path}")

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    # Collect declared packages with line numbers
    declared: list[tuple[str, int]] = []
    for i, line in enumerate(lines, 1):
        for m in _PKG_RE.finditer(line):
            for pkg in m.group(1).split(","):
                declared.append((pkg.strip(), i))

    packages = [p for p, _ in declared]
    issues: list[PackageIssue] = []

    # Duplicate detection
    seen: dict[str, int] = {}
    for pkg, lineno in declared:
        if pkg in seen:
            issues.append(PackageIssue("duplicate", pkg, lineno))
        else:
            seen[pkg] = lineno

    # Heuristic unused detection
    commands_used = set(_CMD_RE.findall(text))
    for pkg, lineno in declared:
        if pkg not in _PACKAGE_COMMANDS:
            continue
        expected = _PACKAGE_COMMANDS[pkg]
        if not any(cmd in commands_used for cmd in expected):
            issues.append(PackageIssue("unused", pkg, lineno))

    return PackageCheckResult(issues=issues, packages=packages)
