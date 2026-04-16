"""Tests for texflow.clean and texflow.clean_cli."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from texflow.clean import find_aux_files, clean_aux_files, AUX_EXTENSIONS
from texflow.clean_cli import clean_group


def _make_files(tmp_path: Path, names: list[str]) -> list[Path]:
    paths = []
    for name in names:
        p = tmp_path / name
        p.write_text("dummy")
        paths.append(p)
    return paths


def test_find_aux_files_returns_known_extensions(tmp_path: Path) -> None:
    _make_files(tmp_path, ["main.aux", "main.log", "main.tex", "main.pdf"])
    found = find_aux_files(tmp_path)
    names = {p.name for p in found}
    assert "main.aux" in names
    assert "main.log" in names
    assert "main.tex" not in names
    assert "main.pdf" not in names


def test_find_aux_files_empty_dir(tmp_path: Path) -> None:
    assert find_aux_files(tmp_path) == []


def test_clean_aux_files_deletes(tmp_path: Path) -> None:
    _make_files(tmp_path, ["main.aux", "main.out"])
    removed = clean_aux_files(tmp_path)
    assert len(removed) == 2
    for p in removed:
        assert not p.exists()


def test_clean_aux_files_dry_run(tmp_path: Path) -> None:
    _make_files(tmp_path, ["main.aux"])
    removed = clean_aux_files(tmp_path, dry_run=True)
    assert len(removed) == 1
    assert removed[0].exists()  # file must still exist


def test_cli_run_clean(tmp_path: Path) -> None:
    _make_files(tmp_path, ["main.aux", "main.log"])
    runner = CliRunner()
    result = runner.invoke(clean_group, ["run", str(tmp_path)])
    assert result.exit_code == 0
    assert "2 file(s)" in result.output
    assert "removed" in result.output


def test_cli_dry_run(tmp_path: Path) -> None:
    _make_files(tmp_path, ["main.aux"])
    runner = CliRunner()
    result = runner.invoke(clean_group, ["run", "--dry-run", str(tmp_path)])
    assert result.exit_code == 0
    assert "listed" in result.output
    assert (tmp_path / "main.aux").exists()


def test_cli_list(tmp_path: Path) -> None:
    _make_files(tmp_path, ["main.toc"])
    runner = CliRunner()
    result = runner.invoke(clean_group, ["list", str(tmp_path)])
    assert result.exit_code == 0
    assert "main.toc" in result.output


def test_cli_no_files(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(clean_group, ["run", str(tmp_path)])
    assert result.exit_code == 0
    assert "No auxiliary files found" in result.output
