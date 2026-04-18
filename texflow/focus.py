"""Focus mode: track and highlight a specific section during watch."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import re


@dataclass
class FocusRegion:
    label: str
    start_line: int
    end_line: int
    content: str

    def line_count(self) -> int:
        return self.end_line - self.start_line + 1

    def __str__(self) -> str:
        return f"[{self.label}] lines {self.start_line}–{self.end_line} ({self.line_count()} lines)"


@dataclass
class FocusResult:
    region: FocusRegion | None = None
    error: str = ""

    def ok(self) -> bool:
        return self.region is not None and not self.error


_SECTION_RE = re.compile(
    r"^\\(part|chapter|section|subsection|subsubsection)\*?\{(.+?)\}",
    re.MULTILINE,
)


def find_focus(path: Path, label: str) -> FocusResult:
    """Find the section matching *label* (-insensitive) and return its lines."""
    if not path.exists():
        return FocusResult(error=f"File not found: {path}")

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    matches: list[tuple[int, str]] = []
    for i, line in enumerate(lines, start=1):
        m = _SECTION_RE.match(line.strip())
        if m and label.lower() in m.group(2).lower():
            matches.append((i, m.group(2)))

    if not matches:
        return FocusResult(error=f"No section matching '{label}' found in {path.name}")

    start_line, matched_label = matches[0]

    # Find end: next section at same or higher level, or EOF
    end_line = len(lines)
    for i in range(start_line, len(lines)):
        if i == start_line - 1:
            continue
        if _SECTION_RE.match(lines[i].strip()):
            end_line = i  # 1-based: line i is 0-based index i
            break

    region_lines = lines[start_line - 1 : end_line]
    return FocusResult(
        region=FocusRegion(
            label=matched_label,
            start_line=start_line,
            end_line=start_line - 1 + len(region_lines),
            content="\n".join(region_lines),
        )
    )
