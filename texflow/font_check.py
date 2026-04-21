"""Font usage checker for LaTeX source files."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class FontIssue:
    line: int
    message: str
    context: str = ""

    def __str__(self) -> str:
        ctx = f" — {self.context}" if self.context else ""
        return f"Line {self.line}: {self.message}{ctx}"


@dataclass
class FontCheckResult:
    issues: List[FontIssue] = field(default_factory=list)
    fonts_declared: List[str] = field(default_factory=list)
    missing: bool = False

    def ok(self) -> bool:
        return not self.issues

    def summary(self) -> str:
        if self.missing:
            return "File not found."
        if not self.issues:
            n = len(self.fonts_declared)
            return f"No font issues. {n} font declaration(s) found."
        return f"{len(self.issues)} font issue(s) detected."


_FONT_CMDS = re.compile(
    r"\\(setmainfont|setsansfont|setmonofont|fontfamily|usefont|\\newfontfamily)"
    r"\s*(?:\[.*?\])?\s*\{([^}]*)\}",
    re.DOTALL,
)
_ENCODING_CMD = re.compile(r"\\usepackage\s*(?:\[.*?\])?\s*\{fontenc\}")
_INPUTENC_CMD = re.compile(r"\\usepackage\s*(?:\[.*?\])?\s*\{inputenc\}")
_LEGACY_FONT = re.compile(r"\\(rm|sf|tt|bf|it|sl|sc)(?=\s|\{|\\|$)")


def check_fonts(path: Path) -> FontCheckResult:
    if not path.exists():
        return FontCheckResult(missing=True)

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    issues: List[FontIssue] = []
    fonts_declared: List[str] = []

    for m in _FONT_CMDS.finditer(text):
        fonts_declared.append(m.group(2).strip())

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("%"):
            continue
        for m in _LEGACY_FONT.finditer(stripped):
            issues.append(
                FontIssue(
                    line=lineno,
                    message=f"Legacy font command '\\{m.group(1)}' — prefer font environment or fontspec",
                    context=stripped[:60],
                )
            )

    has_fontspec = any(
        re.search(r"\\usepackage\s*(?:\[.*?\])?\s*\{fontspec\}", line)
        for line in lines
    )
    has_fontenc = bool(_ENCODING_CMD.search(text))
    has_inputenc = bool(_INPUTENC_CMD.search(text))

    if has_fontspec and has_fontenc:
        issues.append(
            FontIssue(
                line=0,
                message="fontspec and fontenc are both loaded — fontspec manages encoding automatically",
            )
        )
    if has_fontspec and has_inputenc:
        issues.append(
            FontIssue(
                line=0,
                message="fontspec and inputenc are both loaded — inputenc is unnecessary with fontspec",
            )
        )

    return FontCheckResult(issues=issues, fonts_declared=fonts_declared)
