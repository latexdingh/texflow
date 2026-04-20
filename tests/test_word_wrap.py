"""Tests for texflow.word_wrap."""
from pathlib import Path
import pytest
from texflow.word_wrap import check_word_wrap, WrapResult


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content, encoding="utf-8")
    return p


def test_missing_file_returns_error(tmp_path: Path) -> None:
    result = check_word_wrap(tmp_path / "missing.tex")
    assert not result.ok()
    assert "not found" in result.error


def test_clean_file_returns_ok(tmp_path: Path) -> None:
    p = _write(tmp_path, "Short line.\nAnother short line.\n")
    result = check_word_wrap(p)
    assert result.ok()
    assert result.summary() == "No wrap issues found."


def test_long_line_detected(tmp_path: Path) -> None:
    long_line = "x" * 101
    p = _write(tmp_path, long_line + "\n")
    result = check_word_wrap(p, max_len=100)
    assert not result.ok()
    assert len(result.issues) == 1
    assert result.issues[0].line == 1


def test_comment_line_skipped(tmp_path: Path) -> None:
    long_comment = "% " + "x" * 110
    p = _write(tmp_path, long_comment + "\n")
    result = check_word_wrap(p, max_len=100)
    assert result.ok()


def test_multiple_long_lines(tmp_path: Path) -> None:
    lines = ["a" * 105, "b" * 102, "short"]
    p = _write(tmp_path, "\n".join(lines))
    result = check_word_wrap(p, max_len=100)
    assert len(result.issues) == 2


def test_summary_counts_issues(tmp_path: Path) -> None:
    lines = ["a" * 105, "b" * 102]
    p = _write(tmp_path, "\n".join(lines))
    result = check_word_wrap(p, max_len=100)
    assert "2" in result.summary()


def test_suggestion_breaks_at_space(tmp_path: Path) -> None:
    line = "word " * 22  # each repetition is 5 chars → 110 chars total
    p = _write(tmp_path, line.rstrip() + "\n")
    result = check_word_wrap(p, max_len=100)
    assert result.issues
    assert result.issues[0].suggestion.endswith("%")


def test_custom_max_len(tmp_path: Path) -> None:
    p = _write(tmp_path, "x" * 60 + "\n")
    assert check_word_wrap(p, max_len=80).ok()
    assert not check_word_wrap(p, max_len=50).ok()
