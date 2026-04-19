"""Tests for texflow.abstract and abstract_cli."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from texflow.abstract import extract_abstract
from texflow.abstract_cli import abstract_group


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content)
    return p


def test_missing_file_returns_error(tmp_path: Path) -> None:
    result = extract_abstract(tmp_path / "nope.tex")
    assert not result.ok
    assert "not found" in result.error


def test_no_abstract_returns_error(tmp_path: Path) -> None:
    p = _write(tmp_path, r"\section{Intro} Hello.")
    result = extract_abstract(p)
    assert not result.ok
    assert "No abstract" in result.error


def test_extracts_abstract_text(tmp_path: Path) -> None:
    p = _write(tmp_path, r"""
\begin{abstract}
This is a short abstract with five words.
\end{abstract}
""")
    result = extract_abstract(p)
    assert result.ok
    assert "short abstract" in result.text


def test_word_count(tmp_path: Path) -> None:
    p = _write(tmp_path, r"""
\begin{abstract}
one two three four five
\end{abstract}
""")
    result = extract_abstract(p)
    assert result.word_count == 5


def test_strips_latex_commands(tmp_path: Path) -> None:
    p = _write(tmp_path, r"""
\begin{abstract}
\textbf{Bold} and \emph{italic} text.
\end{abstract}
""")
    result = extract_abstract(p)
    assert "\\textbf" not in result.text
    assert result.ok


def test_cli_show(tmp_path: Path) -> None:
    p = _write(tmp_path, r"""
\begin{abstract}
Hello world.
\end{abstract}
""")
    runner = CliRunner()
    out = runner.invoke(abstract_group, ["show", str(p)])
    assert out.exit_code == 0
    assert "Hello world" in out.output


def test_cli_info(tmp_path: Path) -> None:
    p = _write(tmp_path, r"""
\begin{abstract}
Hello world.
\end{abstract}
""")
    runner = CliRunner()
    out = runner.invoke(abstract_group, ["info", str(p)])
    assert out.exit_code == 0
    assert "Words" in out.output


def test_cli_show_missing_abstract(tmp_path: Path) -> None:
    p = _write(tmp_path, r"\section{X} nothing")
    runner = CliRunner()
    out = runner.invoke(abstract_group, ["show", str(p)])
    assert out.exit_code != 0
