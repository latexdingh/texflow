"""Extract and analyse the abstract from a LaTeX document."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AbstractResult:
    text: str | None
    word_count: int
    char_count: int
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.text is not None

    def summary(self) -> str:
        if not self.ok:
            return self.error or "No abstract found"
        return (
            f"Abstract: {self.word_count} words, {self.char_count} characters"
        )


_ABSTRACT_RE = re.compile(
    r"\\begin\{abstract\}(.*?)\\end\{abstract\}",
    re.DOTALL,
)


def _strip_latex(text: str) -> str:
    text = re.sub(r"%.*?$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\\[a-zA-Z]+\*?\{[^}]*\}", " ", text)
    text = re.sub(r"\\[a-zA-Z]+\*?", " ", text)
    text = re.sub(r"[{}]", "", text)
    return text.strip()


def extract_abstract(path: Path) -> AbstractResult:
    if not path.exists():
        return AbstractResult(text=None, word_count=0, char_count=0, error=f"File not found: {path}")
    source = path.read_text(encoding="utf-8", errors="replace")
    match = _ABSTRACT_RE.search(source)
    if not match:
        return AbstractResult(text=None, word_count=0, char_count=0, error="No abstract environment found")
    raw = match.group(1)
    clean = _strip_latex(raw)
    words = [w for w in clean.split() if w]
    return AbstractResult(text=clean, word_count=len(words), char_count=len(clean))
