"""Tests for texflow.hyperlink_cli."""
import pytest
from pathlib import Path
from click.testing import CliRunner
from texflow.hyperlink_cli import hyperlink_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def _tex(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content, encoding="utf-8")
    return p


def test_list_no_links(runner: CliRunner, tmp_path: Path) -> None:
    p = _tex(tmp_path, "No links here.\n")
    result = runner.invoke(hyperlink_group, ["list", str(p)])
    assert result.exit_code == 0
    assert "No hyperlinks" in result.output


def test_list_shows_links(runner: CliRunner, tmp_path: Path) -> None:
    p = _tex(tmp_path, r"\href{https://example.com}{Ex}" + "\n")
    result = runner.invoke(hyperlink_group, ["list", str(p)])
    assert result.exit_code == 0
    assert "example.com" in result.output


def test_list_missing_file(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(hyperlink_group, ["list", str(tmp_path / "ghost.tex")])
    assert result.exit_code != 0


def test_summary_command(runner: CliRunner, tmp_path: Path) -> None:
    p = _tex(tmp_path,
        r"\url{https://a.com}" + "\n" +
        r"\href{https://b.com}{B}" + "\n"
    )
    result = runner.invoke(hyperlink_group, ["summary", str(p)])
    assert result.exit_code == 0
    assert "2 hyperlink" in result.output


def test_summary_missing_file(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(hyperlink_group, ["summary", str(tmp_path / "no.tex")])
    assert result.exit_code != 0
