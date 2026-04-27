"""Tests for texflow.figure."""
from pathlib import Path
import pytest
from texflow.figure import check_figures, FigureResult


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_missing_file_returns_empty(tmp_path):
    result = check_figures(tmp_path / "nonexistent.tex")
    assert isinstance(result, FigureResult)
    assert result.figures == []
    assert result.ok()


def test_no_figures_returns_ok(tmp_path):
    tex = _write(tmp_path, "main.tex", "Hello world\n")
    result = check_figures(tex)
    assert result.ok()
    assert result.figures == []


def test_detects_missing_figure(tmp_path):
    tex = _write(tmp_path, "main.tex", "\\includegraphics{fig1}\n")
    result = check_figures(tex, tmp_path)
    assert "fig1" in result.figures
    assert not result.ok()
    assert result.issues[0].line == 1


def test_present_figure_no_issue(tmp_path):
    (tmp_path / "fig1.png").write_bytes(b"")
    tex = _write(tmp_path, "main.tex", "\\includegraphics{fig1}\n")
    result = check_figures(tex, tmp_path)
    assert result.ok()
    assert result.figures == ["fig1"]


def test_explicit_extension_resolved(tmp_path):
    (tmp_path / "chart.pdf").write_bytes(b"")
    tex = _write(tmp_path, "main.tex", "\\includegraphics[width=0.5\\textwidth]{chart.pdf}\n")
    result = check_figures(tex, tmp_path)
    assert result.ok()


def test_skips_comment_lines(tmp_path):
    tex = _write(tmp_path, "main.tex", "% \\includegraphics{missing}\n")
    result = check_figures(tex, tmp_path)
    assert result.figures == []


def test_summary_missing(tmp_path):
    tex = _write(tmp_path, "main.tex", "\\includegraphics{a}\n\\includegraphics{b}\n")
    result = check_figures(tex, tmp_path)
    assert "2" in result.summary()
    assert "missing" in result.summary()


def test_summary_ok(tmp_path):
    (tmp_path / "a.png").write_bytes(b"")
    tex = _write(tmp_path, "main.tex", "\\includegraphics{a}\n")
    result = check_figures(tex, tmp_path)
    assert "present" in result.summary()


def test_multiple_figures_partial_missing(tmp_path):
    """Only some figures present; result should report exactly the missing ones."""
    (tmp_path / "present.png").write_bytes(b"")
    tex = _write(
        tmp_path,
        "main.tex",
        "\\includegraphics{present}\n\\includegraphics{missing}\n",
    )
    result = check_figures(tex, tmp_path)
    assert not result.ok()
    missing_names = [issue.name for issue in result.issues]
    assert "missing" in missing_names
    assert "present" not in missing_names
