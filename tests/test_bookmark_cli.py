"""Tests for bookmark CLI commands."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from texflow.bookmark_cli import bookmark_group


@pytest.fixture
def runner():
    return CliRunner()


def _tex(tmp_path: Path, name="main.tex", lines=30) -> Path:
    p = tmp_path / name
    p.write_text("\n".join(f"line {i}" for i in range(1, lines + 1)))
    return p


def test_add_bookmark(runner, tmp_path):
    tex = _tex(tmp_path)
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(bookmark_group, ["add", "intro", str(tex), "5"])
    assert result.exit_code == 0
    assert "intro" in result.output


def test_add_missing_file(runner, tmp_path):
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(bookmark_group, ["add", "x", "ghost.tex", "1"])
    assert result.exit_code != 0


def test_list_no_bookmarks(runner, tmp_path):
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(bookmark_group, ["list"])
    assert "No bookmarks" in result.output


def test_list_shows_bookmarks(runner, tmp_path):
    tex = _tex(tmp_path)
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(bookmark_group, ["add", "sec1", str(tex), "3"])
        result = runner.invoke(bookmark_group, ["list"])
    assert "sec1" in result.output


def test_remove_bookmark(runner, tmp_path):
    tex = _tex(tmp_path)
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(bookmark_group, ["add", "rm_me", str(tex), "1"])
        result = runner.invoke(bookmark_group, ["remove", "rm_me"])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_nonexistent(runner, tmp_path):
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(bookmark_group, ["remove", "nope"])
    assert result.exit_code != 0


def test_show_context(runner, tmp_path):
    tex = _tex(tmp_path)
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(bookmark_group, ["add", "mid", str(tex), "15"])
        result = runner.invoke(bookmark_group, ["show", "mid", "--context", "2"])
    assert ">>" in result.output
    assert "15" in result.output
