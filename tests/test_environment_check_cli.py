"""Tests for texflow.environment_check_cli."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from texflow.environment_check_cli import env_check_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def _tex(tmp_path: Path, content: str) -> str:
    p = tmp_path / "doc.tex"
    p.write_text(content, encoding="utf-8")
    return str(p)


def test_check_clean_file_exits_zero(runner: CliRunner, tmp_path: Path) -> None:
    path = _tex(tmp_path, "\\begin{document}\nHello\n\\end{document}\n")
    result = runner.invoke(env_check_group, ["check", path])
    assert result.exit_code == 0
    assert "matched" in result.output.lower()


def test_check_unmatched_exits_nonzero(runner: CliRunner, tmp_path: Path) -> None:
    path = _tex(
        tmp_path,
        "\\begin{document}\n\\begin{itemize}\nHi\n\\end{document}\n",
    )
    result = runner.invoke(env_check_group, ["check", path])
    assert result.exit_code != 0
    assert "issue" in result.output.lower()


def test_check_mismatch_shows_detail(runner: CliRunner, tmp_path: Path) -> None:
    path = _tex(
        tmp_path,
        "\\begin{document}\n\\begin{itemize}\nHi\n\\end{enumerate}\n\\end{document}\n",
    )
    result = runner.invoke(env_check_group, ["check", path])
    assert result.exit_code != 0
    assert "mismatch" in result.output


def test_summary_clean(runner: CliRunner, tmp_path: Path) -> None:
    path = _tex(tmp_path, "\\begin{document}\nHello\n\\end{document}\n")
    result = runner.invoke(env_check_group, ["summary", path])
    assert result.exit_code == 0
    assert "matched" in result.output.lower()


def test_summary_issues(runner: CliRunner, tmp_path: Path) -> None:
    path = _tex(tmp_path, "\\begin{document}\n\\end{itemize}\n\\end{document}\n")
    result = runner.invoke(env_check_group, ["summary", path])
    assert "issue" in result.output.lower()
