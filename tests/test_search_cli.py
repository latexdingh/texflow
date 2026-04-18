"""Tests for texflow.search_cli."""
from pathlib import Path
from click.testing import CliRunner
from texflow.search_cli import search_group


def runner():
    return CliRunner()


def _tex(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_find_no_matches(tmp_path):
    r = CliRunner()
    f = _tex(tmp_path, "main.tex", "hello world\n")
    result = r.invoke(search_group, ["find", "missing", str(f)])
    assert result.exit_code == 0
    assert "No matches" in result.output


def test_find_with_match(tmp_path):
    r = CliRunner()
    f = _tex(tmp_path, "main.tex", "find this line\n")
    result = r.invoke(search_group, ["find", "find this", str(f), "--no-color"])
    assert result.exit_code == 0
    assert "find this line" in result.output


def test_find_missing_root(tmp_path):
    r = CliRunner()
    result = r.invoke(search_group, ["find", "hello", str(tmp_path / "nope.tex")])
    assert result.exit_code != 0


def test_find_invalid_regex(tmp_path):
    r = CliRunner()
    f = _tex(tmp_path, "main.tex", "hello\n")
    result = r.invoke(search_group, ["find", "[", str(f), "--regex"])
    assert result.exit_code != 0


def test_find_case_sensitive(tmp_path):
    r = CliRunner()
    f = _tex(tmp_path, "main.tex", "HELLO\n")
    result = r.invoke(search_group, ["find", "hello", str(f), "--case-sensitive", "--no-color"])
    assert "No matches" in result.output
