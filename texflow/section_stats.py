"""Per-section word and equation counts for a LaTeX document."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List
import re


@dataclass
class SectionStat:
    title: str
    level: str  # section / subsection / subsubsection
    line: int
    word_count: int
    equation_count: int

    def __str__(self) -> str:
        return (
            f"[{self.level}] {self.title} (line {self.line}) "
            f"— {self.word_count} words, {self.equation_count} equations"
        )


@dataclass
class SectionStatsResult:
    sections: List[SectionStat] = field(default_factory=list)
    error: str = ""

    def ok(self) -> bool:
        return not self.error

    def summary(self) -> str:
        if self.error:
            return f"error: {self.error}"
        if not self.sections:
            return "no sections found"
        total_words = sum(s.word_count for s in self.sections)
        return f"{len(self.sections)} section(s), {total_words} total words"


_SECTION_RE = re.compile(
    r"^\\(subsubsection|subsection|section)\*?\{([^}]+)\}", re.MULTILINE
)
_MATH_RE = re.compile(r"\\begin\{(equation|align|gather|multline)\*?\}")
_WORD_RE = re.compile(r"[a-zA-Z]{2,}")
_COMMENT_RE = re.compile(r"%.*$", re.MULTILINE)
_CMD_RE = re.compile(r"\\[a-zA-Z]+")


def _clean(text: str) -> str:
    text = _COMMENT_RE.sub("", text)
    text = _CMD_RE.sub("", text)
    return text


def gather_section_stats(path: Path) -> SectionStatsResult:
    if not path.exists():
        return SectionStatsResult(error=f"{path} not found")
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    boundaries: list[tuple[int, str, str]] = []
    for i, line in enumerate(lines, 1):
        m = _SECTION_RE.match(line.strip())
        if m:
            boundaries.append((i, m.group(1), m.group(2)))

    results: list[SectionStat] = []
    for idx, (lineno, level, title) in enumerate(boundaries):
        start = lineno  # 1-based
        end = boundaries[idx + 1][0] - 1 if idx + 1 < len(boundaries) else len(lines)
        chunk = "\n".join(lines[start:end])
        words = len(_WORD_RE.findall(_clean(chunk)))
        equations = len(_MATH_RE.findall(chunk))
        results.append(SectionStat(title=title, level=level, line=lineno,
                                   word_count=words, equation_count=equations))
    return SectionStatsResult(sections=results)
