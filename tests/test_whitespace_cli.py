"""Tests for texflow.whitespace_cli."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from texflow.whitespace_cli import whitespace_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def _tex(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content, encoding="utf-8")
    return p


def test_check_clean_file_exits_zero(runner: CliRunner, tmp_path: Path) -> None:
    p = _tex(tmp_path, "Hello world\n")
    result = runner.invoke(whitespace_group, ["check", str(p)])
    assert result.exit_code == 0
    assert "No whitespace" in result.output


def test_check_trailing_exits_nonzero(runner: CliRunner, tmp_path: Path) -> None:
    p = _tex(tmp_path, "Hello   \n")
    result = runner.invoke(whitespace_group, ["check", str(p)])
    assert result.exit_code != 0
    assert "trailing" in result.output


def test_check_tab_exits_nonzero(runner: CliRunner, tmp_path: Path) -> None:
    p = _tex(tmp_path, "\tindented\n")
    result = runner.invoke(whitespace_group, ["check", str(p)])
    assert result.exit_code != 0
    assert "tab" in result.output


def test_check_missing_file_exits_nonzero(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(
        whitespace_group, ["check", str(tmp_path / "missing.tex")]
    )
    assert result.exit_code != 0
    assert "not found" in result.output.lower()


def test_no_trailing_flag_suppresses(runner: CliRunner, tmp_path: Path) -> None:
    p = _tex(tmp_path, "Hello   \n")
    result = runner.invoke(whitespace_group, ["check", "--no-trailing", str(p)])
    assert result.exit_code == 0


def test_summary_command(runner: CliRunner, tmp_path: Path) -> None:
    p = _tex(tmp_path, "Hello world\n")
    result = runner.invoke(whitespace_group, ["summary", str(p)])
    assert result.exit_code == 0
    assert "No whitespace" in result.output
