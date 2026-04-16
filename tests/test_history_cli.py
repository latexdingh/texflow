"""Tests for history CLI commands."""
import time
from pathlib import Path

from click.testing import CliRunner

from texflow.history_cli import history_group
from texflow.log_history import BuildHistory, BuildRecord, save_history


def _record(success: bool = True) -> BuildRecord:
    return BuildRecord(
        timestamp=time.time(),
        success=success,
        errors=0 if success else 2,
        warnings=1,
        source_file="main.tex",
        duration_ms=200.0,
    )


def test_show_no_history(tmp_path):
    runner = CliRunner()
    result = runner.invoke(history_group, ["show", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No build history" in result.output


def test_show_lists_records(tmp_path):
    h = BuildHistory(records=[_record(True), _record(False)])
    save_history(tmp_path, h)
    runner = CliRunner()
    result = runner.invoke(history_group, ["show", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "OK" in result.output
    assert "FAIL" in result.output


def test_stats_no_history(tmp_path):
    runner = CliRunner()
    result = runner.invoke(history_group, ["stats", "--dir", str(tmp_path)])
    assert "No build history" in result.output


def test_stats_shows_rate(tmp_path):
    h = BuildHistory(records=[_record(True), _record(True), _record(False)])
    save_history(tmp_path, h)
    runner = CliRunner()
    result = runner.invoke(history_group, ["stats", "--dir", str(tmp_path)])
    assert "66.7%" in result.output
    assert "Total builds" in result.output
