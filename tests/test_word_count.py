"""Tests for word count module and CLI."""
from pathlib import Path
import pytest
from click.testing import CliRunner
from texflow.word_count import count_words, WordCountResult
from texflow.word_count_cli import wordcount_group


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding='utf-8')
    return p


DOC = r"""
\documentclass{article}
\begin{document}
Hello world this is a test.
\end{document}
"""

DOC_MATH = r"""
\documentclass{article}
\begin{document}
Some text here.
\begin{equation}
x = y + z
\end{equation}
More words after.
\end{document}
"""


def test_count_words_basic(tmp_path):
    p = _write(tmp_path, 'main.tex', DOC)
    result = count_words(p)
    assert result.total_words >= 5
    assert isinstance(result, WordCountResult)


def test_body_words_less_than_total(tmp_path):
    content = r"\documentclass{article}\n\begin{document}\nHello world.\n\end{document}"
    p = _write(tmp_path, 'main.tex', DOC)
    result = count_words(p)
    assert result.body_words <= result.total_words


def test_math_env_counted(tmp_path):
    p = _write(tmp_path, 'main.tex', DOC_MATH)
    result = count_words(p)
    assert result.math_envs >= 1


def test_summary_string(tmp_path):
    p = _write(tmp_path, 'main.tex', DOC)
    result = count_words(p)
    s = result.summary()
    assert 'words' in s
    assert 'main.tex' in s


def test_cli_count(tmp_path):
    p = _write(tmp_path, 'main.tex', DOC)
    runner = CliRunner()
    res = runner.invoke(wordcount_group, ['count', str(p)])
    assert res.exit_code == 0
    assert 'main.tex' in res.output


def test_cli_count_body_only(tmp_path):
    p = _write(tmp_path, 'main.tex', DOC)
    runner = CliRunner()
    res = runner.invoke(wordcount_group, ['count', '--body-only', str(p)])
    assert res.exit_code == 0
    assert 'body words' in res.output


def test_cli_summary(tmp_path):
    p = _write(tmp_path, 'main.tex', DOC)
    runner = CliRunner()
    res = runner.invoke(wordcount_group, ['summary', str(p)])
    assert res.exit_code == 0
    assert 'words total' in res.output


def test_cli_non_tex_skipped(tmp_path):
    p = _write(tmp_path, 'notes.txt', 'hello world')
    runner = CliRunner()
    res = runner.invoke(wordcount_group, ['count', str(p)])
    assert 'Skipping' in res.output
