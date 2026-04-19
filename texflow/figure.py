"""Figure inventory: scan .tex files for \includegraphics references and check file existence."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

_GRAPHICS_RE = re.compile(r'\\includegraphics(?:\[.*?\])?\{([^}]+)\}')
_IMAGE_EXTS = (".pdf", ".png", ".jpg", ".jpeg", ".eps")


@dataclass
class FigureIssue:
    path: str
    line: int
    message: str

    def __str__(self) -> str:
        return f"Line {self.line}: {self.message} ({self.path})"


@dataclass
class FigureResult:
    figures: List[str] = field(default_factory=list)
    issues: List[FigureIssue] = field(default_factory=list)

    def ok(self) -> bool:
        return len(self.issues) == 0

    def summary(self) -> str:
        if self.ok():
            return f"{len(self.figures)} figure(s) found, all present."
        return f"{len(self.figures)} figure(s) found, {len(self.issues)} missing."


def _resolve_figure(ref: str, base: Path) -> Optional[Path]:
    p = Path(ref)
    if p.suffix in _IMAGE_EXTS:
        candidates = [base / p]
    else:
        candidates = [base / (ref + ext) for ext in _IMAGE_EXTS]
    for c in candidates:
        if c.exists():
            return c
    return None


def check_figures(tex_path: Path, base_dir: Optional[Path] = None) -> FigureResult:
    if not tex_path.exists():
        return FigureResult()
    base = base_dir or tex_path.parent
    result = FigureResult()
    for lineno, line in enumerate(tex_path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("%"):
            continue
        for ref in _GRAPHICS_RE.findall(line):
            result.figures.append(ref)
            if _resolve_figure(ref, base) is None:
                result.issues.append(FigureIssue(ref, lineno, f"Missing figure file"))
    return result
