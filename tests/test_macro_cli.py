"""Tests for texflow.macro_cli."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from texflow.macro_cli import macro_group


@pytest.fixture()
def runner():
    return CliRunner()


def _tex(tmp_path: Path, content: str) -> str:
    p = tmp_path / "main.tex"
    p.write_text(content)
    return str(p)


def test_check_no_issues(runner, tmp_path):
    f = _tex(tmp_path, r"\newcommand{\hi}{x}" + "\n" + r"\begin{document}\hi\end{document}")
    result = runner.invoke(macro_group, ["check", f])
    assert result.exit_code == 0
    assert "No macro issues" in result.output


def test_check_unused(runner, tmp_path):
    f = _tex(tmp_path, r"\newcommand{\ghost}{x}" + "\n" + r"\begin{document}hi\end{document}")
    result = runner.invoke(macro_group, ["check", f])
    assert result.exit_code == 0
    assert "UNUSED" in result.output


def test_list_no_macros(runner, tmp_path):
    f = _tex(tmp_path, r"\begin{document}hi\end{document}")
    result = runner.invoke(macro_group, ["list", f])
    assert result.exit_code == 0
    assert "No macros" in result.output


def test_list_shows_macros(runner, tmp_path):
    f = _tex(tmp_path, r"\newcommand{\myfoo}{x}" + "\n" + r"\begin{document}\myfoo\end{document}")
    result = runner.invoke(macro_group, ["list", f])
    assert result.exit_code == 0
    assert "\\myfoo" in result.output
