"""Tests for texflow.whitespace."""
from __future__ import annotations

from pathlib import Path

import pytest

from texflow.whitespace import check_whitespace, WhitespaceIssue


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content, encoding="utf-8")
    return p


def test_missing_file_returns_missing(tmp_path: Path) -> None:
    result = check_whitespace(tmp_path / "nope.tex")
    assert result.missing
    assert not result.ok()


def test_clean_file_returns_ok(tmp_path: Path) -> None:
    p = _write(tmp_path, "Hello world\n\nBye\n")
    result = check_whitespace(p)
    assert result.ok()
    assert "No whitespace" in result.summary()


def test_trailing_space_detected(tmp_path: Path) -> None:
    p = _write(tmp_path, "Hello   \nBye\n")
    result = check_whitespace(p)
    assert not result.ok()
    kinds = {i.kind for i in result.issues}
    assert "trailing" in kinds


def test_tab_detected(tmp_path: Path) -> None:
    p = _write(tmp_path, "\tindented\n")
    result = check_whitespace(p)
    kinds = {i.kind for i in result.issues}
    assert "tab" in kinds


def test_multiple_blank_lines_detected(tmp_path: Path) -> None:
    p = _write(tmp_path, "A\n\n\nB\n")
    result = check_whitespace(p)
    kinds = {i.kind for i in result.issues}
    assert "multiple_blank" in kinds


def test_single_blank_line_ok(tmp_path: Path) -> None:
    p = _write(tmp_path, "A\n\nB\n")
    result = check_whitespace(p)
    assert result.ok()


def test_no_trailing_flag_skips(tmp_path: Path) -> None:
    p = _write(tmp_path, "Hello   \n")
    result = check_whitespace(p, check_trailing=False)
    assert result.ok()


def test_no_tabs_flag_skips(tmp_path: Path) -> None:
    p = _write(tmp_path, "\tindented\n")
    result = check_whitespace(p, check_tabs=False)
    assert result.ok()


def test_issue_str_contains_line_number(tmp_path: Path) -> None:
    p = _write(tmp_path, "Hello   \n")
    result = check_whitespace(p)
    assert any("Line 1" in str(i) for i in result.issues)


def test_summary_lists_kinds(tmp_path: Path) -> None:
    p = _write(tmp_path, "Hello   \n\t world\n")
    result = check_whitespace(p)
    s = result.summary()
    assert "trailing" in s or "tab" in s
