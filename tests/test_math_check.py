"""Tests for texflow.math_check."""
from pathlib import Path
import pytest
from texflow.math_check import check_math, MathCheckResult


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content, encoding="utf-8")
    return p


def test_missing_file_returns_empty(tmp_path):
    result = check_math(tmp_path / "nope.tex")
    assert result.ok()
    assert result.issues == []


def test_clean_file_returns_ok(tmp_path):
    p = _write(tmp_path, r"\( x^2 + y^2 = z^2 \)" + "\n")
    result = check_math(p)
    assert result.ok()


def test_unmatched_inline_dollar(tmp_path):
    p = _write(tmp_path, "Here is $x + y without closing.\n")
    result = check_math(p)
    assert not result.ok()
    assert any("Unmatched inline $" in str(i) for i in result.issues)


def test_matched_inline_dollars_ok(tmp_path):
    p = _write(tmp_path, "Inline $x + y$ is fine.\n")
    result = check_math(p)
    assert result.ok()


def test_frac_no_braces(tmp_path):
    p = _write(tmp_path, r"$\frac 1 2$" + "\n")
    result = check_math(p)
    assert not result.ok()
    assert any("frac" in str(i) for i in result.issues)


def test_frac_with_braces_ok(tmp_path):
    p = _write(tmp_path, r"$\frac{1}{2}$" + "\n")
    result = check_math(p)
    assert result.ok()


def test_empty_equation_env(tmp_path):
    p = _write(tmp_path, "\\begin{equation}\n\\end{equation}\n")
    result = check_math(p)
    assert not result.ok()
    assert any("Empty math environment" in str(i) for i in result.issues)


def test_non_empty_equation_ok(tmp_path):
    p = _write(tmp_path, "\\begin{equation}\n  x = 1\n\\end{equation}\n")
    result = check_math(p)
    assert result.ok()


def test_summary_no_issues():
    r = MathCheckResult()
    assert "No math" in r.summary()


def test_summary_with_issues(tmp_path):
    p = _write(tmp_path, "$x\n")
    r = check_math(p)
    assert "issue" in r.summary()
