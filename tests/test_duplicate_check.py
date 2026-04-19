"""Tests for texflow.duplicate_check."""
from pathlib import Path
import pytest
from texflow.duplicate_check import check_duplicates, DuplicateCheckResult


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content, encoding="utf-8")
    return p


def test_missing_file_returns_error(tmp_path: Path):
    result = check_duplicates(tmp_path / "ghost.tex")
    assert not result.ok()
    assert "not found" in result.error


def test_clean_file_returns_ok(tmp_path: Path):
    p = _write(tmp_path, "The quick brown fox jumps over the lazy dog.\n")
    result = check_duplicates(p)
    assert result.ok()
    assert result.summary() == "No duplicate words found."


def test_detects_simple_duplicate(tmp_path: Path):
    p = _write(tmp_path, "the the quick brown fox\n")
    result = check_duplicates(p)
    assert not result.ok()
    assert any(i.word == "the" for i in result.issues)


def test_duplicate_line_number(tmp_path: Path):
    p = _write(tmp_path, "first line\nword word here\n")
    result = check_duplicates(p)
    assert result.issues[0].line == 2


def test_ignores_latex_commands(tmp_path: Path):
    p = _write(tmp_path, r"\textbf{bold} \textit{italic} normal text" + "\n")
    result = check_duplicates(p)
    assert result.ok()


def test_ignores_comment_duplicates(tmp_path: Path):
    # duplicates only in comment portion should be stripped
    p = _write(tmp_path, "some text % the the\n")
    result = check_duplicates(p)
    assert result.ok()


def test_summary_reports_count(tmp_path: Path):
    p = _write(tmp_path, "is is\nare are\n")
    result = check_duplicates(p)
    assert "2" in result.summary()


def test_case_insensitive_detection(tmp_path: Path):
    p = _write(tmp_path, "The the quick\n")
    result = check_duplicates(p)
    assert any(i.word == "the" for i in result.issues)


def test_no_false_positive_single_occurrence(tmp_path: Path):
    p = _write(tmp_path, "one two three four five\n")
    result = check_duplicates(p)
    assert result.ok()
