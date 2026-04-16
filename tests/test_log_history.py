"""Tests for log_history module."""
import json
import time
from pathlib import Path

import pytest

from texflow.log_history import (
    MAX_ENTRIES,
    BuildHistory,
    BuildRecord,
    load_history,
    save_history,
)


def _record(success: bool = True, errors: int = 0, warnings: int = 0) -> BuildRecord:
    return BuildRecord(
        timestamp=time.time(),
        success=success,
        errors=errors,
        warnings=warnings,
        source_file="main.tex",
        duration_ms=120.0,
    )


def test_add_record():
    h = BuildHistory()
    h.add(_record())
    assert len(h.records) == 1


def test_max_entries_trimmed():
    h = BuildHistory()
    for _ in range(MAX_ENTRIES + 10):
        h.add(_record())
    assert len(h.records) == MAX_ENTRIES


def test_last_returns_n():
    h = BuildHistory()
    for _ in range(20):
        h.add(_record())
    assert len(h.last(5)) == 5


def test_success_rate_all_ok():
    h = BuildHistory(records=[_record(True) for _ in range(4)])
    assert h.success_rate() == 1.0


def test_success_rate_mixed():
    h = BuildHistory(records=[_record(True), _record(False)])
    assert h.success_rate() == pytest.approx(0.5)


def test_success_rate_empty():
    assert BuildHistory().success_rate() == 0.0


def test_save_and_load(tmp_path):
    h = BuildHistory()
    h.add(_record(True, errors=0, warnings=2))
    save_history(tmp_path, h)
    loaded = load_history(tmp_path)
    assert len(loaded.records) == 1
    assert loaded.records[0].warnings == 2


def test_load_missing_file(tmp_path):
    h = load_history(tmp_path)
    assert h.records == []


def test_load_corrupt_file(tmp_path):
    (tmp_path / ".texflow_history.json").write_text("not json")
    h = load_history(tmp_path)
    assert h.records == []
