"""Tests for pin CLI commands."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from texflow.pin_cli import pin_group
from texflow.pin import PinStore, PinnedBuild


@pytest.fixture
def runner(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return CliRunner()


def _write_pdf(tmp_path: Path, name="out.pdf") -> Path:
    p = tmp_path / name
    p.write_bytes(b"%PDF-1.4")
    return p


def test_add_pin(runner, tmp_path):
    pdf = _write_pdf(tmp_path)
    result = runner.invoke(pin_group, ["add", "v1", str(pdf)])
    assert result.exit_code == 0
    assert "Pinned 'v1'" in result.output


def test_list_no_pins(runner):
    result = runner.invoke(pin_group, ["list"])
    assert result.exit_code == 0
    assert "No pins found" in result.output


def test_list_shows_pins(runner, tmp_path):
    pdf = _write_pdf(tmp_path)
    runner.invoke(pin_group, ["add", "v1", str(pdf), "--note", "first build"])
    result = runner.invoke(pin_group, ["list"])
    assert "v1" in result.output
    assert "first build" in result.output


def test_remove_pin(runner, tmp_path):
    pdf = _write_pdf(tmp_path)
    runner.invoke(pin_group, ["add", "v1", str(pdf)])
    result = runner.invoke(pin_group, ["remove", "v1"])
    assert "Removed pin 'v1'" in result.output


def test_remove_missing(runner):
    result = runner.invoke(pin_group, ["remove", "ghost"])
    assert "No pin" in result.output


def test_show_pin(runner, tmp_path):
    pdf = _write_pdf(tmp_path)
    runner.invoke(pin_group, ["add", "v1", str(pdf), "--note", "test"])
    result = runner.invoke(pin_group, ["show", "v1"])
    assert "Label" in result.output
    assert "v1" in result.output
    assert "test" in result.output
