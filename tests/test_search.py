"""Tests for texflow.search."""
from pathlib import Path
import pytest
from texflow.search import search_files, SearchResult


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_no_matches_returns_empty(tmp_path):
    f = _write(tmp_path, "a.tex", "Hello world\n")
    result = search_files([f], "missing")
    assert not result.ok
    assert "No matches" in result.summary()


def test_basic_match(tmp_path):
    f = _write(tmp_path, "a.tex", "line one\nfind me here\nline three\n")
    result = search_files([f], "find me")
    assert result.ok
    assert len(result.matches) == 1
    assert result.matches[0].line_number == 2


def test_case_insensitive_default(tmp_path):
    f = _write(tmp_path, "a.tex", "HELLO\n")
    result = search_files([f], "hello")
    assert result.ok


def test_case_sensitive(tmp_path):
    f = _write(tmp_path, "a.tex", "HELLO\n")
    result = search_files([f], "hello", case_sensitive=True)
    assert not result.ok


def test_regex_match(tmp_path):
    f = _write(tmp_path, "a.tex", "section{Intro}\n\\section{Body}\n")
    result = search_files([f], r"\\section\{\w+\}", regex=True)
    assert result.ok


def test_invalid_regex_raises(tmp_path):
    f = _write(tmp_path, "a.tex", "hello\n")
    with pytest.raises(ValueError):
        search_files([f], "[", regex=True)


def test_multiple_files(tmp_path):
    f1 = _write(tmp_path, "a.tex", "needle here\n")
    f2 = _write(tmp_path, "b.tex", "nothing\n")
    f3 = _write(tmp_path, "c.tex", "needle again\n")
    result = search_files([f1, f2, f3], "needle")
    assert len(result.matches) == 2


def test_missing_file_skipped(tmp_path):
    ghost = tmp_path / "ghost.tex"
    result = search_files([ghost], "anything")
    assert not result.ok


def test_column_reported(tmp_path):
    f = _write(tmp_path, "a.tex", "abc target def\n")
    result = search_files([f], "target")
    assert result.matches[0].column == 4


def test_summary_count(tmp_path):
    f = _write(tmp_path, "a.tex", "x\nx\nx\n")
    result = search_files([f], "x")
    assert "3" in result.summary()
