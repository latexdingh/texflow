"""Tests for texflow.custom_command and related CLI."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from texflow.custom_command import CommandStore, CustomCommand, RunResult, run_command
from texflow.custom_command_cli import command_group


# ---------------------------------------------------------------------------
# Unit tests – CustomCommand & CommandStore
# ---------------------------------------------------------------------------

def _store(tmp_path: Path) -> CommandStore:
    return CommandStore(tmp_path / "cmds.json")


def test_add_and_get(tmp_path):
    s = _store(tmp_path)
    s.add(CustomCommand(label="hello", command="echo hi", description="greet"))
    cmd = s.get("hello")
    assert cmd is not None
    assert cmd.command == "echo hi"
    assert cmd.description == "greet"


def test_missing_label_returns_none(tmp_path):
    s = _store(tmp_path)
    assert s.get("nope") is None


def test_add_overwrites_existing(tmp_path):
    s = _store(tmp_path)
    s.add(CustomCommand(label="x", command="echo old"))
    s.add(CustomCommand(label="x", command="echo new"))
    assert s.get("x").command == "echo new"
    assert len(s.all()) == 1


def test_remove_existing(tmp_path):
    s = _store(tmp_path)
    s.add(CustomCommand(label="bye", command="true"))
    assert s.remove("bye") is True
    assert s.get("bye") is None


def test_remove_missing_returns_false(tmp_path):
    s = _store(tmp_path)
    assert s.remove("ghost") is False


def test_persists_to_disk(tmp_path):
    p = tmp_path / "cmds.json"
    s = CommandStore(p)
    s.add(CustomCommand(label="build", command="make"))
    s2 = CommandStore(p)
    assert s2.get("build") is not None


def test_str_representation():
    c = CustomCommand(label="lint", command="chktex main.tex", description="run linter")
    assert "lint" in str(c)
    assert "chktex" in str(c)
    assert "run linter" in str(c)


def test_run_command_success(tmp_path):
    cmd = CustomCommand(label="hi", command="echo hello")
    result = run_command(cmd, cwd=tmp_path)
    assert result.ok
    assert "hello" in result.stdout


def test_run_command_failure(tmp_path):
    cmd = CustomCommand(label="fail", command="exit 42", description="")
    result = run_command(cmd, cwd=tmp_path)
    assert not result.ok
    assert result.returncode == 42


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture
def runner():
    return CliRunner()


def test_add_and_list(runner, tmp_path):
    store = str(tmp_path / "c.json")
    runner.invoke(command_group, ["add", "greet", "echo hi", "--store", store])
    result = runner.invoke(command_group, ["list", "--store", store])
    assert "greet" in result.output


def test_list_empty(runner, tmp_path):
    store = str(tmp_path / "c.json")
    result = runner.invoke(command_group, ["list", "--store", store])
    assert "No custom commands" in result.output


def test_remove_command(runner, tmp_path):
    store = str(tmp_path / "c.json")
    runner.invoke(command_group, ["add", "tmp", "true", "--store", store])
    result = runner.invoke(command_group, ["remove", "tmp", "--store", store])
    assert "Removed" in result.output


def test_remove_unknown_exits_nonzero(runner, tmp_path):
    store = str(tmp_path / "c.json")
    result = runner.invoke(command_group, ["remove", "ghost", "--store", store])
    assert result.exit_code != 0


def test_run_known_command(runner, tmp_path):
    store = str(tmp_path / "c.json")
    runner.invoke(command_group, ["add", "hi", "echo world", "--store", store])
    result = runner.invoke(command_group, ["run", "hi", "--store", store])
    assert "world" in result.output
    assert result.exit_code == 0


def test_run_unknown_command_exits_nonzero(runner, tmp_path):
    store = str(tmp_path / "c.json")
    result = runner.invoke(command_group, ["run", "nope", "--store", store])
    assert result.exit_code != 0
