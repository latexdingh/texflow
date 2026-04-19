"""Tests for texflow.metadata_cli."""
from pathlib import Path
from click.testing import CliRunner
import pytest
from texflow.metadata_cli import metadata_group


@pytest.fixture
def runner():
    return CliRunner()


def _tex(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content)
    return p


def test_show_no_metadata(runner, tmp_path):
    p = _tex(tmp_path, r"\begin{document}hi\end{document}")
    result = runner.invoke(metadata_group, ["show", str(p)])
    assert result.exit_code == 0
    assert "No metadata" in result.output


def test_show_displays_title(runner, tmp_path):
    p = _tex(tmp_path, r"\title{Hello World}" + "\n" + r"\author{Alice}")
    result = runner.invoke(metadata_group, ["show", str(p)])
    assert result.exit_code == 0
    assert "Hello World" in result.output
    assert "Alice" in result.output


def test_title_command(runner, tmp_path):
    p = _tex(tmp_path, r"\title{My Thesis}")
    result = runner.invoke(metadata_group, ["title", str(p)])
    assert result.exit_code == 0
    assert "My Thesis" in result.output


def test_title_missing_exits_nonzero(runner, tmp_path):
    p = _tex(tmp_path, r"\begin{document}\end{document}")
    result = runner.invoke(metadata_group, ["title", str(p)])
    assert result.exit_code != 0


def test_packages_list(runner, tmp_path):
    p = _tex(tmp_path, r"\usepackage{amsmath}" + "\n" + r"\usepackage{graphicx}")
    result = runner.invoke(metadata_group, ["packages", str(p)])
    assert result.exit_code == 0
    assert "amsmath" in result.output
    assert "graphicx" in result.output


def test_packages_count(runner, tmp_path):
    p = _tex(tmp_path, r"\usepackage{a}" + "\n" + r"\usepackage{b}" + "\n" + r"\usepackage{c}")
    result = runner.invoke(metadata_group, ["packages", "--count", str(p)])
    assert result.exit_code == 0
    assert "3" in result.output
