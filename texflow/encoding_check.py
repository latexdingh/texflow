"""Check LaTeX source files for encoding issues."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class EncodingIssue:
    file: str
    line: int
    message: str

    def __str__(self) -> str:
        return f"{self.file}:{self.line}: {self.message}"


@dataclass
class EncodingCheckResult:
    issues: List[EncodingIssue] = field(default_factory=list)
    error: str = ""

    def ok(self) -> bool:
        return not self.issues and not self.error

    def summary(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        if not self.issues:
            return "No encoding issues found."
        return f"{len(self.issues)} encoding issue(s) found."


_SUSPICIOUS = [
    ("\\usepackage{inputenc}", "inputenc declared — verify encoding matches file"),
]

_SMART_QUOTES = ["\u2018", "\u2019", "\u201c", "\u201d"]


def check_encoding(path: Path) -> EncodingCheckResult:
    if not path.exists():
        return EncodingCheckResult(error=f"File not found: {path}")

    issues: List[EncodingIssue] = []

    try:
        raw = path.read_bytes()
    except OSError as exc:
        return EncodingCheckResult(error=str(exc))

    # Check for BOM
    if raw.startswith(b"\xef\xbb\xbf"):
        issues.append(EncodingIssue(str(path), 0, "UTF-8 BOM detected — may cause pdflatex errors"))

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return EncodingCheckResult(error=f"File is not valid UTF-8: {exc}")

    for lineno, line in enumerate(text.splitlines(), start=1):
        for char in _SMART_QUOTES:
            if char in line:
                issues.append(EncodingIssue(str(path), lineno, f"Smart quote character '{char}' detected — use LaTeX quotes instead"))
                break
        for pattern, msg in _SUSPICIOUS:
            if pattern in line:
                issues.append(EncodingIssue(str(path), lineno, msg))

    return EncodingCheckResult(issues=issues)
