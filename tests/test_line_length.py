"""Tests for texflow.line_length."""
from pathlib import Path
import pytest
from click.testing import CliRunner
from texflow.line_length import check_line_length, DEFAULT_MAX_LENGTH
from texflow.line_length_cli import line_length_group


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content, encoding="utf-8")
    return p


def test_missing_file_returns_error(tmp_path):
    result = check_line_length(tmp_path / "missing.tex")
    assert not result.ok()
    assert "not found" in result.error


def test_clean_file_returns_ok(tmp_path):
    p = _write(tmp_path, "Short line.\nAnother short line.\n")
    result = check_line_length(p)
    assert result.ok()
    assert result.summary() == "All lines within length limit."


def test_long_line_detected(tmp_path):
    long_line = "x" * (DEFAULT_MAX_LENGTH + 1)
    p = _write(tmp_path, f"{long_line}\n")
    result = check_line_length(p)
    assert not result.ok()
    assert len(result.issues) == 1
    assert result.issues[0].line_number == 1
    assert result.issues[0].length == DEFAULT_MAX_LENGTH + 1


def test_comment_line_skipped_by_default(tmp_path):
    long_comment = "% " + "x" * (DEFAULT_MAX_LENGTH + 5)
    p = _write(tmp_path, f"{long_comment}\n")
    result = check_line_length(p, skip_comments=True)
    assert result.ok()


def test_comment_line_checked_when_skip_disabled(tmp_path):
    long_comment = "% " + "x" * (DEFAULT_MAX_LENGTH + 5)
    p = _write(tmp_path, f"{long_comment}\n")
    result = check_line_length(p, skip_comments=False)
    assert not result.ok()


def test_custom_max_length(tmp_path):
    p = _write(tmp_path, "x" * 50 + "\n")
    result = check_line_length(p, max_length=40)
    assert not result.ok()
    assert result.issues[0].max_allowed == 40


def test_issue_str_contains_line_number(tmp_path):
    p = _write(tmp_path, "short\n" + "y" * 130 + "\n")
    result = check_line_length(p)
    assert "Line 2" in str(result.issues[0])


# CLI tests

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_check_ok(runner, tmp_path):
    p = _write(tmp_path, "Hello LaTeX\n")
    res = runner.invoke(line_length_group, ["check", str(p)])
    assert res.exit_code == 0
    assert "within" in res.output


def test_cli_check_fails_on_long_line(runner, tmp_path):
    p = _write(tmp_path, "x" * 200 + "\n")
    res = runner.invoke(line_length_group, ["check", str(p)])
    assert res.exit_code != 0
    assert "Line 1" in res.output


def test_cli_summary_command(runner, tmp_path):
    p = _write(tmp_path, "short\n")
    res = runner.invoke(line_length_group, ["summary", str(p)])
    assert res.exit_code == 0
    assert "All lines" in res.output
