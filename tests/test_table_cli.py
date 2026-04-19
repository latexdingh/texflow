"""Tests for texflow.table_cli."""
from pathlib import Path
from click.testing import CliRunner
from texflow.table_cli import table_group
import pytest


@pytest.fixture()
def runner():
    return CliRunner()


def _tex(tmp_path: Path, content: str) -> str:
    p = tmp_path / "doc.tex"
    p.write_text(content)
    return str(p)


def test_check_no_tables(runner, tmp_path):
    f = _tex(tmp_path, "No tables here.\n")
    result = runner.invoke(table_group, ["check", f])
    assert result.exit_code == 0
    assert "No issues" in result.output


def test_check_valid_table(runner, tmp_path):
    content = "\\begin{tabular}{ll}\nA & B \\\\\n\\end{tabular}\n"
    f = _tex(tmp_path, content)
    result = runner.invoke(table_group, ["check", f])
    assert result.exit_code == 0


def test_check_bad_table_exits_nonzero(runner, tmp_path):
    content = "\\begin{tabular}{l}\nA & B \\\\\n\\end{tabular}\n"
    f = _tex(tmp_path, content)
    result = runner.invoke(table_group, ["check", f])
    assert result.exit_code != 0
    assert "Line" in result.output


def test_summary_ok(runner, tmp_path):
    f = _tex(tmp_path, "\\begin{tabular}{l}\nA \\\\\n\\end{tabular}\n")
    result = runner.invoke(table_group, ["summary", f])
    assert result.exit_code == 0
    assert "OK" in result.output
