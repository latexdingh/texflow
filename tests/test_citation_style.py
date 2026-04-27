"""Tests for texflow.citation_style."""
from __future__ import annotations

from pathlib import Path

import pytest

from texflow.citation_style import check_citation_style


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content, encoding="utf-8")
    return p


def test_missing_file_returns_missing(tmp_path: Path) -> None:
    result = check_citation_style(tmp_path / "ghost.tex")
    assert result.missing
    assert not result.ok()
    assert "not found" in result.summary()


def test_no_citations_returns_ok(tmp_path: Path) -> None:
    p = _write(tmp_path, "Hello world.\n")
    result = check_citation_style(p)
    assert result.ok()
    assert result.cite_count == 0
    assert result.styles_found == []


def test_single_cite_with_tilde_ok(tmp_path: Path) -> None:
    p = _write(tmp_path, "See~\\cite{key2024}.\n")
    result = check_citation_style(p, require_tilde=True)
    assert result.ok()
    assert result.cite_count == 1
    assert "cite" in result.styles_found


def test_detects_missing_tilde(tmp_path: Path) -> None:
    p = _write(tmp_path, "See \\cite{key2024} for details.\n")
    result = check_citation_style(p, require_tilde=True)
    assert not result.ok()
    assert any("non-breaking" in i.message for i in result.issues)


def test_no_tilde_required_passes(tmp_path: Path) -> None:
    p = _write(tmp_path, "See \\cite{key2024} for details.\n")
    result = check_citation_style(p, require_tilde=False)
    assert result.ok()


def test_citep_style_recorded(tmp_path: Path) -> None:
    p = _write(tmp_path, "Result~\\citep{smith2020}.\n")
    result = check_citation_style(p, require_tilde=True)
    assert "citep" in result.styles_found


def test_multi_key_allowed_by_default(tmp_path: Path) -> None:
    p = _write(tmp_path, "See~\\cite{a,b,c}.\n")
    result = check_citation_style(p, require_tilde=True, disallow_multi_key=False)
    assert result.ok()


def test_multi_key_disallowed_raises_issue(tmp_path: Path) -> None:
    p = _write(tmp_path, "See~\\cite{a,b}.\n")
    result = check_citation_style(p, require_tilde=True, disallow_multi_key=True)
    assert not result.ok()
    assert any("Multiple keys" in i.message for i in result.issues)


def test_comment_lines_skipped(tmp_path: Path) -> None:
    p = _write(tmp_path, "% See \\cite{ignored} here\n")
    result = check_citation_style(p, require_tilde=True)
    assert result.ok()
    assert result.cite_count == 0


def test_summary_ok_message(tmp_path: Path) -> None:
    p = _write(tmp_path, "See~\\cite{x}.\n")
    result = check_citation_style(p)
    assert "OK" in result.summary()
    assert "1" in result.summary()
