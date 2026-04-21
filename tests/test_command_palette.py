"""Tests for texflow.command_palette and texflow.command_palette_cli."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from texflow.command_palette import (
    PaletteEntry,
    PaletteResult,
    search_palette,
    _REGISTRY,
)
from texflow.command_palette_cli import palette_group


# ---------------------------------------------------------------------------
# Unit tests – search_palette
# ---------------------------------------------------------------------------

_SAMPLE = [
    PaletteEntry("check", "cite", "Check citation keys", "<file.tex>"),
    PaletteEntry("check", "spell", "Spell-check a .tex file", "<file.tex>"),
    PaletteEntry("show", "history", "Show recent build history"),
    PaletteEntry("push", "remote", "Push PDF to a remote target", "<name> <pdf>"),
]


def test_empty_query_returns_all():
    result = search_palette("", registry=_SAMPLE)
    assert result.ok
    assert len(result.entries) == len(_SAMPLE)


def test_single_token_match():
    result = search_palette("cite", registry=_SAMPLE)
    assert result.ok
    assert len(result.entries) == 1
    assert result.entries[0].name == "check"
    assert result.entries[0].group == "cite"


def test_multi_token_match():
    result = search_palette("check spell", registry=_SAMPLE)
    assert result.ok
    assert len(result.entries) == 1
    assert result.entries[0].group == "spell"


def test_case_insensitive():
    result = search_palette("HISTORY", registry=_SAMPLE)
    assert result.ok
    assert result.entries[0].group == "history"


def test_no_match_returns_empty_result():
    result = search_palette("nonexistent_xyz", registry=_SAMPLE)
    assert not result.ok
    assert result.entries == []
    assert "No matching" in result.summary()


def test_group_filter():
    result = search_palette("", registry=_SAMPLE, group_filter="remote")
    assert result.ok
    assert all(e.group == "remote" for e in result.entries)


def test_group_filter_no_match():
    result = search_palette("", registry=_SAMPLE, group_filter="template")
    assert not result.ok


def test_palette_entry_str():
    entry = PaletteEntry("push", "remote", "Push PDF", "<name> <pdf>")
    s = str(entry)
    assert "remote push" in s
    assert "Push PDF" in s


def test_palette_entry_str_no_usage():
    entry = PaletteEntry("list", "pin", "List pinned builds")
    s = str(entry)
    assert "pin list" in s


def test_registry_not_empty():
    assert len(_REGISTRY) > 5


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner():
    return CliRunner()


def test_search_no_query_lists_all(runner):
    result = runner.invoke(palette_group, ["search"])
    assert result.exit_code == 0
    assert "command(s) matched" in result.output


def test_search_with_match(runner):
    result = runner.invoke(palette_group, ["search", "cite"])
    assert result.exit_code == 0
    assert "cite" in result.output


def test_search_no_match_exits_nonzero(runner):
    result = runner.invoke(palette_group, ["search", "zzznomatch"])
    assert result.exit_code != 0
    assert "No matching" in result.output


def test_search_group_filter(runner):
    result = runner.invoke(palette_group, ["search", "--group", "remote"])
    assert result.exit_code == 0
    assert "remote" in result.output


def test_list_all(runner):
    result = runner.invoke(palette_group, ["list"])
    assert result.exit_code == 0
    assert "[" in result.output  # group headers


def test_list_group_filter(runner):
    result = runner.invoke(palette_group, ["list", "--group", "check"])
    assert result.exit_code == 0
    assert "[check]" in result.output


def test_list_unknown_group_exits_nonzero(runner):
    result = runner.invoke(palette_group, ["list", "--group", "zzznope"])
    assert result.exit_code != 0
