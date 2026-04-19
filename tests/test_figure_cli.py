"""Tests for texflow.figure_cli."""
from pathlib import Path
from click.testing import CliRunner
from texflow.figure_cli import figure_group


@pytest.fixture
def runner():
    return CliRunner()


def _tex(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content)
    return p


import pytest


def test_check_no_figures(tmp_path):
    runner = CliRunner()
    p = _tex(tmp_path, "Hello world")
    result = runner.invoke(figure_group, ["check", str(p)])
    assert result.exit_code == 0
    assert "No" in result.output


def test_check_missing_figure(tmp_path):
    runner = CliRunner()
    p = _tex(tmp_path, "\\includegraphics{ghost}\n")
    result = runner.invoke(figure_group, ["check", str(p), "--base-dir", str(tmp_path)])
    assert result.exit_code == 1
    assert "ghost" in result.output


def test_check_present_figure(tmp_path):
    runner = CliRunner()
    (tmp_path / "img.png").write_bytes(b"")
    p = _tex(tmp_path, "\\includegraphics{img}\n")
    result = runner.invoke(figure_group, ["check", str(p), "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "present" in result.output


def test_list_figures(tmp_path):
    runner = CliRunner()
    p = _tex(tmp_path, "\\includegraphics{fig1}\n\\includegraphics{fig2}\n")
    result = runner.invoke(figure_group, ["list", str(p)])
    assert "fig1" in result.output
    assert "fig2" in result.output


def test_list_no_figures(tmp_path):
    runner = CliRunner()
    p = _tex(tmp_path, "No graphics here.")
    result = runner.invoke(figure_group, ["list", str(p)])
    assert "No figures" in result.output
