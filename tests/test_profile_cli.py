"""Tests for profile CLI commands."""
import json
import os
import pytest
from click.testing import CliRunner
from texflow.profile_cli import profile_group


@pytest.fixture
def runner():
    return CliRunner()


def test_init_creates_file(runner, tmp_path):
    profile_path = str(tmp_path / ".texflow.json")
    result = runner.invoke(profile_group, ["init", "--engine", "xelatex", "--file", profile_path])
    assert result.exit_code == 0
    assert os.path.exists(profile_path)
    with open(profile_path) as f:
        data = json.load(f)
    assert data["engine"] == "xelatex"


def test_show_displays_fields(runner, tmp_path):
    profile_path = str(tmp_path / ".texflow.json")
    runner.invoke(profile_group, ["init", "--file", profile_path])
    result = runner.invoke(profile_group, ["show", "--file", profile_path])
    assert result.exit_code == 0
    assert "pdflatex" in result.output
    assert "Max runs" in result.output


def test_set_engine(runner, tmp_path):
    profile_path = str(tmp_path / ".texflow.json")
    runner.invoke(profile_group, ["init", "--file", profile_path])
    result = runner.invoke(profile_group, ["set", "engine", "lualatex", "--file", profile_path])
    assert result.exit_code == 0
    with open(profile_path) as f:
        data = json.load(f)
    assert data["engine"] == "lualatex"


def test_set_unknown_key_fails(runner, tmp_path):
    profile_path = str(tmp_path / ".texflow.json")
    runner.invoke(profile_group, ["init", "--file", profile_path])
    result = runner.invoke(profile_group, ["set", "unknown_key", "value", "--file", profile_path])
    assert result.exit_code != 0
    assert "Unknown profile key" in result.output


def test_init_default_max_runs(runner, tmp_path):
    profile_path = str(tmp_path / ".texflow.json")
    runner.invoke(profile_group, ["init", "--file", profile_path])
    with open(profile_path) as f:
        data = json.load(f)
    assert data["max_runs"] == 2
