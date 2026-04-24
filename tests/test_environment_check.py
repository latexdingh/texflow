"""Tests for texflow.environment_check."""
from __future__ import annotations

from pathlib import Path

import pytest

from texflow.environment_check import check_environments, EnvIssue


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "doc.tex"
    p.write_text(content, encoding="utf-8")
    return p


def test_missing_file_returns_missing(tmp_path: Path) -> None:
    result = check_environments(tmp_path / "ghost.tex")
    assert result.missing
    assert not result.ok()


def test_clean_file_returns_ok(tmp_path: Path) -> None:
    tex = _write(tmp_path, "\\begin{document}\nHello\n\\end{document}\n")
    result = check_environments(tex)
    assert result.ok()
    assert result.issues == []


def test_unmatched_begin_detected(tmp_path: Path) -> None:
    tex = _write(tmp_path, "\\begin{document}\n\\begin{itemize}\nHello\n\\end{document}\n")
    result = check_environments(tex)
    assert not result.ok()
    kinds = {i.kind for i in result.issues}
    assert "unmatched_begin" in kinds


def test_unmatched_end_detected(tmp_path: Path) -> None:
    tex = _write(tmp_path, "\\end{itemize}\n\\begin{document}\nHi\n\\end{document}\n")
    result = check_environments(tex)
    assert not result.ok()
    kinds = {i.kind for i in result.issues}
    assert "unmatched_end" in kinds


def test_mismatch_detected(tmp_path: Path) -> None:
    tex = _write(
        tmp_path,
        "\\begin{document}\n\\begin{itemize}\nHi\n\\end{enumerate}\n\\end{document}\n",
    )
    result = check_environments(tex)
    assert not result.ok()
    kinds = {i.kind for i in result.issues}
    assert "mismatch" in kinds


def test_nested_environments_ok(tmp_path: Path) -> None:
    tex = _write(
        tmp_path,
        "\\begin{document}\n\\begin{itemize}\n\\item x\n\\end{itemize}\n\\end{document}\n",
    )
    result = check_environments(tex)
    assert result.ok()


def test_comment_line_ignored(tmp_path: Path) -> None:
    tex = _write(
        tmp_path,
        "\\begin{document}\n% \\begin{itemize}\nHello\n\\end{document}\n",
    )
    result = check_environments(tex)
    assert result.ok()


def test_issue_str_contains_line(tmp_path: Path) -> None:
    tex = _write(tmp_path, "\\begin{document}\n\\end{itemize}\n\\end{document}\n")
    result = check_environments(tex)
    assert any("Line 2" in str(i) for i in result.issues)


def test_summary_reports_count(tmp_path: Path) -> None:
    tex = _write(tmp_path, "\\begin{document}\n\\end{itemize}\n\\end{document}\n")
    result = check_environments(tex)
    assert "1" in result.summary()
