"""Word count utilities for LaTeX source files."""
from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path


_COMMENT_RE = re.compile(r'%.*')
_COMMAND_RE = re.compile(r'\\[a-zA-Z]+')
_BRACE_RE = re.compile(r'[{}]')
_ENV_RE = re.compile(r'\\(begin|end)\{[^}]+\}')


@dataclass
class WordCountResult:
    path: str
    total_words: int
    body_words: int
    math_envs: int

    def summary(self) -> str:
        return (
            f"{self.path}: {self.total_words} words total, "
            f"{self.body_words} body words, {self.math_envs} math environment(s)"
        )


def _strip_comments(text: str) -> str:
    return _COMMENT_RE.sub('', text)


def _count_math_envs(text: str) -> int:
    display = len(re.findall(r'\\\[', text)) + len(re.findall(r'\\begin\{(equation|align|gather|multline)\*?\}', text))
    return display


def count_words(path: Path) -> WordCountResult:
    """Count words in a .tex file, stripping commands and comments."""
    text = path.read_text(encoding='utf-8', errors='replace')
    math_envs = _count_math_envs(text)
    stripped = _strip_comments(text)
    # Remove display math blocks
    stripped = re.sub(r'\$\$.*?\$\$', ' ', stripped, flags=re.DOTALL)
    stripped = re.sub(r'\\\[.*?\\\]', ' ', stripped, flags=re.DOTALL)
    stripped = re.sub(r'\\begin\{(equation|align|gather|multline)\*?\}.*?\\end\{\1\*?\}', ' ', stripped, flags=re.DOTALL)
    # Remove inline math
    stripped = re.sub(r'\$[^$]+\$', ' ', stripped)
    # Remove LaTeX commands but keep their arguments
    stripped = _COMMAND_RE.sub(' ', stripped)
    stripped = _BRACE_RE.sub(' ', stripped)
    all_words = stripped.split()
    total = len(all_words)
    # Body words: exclude preamble (before \begin{document})
    body_match = re.search(r'\\begin\{document\}(.*)', text, re.DOTALL)
    if body_match:
        body_text = _strip_comments(body_match.group(1))
        body_text = re.sub(r'\\[a-zA-Z]+', ' ', body_text)
        body_text = _BRACE_RE.sub(' ', body_text)
        body_words = len(body_text.split())
    else:
        body_words = total
    return WordCountResult(path=str(path), total_words=total, body_words=body_words, math_envs=math_envs)
