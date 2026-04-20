"""Tests for texflow.word_wrap_cli."""
from pathlib import Path
import pytest
from click.testing import CliRunner
from texflow.word_wrap_cli import wrap_group


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def _tex(tmp_path: Path, content: str) -> str:
    p = tmp_path / "doc.tex"
    p.write_text(content, encoding="utf-8")
    return str(p)


def test_check_clean_file(runner: CliRunner, tmp_path: Path) -> None:
    path = _tex(tmp_path, "Short.\n")
    result = runner.invoke(wrap_group, ["check", path])
    assert result.exit_code == 0
    assert "No wrap" in result.output


def test_check_long_line_exits_nonzero(runner: CliRunner, tmp_path: Path) -> None:
    path = _tex(tmp_path, "x" * 105 + "\n")
    result = runner.invoke(wrap_group, ["check", path])
    assert result.exit_code != 0
    assert "Line 1" in result.output


def test_check_custom_max_len(runner: CliRunner, tmp_path: Path) -> None:
    path = _tex(tmp_path, "x" * 60 + "\n")
    result = runner.invoke(wrap_group, ["check", "--max-len", "50", path])
    assert result.exit_code != 0


def test_summary_clean(runner: CliRunner, tmp_path: Path) -> None:
    path = _tex(tmp_path, "Short line.\n")
    result = runner.invoke(wrap_group, ["summary", path])
    assert result.exit_code == 0
    assert "No wrap" in result.output


def test_summary_issues_exits_nonzero(runner: CliRunner, tmp_path: Path) -> None:
    path = _tex(tmp_path, "y" * 110 + "\n")
    result = runner.invoke(wrap_group, ["summary", path])
    assert result.exit_code != 0
    assert "issue" in result.output
