"""Tests for texflow.macro."""
import pytest
from pathlib import Path
from texflow.macro import check_macros, MacroResult


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content)
    return p


def test_missing_file_returns_empty(tmp_path):
    result = check_macros(tmp_path / "none.tex")
    assert isinstance(result, MacroResult)
    assert result.defined == []
    assert result.issues == []


def test_no_macros_returns_ok(tmp_path):
    p = _write(tmp_path, r"\documentclass{article}" + "\n" + r"\begin{document}hello\end{document}")
    result = check_macros(p)
    assert result.ok()
    assert result.defined == []


def test_detects_unused_macro(tmp_path):
    content = (
        r"\newcommand{\myfoo}{bar}" + "\n"
        r"\begin{document}nothing\end{document}"
    )
    p = _write(tmp_path, content)
    result = check_macros(p)
    assert not result.ok()
    kinds = [i.kind for i in result.issues]
    assert "unused" in kinds


def test_used_macro_no_issue(tmp_path):
    content = (
        r"\newcommand{\myfoo}{bar}" + "\n"
        r"\begin{document}\myfoo{}\end{document}"
    )
    p = _write(tmp_path, content)
    result = check_macros(p)
    assert result.ok()
    assert "myfoo" in result.defined


def test_detects_duplicate_macro(tmp_path):
    content = (
        r"\newcommand{\myfoo}{a}" + "\n"
        r"\newcommand{\myfoo}{b}" + "\n"
        r"\begin{document}\myfoo\end{document}"
    )
    p = _write(tmp_path, content)
    result = check_macros(p)
    kinds = [i.kind for i in result.issues]
    assert "duplicate" in kinds


def test_summary_ok(tmp_path):
    content = (
        r"\newcommand{\bar}{x}" + "\n"
        r"\begin{document}\bar\end{document}"
    )
    result = check_macros(_write(tmp_path, content))
    assert "no issues" in result.summary()


def test_summary_issues(tmp_path):
    content = r"\newcommand{\unused}{x}" + "\n" + r"\begin{document}hi\end{document}"
    result = check_macros(_write(tmp_path, content))
    assert "issue" in result.summary()


def test_comment_lines_ignored(tmp_path):
    content = (
        "% \\newcommand{\\ghost}{x}\n"
        r"\begin{document}hi\end{document}"
    )
    result = check_macros(_write(tmp_path, content))
    assert "ghost" not in result.defined
