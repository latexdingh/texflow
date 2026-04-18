"""Check for required LaTeX tools in the system environment."""
from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from typing import List, Optional

REQUIRED_TOOLS = ["pdflatex", "xelatex", "lualatex", "bibtex", "biber"]
OPTIONAL_TOOLS = ["latexmk", "makeglossaries", "makeindex", "chktex"]


@dataclass
class ToolStatus:
    name: str
    found: bool
    path: Optional[str] = None

    def __str__(self) -> str:
        if self.found:
            return f"  [ok] {self.name:<20} {self.path}"
        return f"  [missing] {self.name}"


@dataclass
class EnvCheckResult:
    required: List[ToolStatus] = field(default_factory=list)
    optional: List[ToolStatus] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(t.found for t in self.required)

    @property
    def missing_required(self) -> List[str]:
        return [t.name for t in self.required if not t.found]

    def summary(self) -> str:
        lines = ["LaTeX Environment Check", "=" * 24]
        lines.append("Required:")
        for t in self.required:
            lines.append(str(t))
        lines.append("Optional:")
        for t in self.optional:
            lines.append(str(t))
        if self.ok:
            lines.append("\nAll required tools are available.")
        else:
            missing = ", ".join(self.missing_required)
            lines.append(f"\nMissing required tools: {missing}")
        return "\n".join(lines)


def _probe(name: str) -> ToolStatus:
    path = shutil.which(name)
    return ToolStatus(name=name, found=path is not None, path=path)


def check_environment(
    required: List[str] | None = None,
    optional: List[str] | None = None,
) -> EnvCheckResult:
    req = required if required is not None else REQUIRED_TOOLS
    opt = optional if optional is not None else OPTIONAL_TOOLS
    return EnvCheckResult(
        required=[_probe(t) for t in req],
        optional=[_probe(t) for t in opt],
    )
