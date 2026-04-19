"""Tests for texflow.cross_ref_cli."""
from pathlib import Path
from click.testing import CliRunner
import pytest
from texflow.cross_ref_cli import cross_ref_group


@pytest.fixture
def runner():
    return CliRunner()


def _tex(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_list_no_labels(runner, tmp_path):
    f = _tex(tmp_path, "main.tex", "Hello world\n")
    result = runner.invoke(cross_ref_group, ["list", str(f)])
    assert result.exit_code == 0
    assert "No labels" in result.output


def test_list_shows_labels(runner, tmp_path):
    f = _tex(tmp_path, "main.tex", "\\label{sec:intro}\n")
    result = runner.invoke(cross_ref_group, ["list", str(f)])
    assert result.exit_code == 0
    assert "sec:intro" in result.output


def test_list_missing_root(runner, tmp_path):
    result = runner.invoke(cross_ref_group, ["list", str(tmp_path / "ghost.tex")])
    assert result.exit_code != 0


def test_find_existing_label(runner, tmp_path):
    f = _tex(tmp_path, "main.tex", "\\label{fig:plot}\n")
    result = runner.invoke(cross_ref_group, ["find", "fig:plot", str(f)])
    assert result.exit_code == 0
    assert "fig:plot" in result.output


def test_find_missing_label(runner, tmp_path):
    f = _tex(tmp_path, "main.tex", "no labels\n")
    result = runner.invoke(cross_ref_group, ["find", "nope", str(f)])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_summary_command(runner, tmp_path):
    f = _tex(tmp_path, "main.tex", "\\label{a}\n\\label{b}\n")
    result = runner.invoke(cross_ref_group, ["summary", str(f)])
    assert result.exit_code == 0
    assert "2" in result.output
