"""Tests for texflow.section_stats_cli."""
from pathlib import Path
from click.testing import CliRunner
import pytest
from texflow.section_stats_cli import section_stats_group


@pytest.fixture()
def runner():
    return CliRunner()


def _tex(tmp_path: Path, content: str) -> str:
    p = tmp_path / "doc.tex"
    p.write_text(content)
    return str(p)


def test_show_no_sections(runner, tmp_path):
    path = _tex(tmp_path, "just text\n")
    result = runner.invoke(section_stats_group, ["show", path])
    assert result.exit_code == 0
    assert "No sections" in result.output


def test_show_lists_sections(runner, tmp_path):
    path = _tex(tmp_path, "\\section{Intro}\nhello world\n")
    result = runner.invoke(section_stats_group, ["show", path])
    assert result.exit_code == 0
    assert "Intro" in result.output


def test_summary_command(runner, tmp_path):
    path = _tex(tmp_path, "\\section{A}\nfoo bar\n")
    result = runner.invoke(section_stats_group, ["summary", path])
    assert result.exit_code == 0
    assert "section" in result.output


def test_show_missing_file(runner, tmp_path):
    result = runner.invoke(section_stats_group, ["show", str(tmp_path / "x.tex")])
    assert result.exit_code != 0
