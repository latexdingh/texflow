"""Tests for texflow.equation."""
from pathlib import Path
import pytest
from texflow.equation import extract_equations, EquationItem


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content, encoding="utf-8")
    return p


def test_missing_file_returns_error(tmp_path):
    result = extract_equations(tmp_path / "missing.tex")
    assert not result.ok()
    assert "not found" in result.error


def test_no_equations_returns_empty(tmp_path):
    p = _write(tmp_path, "Just some text, no math environments.\n")
    result = extract_equations(p)
    assert result.ok()
    assert result.equations == []
    assert "0 equation(s)" in result.summary()


def test_single_equation(tmp_path):
    p = _write(tmp_path, "\\begin{equation}\nE = mc^2\n\\end{equation}\n")
    result = extract_equations(p)
    assert result.ok()
    assert len(result.equations) == 1
    eq = result.equations[0]
    assert eq.line == 1
    assert eq.label is None
    assert "mc^2" in eq.source


def test_equation_with_label(tmp_path):
    content = "\\begin{equation}\n\\label{eq:energy}\nE = mc^2\n\\end{equation}\n"
    p = _write(tmp_path, content)
    result = extract_equations(p)
    assert len(result.equations) == 1
    assert result.equations[0].label == "eq:energy"


def test_align_environment(tmp_path):
    content = "\\begin{align}\na &= b \\\\\nc &= d\n\\end{align}\n"
    p = _write(tmp_path, content)
    result = extract_equations(p)
    assert len(result.equations) == 1


def test_multiple_equations(tmp_path):
    content = (
        "\\begin{equation}\\label{eq:one}x=1\\end{equation}\n"
        "Some text.\n"
        "\\begin{equation}y=2\\end{equation}\n"
    )
    p = _write(tmp_path, content)
    result = extract_equations(p)
    assert len(result.equations) == 2
    assert result.equations[0].label == "eq:one"
    assert result.equations[1].label is None


def test_summary_counts_labelled(tmp_path):
    content = (
        "\\begin{equation}\\label{eq:a}x\\end{equation}\n"
        "\\begin{equation}y\\end{equation}\n"
    )
    p = _write(tmp_path, content)
    result = extract_equations(p)
    assert "2 equation(s)" in result.summary()
    assert "1 labelled" in result.summary()


def test_str_representation(tmp_path):
    p = _write(tmp_path, "\\begin{equation}\\label{eq:z}z=0\\end{equation}\n")
    result = extract_equations(p)
    s = str(result.equations[0])
    assert "eq:z" in s
    assert "Line" in s
