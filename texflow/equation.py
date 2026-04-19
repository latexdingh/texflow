"""Extract and catalogue numbered equations from LaTeX source files."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class EquationItem:
    line: int
    label: Optional[str]
    source: str

    def __str__(self) -> str:
        label_part = f" [{self.label}]" if self.label else ""
        return f"Line {self.line}{label_part}: {self.source.strip()}"


@dataclass
class EquationResult:
    equations: List[EquationItem] = field(default_factory=list)
    error: str = ""

    def ok(self) -> bool:
        return not self.error

    def summary(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        n = len(self.equations)
        labelled = sum(1 for e in self.equations if e.label)
        return f"{n} equation(s) found, {labelled} labelled."


_ENV_PATTERN = re.compile(
    r"\\begin\{(equation|align|gather|multline)\*?\}(.*?)\\end\{\1\*?\}",
    re.DOTALL,
)
_LABEL_PATTERN = re.compile(r"\\label\{([^}]+)\}")


def extract_equations(path: Path) -> EquationResult:
    if not path.exists():
        return EquationResult(error=f"File not found: {path}")

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    # Build a char-offset -> line-number map
    offsets: List[int] = []
    pos = 0
    for ln in lines:
        offsets.append(pos)
        pos += len(ln) + 1  # +1 for newline

    def line_of(char_pos: int) -> int:
        lo, hi = 0, len(offsets) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if offsets[mid] <= char_pos:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1  # 1-based

    items: List[EquationItem] = []
    for m in _ENV_PATTERN.finditer(text):
        body = m.group(2)
        label_m = _LABEL_PATTERN.search(body)
        label = label_m.group(1) if label_m else None
        source_line = line_of(m.start())
        items.append(EquationItem(line=source_line, label=label, source=body.strip()))

    return EquationResult(equations=items)
