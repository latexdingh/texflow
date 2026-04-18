"""Tests for texflow.rename and rename_cli."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from texflow.rename import rename_tex_file, _stem
from texflow.rename_cli import rename_group


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_stem_strips_tex():
    assert _stem("main.tex") == "main"
    assert _stem("main") == "main"


def test_rename_simple(tmp_path):
    src = _write(tmp_path, "old.tex", "Hello")
    result = rename_tex_file(src, "new", tmp_path)
    assert result.ok
    assert result.new_path.name == "new.tex"
    assert result.new_path.exists()
    assert not src.exists()


def test_rename_updates_references(tmp_path):
    _write(tmp_path, "old.tex", "Content")
    ref = _write(tmp_path, "main.tex", r"\input{old}")
    result = rename_tex_file(tmp_path / "old.tex", "new", tmp_path)
    assert result.ok
    assert ref in result.updated_files
    assert "\\input{new}" in ref.read_text()


def test_rename_updates_include_with_extension(tmp_path):
    _write(tmp_path, "chapter.tex", "Content")
    ref = _write(tmp_path, "main.tex", r"\include{chapter.tex}")
    rename_tex_file(tmp_path / "chapter.tex", "intro", tmp_path)
    assert "\\include{intro}" in ref.read_text()


def test_rename_missing_file(tmp_path):
    result = rename_tex_file(tmp_path / "ghost.tex", "new", tmp_path)
    assert not result.ok
    assert "not found" in result.error


def test_rename_non_tex_file(tmp_path):
    src = _write(tmp_path, "notes.md", "# Notes")
    result = rename_tex_file(src, "other", tmp_path)
    assert not result.ok
    assert "Only .tex" in result.error


def test_rename_destination_exists(tmp_path):
    _write(tmp_path, "a.tex", "A")
    _write(tmp_path, "b.tex", "B")
    result = rename_tex_file(tmp_path / "a.tex", "b", tmp_path)
    assert not result.ok
    assert "already exists" in result.error


def test_cli_rename(tmp_path):
    src = _write(tmp_path, "old.tex", "Hello")
    runner = CliRunner()
    result = runner.invoke(rename_group, ["file", str(src), "new"])
    assert result.exit_code == 0
    assert "new.tex" in result.output


def test_cli_dry_run(tmp_path):
    src = _write(tmp_path, "old.tex", "Hello")
    runner = CliRunner()
    result = runner.invoke(rename_group, ["file", str(src), "new", "--dry-run"])
    assert result.exit_code == 0
    assert "dry-run" in result.output
    assert src.exists()  # not actually renamed
