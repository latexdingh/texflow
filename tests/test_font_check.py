"""Tests for texflow.font_check."""
from __future__ import annotations

from pathlib import Path

import pytest

from texflow.font_check import check_fonts


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content, encoding="utf-8")
    return p


def test_missing_file_returns_missing(tmp_path: Path) -> None:
    result = check_fonts(tmp_path / "ghost.tex")
    assert result.missing
    assert not result.ok()
    assert "not found" in result.summary().lower()


def test_clean_file_returns_ok(tmp_path: Path) -> None:
    p = _write(tmp_path, r"\documentclass{article}" + "\n" + r"\begin{document}Hello\end{document}")
    result = check_fonts(p)
    assert result.ok()
    assert result.issues == []


def test_detects_legacy_rm(tmp_path: Path) -> None:
    p = _write(tmp_path, r"\begin{document}{\rm old style}\end{document}")
    result = check_fonts(p)
    assert not result.ok()
    assert any("\\rm" in str(i) for i in result.issues)


def test_detects_legacy_bf(tmp_path: Path) -> None:
    p = _write(tmp_path, r"\begin{document}{\bf bold}\end{document}")
    result = check_fonts(p)
    issue_msgs = [i.message for i in result.issues]
    assert any("bf" in m for m in issue_msgs)


def test_detects_declared_fonts(tmp_path: Path) -> None:
    content = (
        r"\usepackage{fontspec}" + "\n"
        r"\setmainfont{TeX Gyre Termes}" + "\n"
        r"\setsansfont{DejaVu Sans}" + "\n"
    )
    p = _write(tmp_path, content)
    result = check_fonts(p)
    assert "TeX Gyre Termes" in result.fonts_declared
    assert "DejaVu Sans" in result.fonts_declared


def test_fontspec_and_fontenc_conflict(tmp_path: Path) -> None:
    content = (
        r"\usepackage{fontspec}" + "\n"
        r"\usepackage[T1]{fontenc}" + "\n"
    )
    p = _write(tmp_path, content)
    result = check_fonts(p)
    assert not result.ok()
    assert any("fontenc" in i.message for i in result.issues)


def test_fontspec_and_inputenc_conflict(tmp_path: Path) -> None:
    content = (
        r"\usepackage{fontspec}" + "\n"
        r"\usepackage[utf8]{inputenc}" + "\n"
    )
    p = _write(tmp_path, content)
    result = check_fonts(p)
    assert not result.ok()
    assert any("inputenc" in i.message for i in result.issues)


def test_comment_lines_skipped(tmp_path: Path) -> None:
    p = _write(tmp_path, "% {\\rm this is a comment}\n")
    result = check_fonts(p)
    assert result.ok()


def test_summary_no_issues(tmp_path: Path) -> None:
    p = _write(tmp_path, r"\documentclass{article}")
    result = check_fonts(p)
    assert "No font issues" in result.summary()


def test_summary_with_issues(tmp_path: Path) -> None:
    p = _write(tmp_path, r"{\it italic}")
    result = check_fonts(p)
    assert "issue" in result.summary()
