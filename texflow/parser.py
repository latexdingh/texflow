"""Parse LaTeX compiler output into structured error/warning objects."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Optional

ERROR_RE = re.compile(r"^!\s*(.+)$", re.MULTILINE)
LINE_RE = re.compile(r"^l\.(\d+)", re.MULTILINE)
WARNING_RE = re.compile(
    r"^LaTeX Warning:\s*(.+?)(?:\s+on input line (\d+))?\.?$", re.MULTILINE
)
FILE_RE = re.compile(r"\(([^()\n]+\.tex)")


@dataclass
class LatexError:
    message: str
    line: Optional[int] = None
    file: Optional[str] = None
    kind: str = "error"

    def __str__(self) -> str:
        loc = f":{self.line}" if self.line else ""
        src = f"{self.file}{loc}" if self.file else (f"line {self.line}" if self.line else "unknown location")
        return f"[{self.kind.upper()}] {src} — {self.message}"


@dataclass
class ParseResult:
    errors: List[LatexError] = field(default_factory=list)
    warnings: List[LatexError] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        parts = []
        if self.errors:
            parts.append(f"{len(self.errors)} error(s)")
        if self.warnings:
            parts.append(f"{len(self.warnings)} warning(s)")
        return ", ".join(parts) if parts else "no issues"


def parse_log(log_text: str) -> ParseResult:
    result = ParseResult()
    files = FILE_RE.findall(log_text)
    current_file = files[0] if files else None

    for match in ERROR_RE.finditer(log_text):
        msg = match.group(1).strip()
        after = log_text[match.end():match.end() + 200]
        line_match = LINE_RE.search(after)
        line = int(line_match.group(1)) if line_match else None
        result.errors.append(LatexError(message=msg, line=line, file=current_file, kind="error"))

    for match in WARNING_RE.finditer(log_text):
        msg = match.group(1).strip()
        line = int(match.group(2)) if match.group(2) else None
        result.warnings.append(LatexError(message=msg, line=line, file=current_file, kind="warning"))

    return result
