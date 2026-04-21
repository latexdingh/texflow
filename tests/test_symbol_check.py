"""Tests for texflow.symbol_check."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from texflow.symbol_check import check_symbols, SymbolCheckResult
from texflow.symbol_check_cli import symbol_group


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "test.tex"
    p.write_text(content, encoding="utf-8")
    return p


def test_missing_file_returns_error() -> None:
    result = check_symbols(Path("/nonexistent/file.tex"))
    assert not result.ok()
    assert result.error is not None


def test_clean_file_returns_ok(tmp_path: Path) -> None:
    p = _write(tmp_path, "Hello \\LaTeX\n")
    result = check_symbols(p)
    assert result.ok()
    assert result.summary() == "No symbol issues found."


def test_detects_ldots(tmp_path: Path) -> None:
    p = _write(tmp_path, "See item 1...\n")
    result = check_symbols(p)
    assert not result.ok()
    assert any("ldots" in i.description for i in result.issues)


def test_detects_neq(tmp_path: Path) -> None:
    p = _write(tmp_path, "$a != b$\n")
    result = check_symbols(p)
    assert not result.ok()
    assert any("neq" in i.description for i in result.issues)


def test_pure_comment_line_skipped(tmp_path: Path) -> None:
    p = _write(tmp_path, "% See item 1...\n")
    result = check_symbols(p)
    assert result.ok()


def test_inline_comment_stripped(tmp_path: Path) -> None:
    # The ... is after a comment marker, should be ignored
    p = _write(tmp_path, "Hello world % See item 1...\n")
    result = check_symbols(p)
    assert result.ok()


def test_issue_str_contains_line_number(tmp_path: Path) -> None:
    p = _write(tmp_path, "\nSee item 1...\n")
    result = check_symbols(p)
    assert any(":2:" in str(i) for i in result.issues)


def test_summary_count(tmp_path: Path) -> None:
    p = _write(tmp_path, "item 1... and item 2...\n")
    result = check_symbols(p)
    assert "2" in result.summary() or int(result.summary().split()[0]) >= 2


# --- CLI tests ---

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_cli_check_clean_file(runner: CliRunner, tmp_path: Path) -> None:
    p = _write(tmp_path, "Hello \\LaTeX\n")
    res = runner.invoke(symbol_group, ["check", str(p)])
    assert res.exit_code == 0
    assert "No symbol issues" in res.output


def test_cli_check_exits_nonzero_on_issues(runner: CliRunner, tmp_path: Path) -> None:
    p = _write(tmp_path, "See item 1...\n")
    res = runner.invoke(symbol_group, ["check", str(p)])
    assert res.exit_code != 0


def test_cli_summary_command(runner: CliRunner, tmp_path: Path) -> None:
    p = _write(tmp_path, "Hello \\LaTeX\n")
    res = runner.invoke(symbol_group, ["summary", str(p)])
    assert res.exit_code == 0
    assert "No symbol" in res.output
