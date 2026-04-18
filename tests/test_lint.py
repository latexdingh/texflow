"""Tests for texflow.lint."""
from pathlib import Path
import pytest
from texflow.lint import lint_file, LintResult, LintIssue


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content, encoding="utf-8")
    return p


def test_clean_file_returns_ok(tmp_path):
    p = _write(tmp_path, r"\documentclass{article}" + "\n" + r"\begin{document}Hello\end{document}")
    result = lint_file(p)
    assert result.ok
    assert result.summary() == "No lint issues found."


def test_detects_double_dollar(tmp_path):
    p = _write(tmp_path, "$$x^2$$\n")
    result = lint_file(p)
    codes = [i.code for i in result.issues]
    assert "W003" in codes


def test_detects_todo_comment(tmp_path):
    p = _write(tmp_path, "Some text % TODO fix this\n")
    result = lint_file(p)
    codes = [i.code for i in result.issues]
    assert "W004" in codes


def test_skips_pure_comment_lines(tmp_path):
    p = _write(tmp_path, "% TODO this is a pure comment line\n")
    result = lint_file(p)
    assert result.ok


def test_detects_multiple_spaces(tmp_path):
    p = _write(tmp_path, "word  word\n")
    result = lint_file(p)
    codes = [i.code for i in result.issues]
    assert "W002" in codes


def test_missing_file_returns_error():
    result = lint_file(Path("/nonexistent/file.tex"))
    assert not result.ok
    assert result.issues[0].code == "E999"


def test_lint_issue_str():
    issue = LintIssue(line=5, code="W001", message="test message")
    assert "L5" in str(issue)
    assert "W001" in str(issue)
    assert "test message" in str(issue)


def test_summary_counts_issues(tmp_path):
    p = _write(tmp_path, "$$x$$ % TODO fix\nword  word\n")
    result = lint_file(p)
    assert not result.ok
    assert str(len(result.issues)) in result.summary()
