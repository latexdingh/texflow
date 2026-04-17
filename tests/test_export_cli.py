"""Tests for texflow.export_cli."""
from pathlib import Path

import pytest
from click.testing import CliRunner

from texflow.export_cli import export_group


@pytest.fixture()
def runner():
    return CliRunner()


def _pdf(tmp_path: Path, name: str = "out.pdf") -> Path:
    p = tmp_path / name
    p.write_bytes(b"%PDF fake")
    return p


def test_run_export_success(runner, tmp_path):
    src = _pdf(tmp_path)
    dest = tmp_path / "exports"
    result = runner.invoke(export_group, ["run", str(src), "--dest", str(dest)])
    assert result.exit_code == 0
    assert "Exported" in result.output


def test_run_export_missing_source(runner, tmp_path):
    result = runner.invoke(
        export_group, ["run", str(tmp_path / "ghost.pdf"), "--dest", str(tmp_path / "e")]
    )
    # click reports missing file before our code runs
    assert result.exit_code != 0


def test_list_no_exports(runner, tmp_path):
    result = runner.invoke(export_group, ["list", "--dest", str(tmp_path / "empty")])
    assert result.exit_code == 0
    assert "No exports" in result.output


def test_list_shows_exports(runner, tmp_path):
    dest = tmp_path / "exports"
    dest.mkdir()
    (dest / "thesis.pdf").write_bytes(b"pdf")
    result = runner.invoke(export_group, ["list", "--dest", str(dest)])
    assert result.exit_code == 0
    assert "thesis.pdf" in result.output
