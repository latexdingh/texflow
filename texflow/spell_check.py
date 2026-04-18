"""Simple spell-check helper using pyspellchecker if available."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class SpellIssue:
    word: str
    line: int
    suggestions: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        sugg = ", ".join(self.suggestions[:3]) or "—"
        return f"Line {self.line}: '{self.word}' → {sugg}"


@dataclass
class SpellResult:
    issues: List[SpellIssue] = field(default_factory=list)
    skipped: bool = False

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0

    def summary(self) -> str:
        if self.skipped:
            return "Spell-check skipped (pyspellchecker not installed)"
        if self.ok:
            return "No spelling issues found"
        return f"{len(self.issues)} spelling issue(s) found"


_LATEX_CMD = re.compile(r"\\[a-zA-Z]+")
_MATH_ENV = re.compile(r"\$[^$]*\$|\$\$[^$]*\$\$")
_NON_ALPHA = re.compile(r"[^a-zA-Z'-]")


def _extract_words(line: str) -> List[str]:
    line = _MATH_ENV.sub(" ", line)
    line = _LATEX_CMD.sub(" ", line)
    line = line.split("%")[0]  # strip comments
    return [w.strip("'-") for w in _NON_ALPHA.split(line) if len(w.strip("'-")) > 2]


def check_file(path: Path) -> SpellResult:
    try:
        from spellchecker import SpellChecker  # type: ignore
    except ImportError:
        return SpellResult(skipped=True)

    spell = SpellChecker()
    issues: List[SpellIssue] = []

    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return SpellResult(skipped=True)

    for lineno, line in enumerate(lines, start=1):
        words = _extract_words(line)
        misspelled = spell.unknown(words)
        for word in misspelled:
            suggestions = list(spell.candidates(word) or [])[:3]
            issues.append(SpellIssue(word=word, line=lineno, suggestions=suggestions))

    return SpellResult(issues=issues)
