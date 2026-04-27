"""Tests for texflow.citation_style_cli."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from texflow.citation_style_cli import citation_style_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def _tex(tmp_path: Path, content: str) -> str:
    p = tmp_path / "main.tex"
    p.write_text(content, encoding="utf-8")
    return str(p)


def test_check_clean_file_exits_zero(runner: CliRunner, tmp_path: Path) -> None:
    path = _tex(tmp_path, "See~\\cite{x}.\n")
    result = runner.invoke(citation_style_group, ["check", path])
    assert result.exit_code == 0
    assert "OK" in result.output


def test_check_missing_tilde_exits_nonzero(runner: CliRunner, tmp_path: Path) -> None:
    path = _tex(tmp_path, "See \\cite{x}.\n")
    result = runner.invoke(citation_style_group, ["check", path])
    assert result.exit_code != 0
    assert "non-breaking" in result.output


def test_check_shows_styles_used(runner: CliRunner, tmp_path: Path) -> None:
    path = _tex(tmp_path, "See~\\citep{x}.\n")
    result = runner.invoke(citation_style_group, ["check", path])
    assert "citep" in result.output


def test_check_no_require_tilde_flag(runner: CliRunner, tmp_path: Path) -> None:
    path = _tex(tmp_path, "See \\cite{x}.\n")
    result = runner.invoke(citation_style_group, ["check", "--no-require-tilde", path])
    assert result.exit_code == 0


def test_summary_command(runner: CliRunner, tmp_path: Path) -> None:
    path = _tex(tmp_path, "")
    result = runner.invoke(citation_style_group, ["summary", path])
    assert result.exit_code == 0
    assert "OK" in result.output
