"""Tests for project_stats module."""
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

from texflow.project_stats import gather_stats, ProjectStats


def _wc(total=100, math=2):
    m = MagicMock()
    m.total_words = total
    m.math_envs = math
    return m


def _outline(n=3):
    m = MagicMock()
    m.entries = [MagicMock()] * n
    return m


def _cite(undefined=None, unused=None):
    m = MagicMock()
    m.undefined = undefined or []
    m.unused = unused or []
    return m


def _ref(undefined=None):
    m = MagicMock()
    m.undefined = undefined or []
    return m


@patch("texflow.project_stats.check_refs")
@patch("texflow.project_stats.check_citations")
@patch("texflow.project_stats.parse_outline")
@patch("texflow.project_stats.count_words")
@patch("texflow.project_stats.project_files")
def test_gather_stats_aggregates(mock_files, mock_wc, mock_outline, mock_cite, mock_ref, tmp_path):
    f1 = tmp_path / "main.tex"
    f1.write_text("hello")
    f2 = tmp_path / "chap.tex"
    f2.write_text("world")

    mock_files.return_value = [f1, f2]
    mock_wc.side_effect = [_wc(100, 2), _wc(200, 5)]
    mock_outline.side_effect = [_outline(3), _outline(1)]
    mock_cite.return_value = _cite(undefined=["missing"], unused=["extra"])
    mock_ref.return_value = _ref(undefined=["fig:x"])

    stats = gather_stats(f1)

    assert stats.total_words == 300
    assert stats.math_envs == 7
    assert stats.sections == 4
    assert stats.undefined_cites == 1
    assert stats.unused_cites == 1
    assert stats.undefined_refs == 1


@patch("texflow.project_stats.check_refs")
@patch("texflow.project_stats.check_citations")
@patch("texflow.project_stats.parse_outline")
@patch("texflow.project_stats.count_words")
@patch("texflow.project_stats.project_files")
def test_summary_contains_fields(mock_files, mock_wc, mock_outline, mock_cite, mock_ref, tmp_path):
    f = tmp_path / "main.tex"
    f.write_text("")
    mock_files.return_value = [f]
    mock_wc.return_value = _wc(50, 0)
    mock_outline.return_value = _outline(0)
    mock_cite.return_value = _cite()
    mock_ref.return_value = _ref()

    stats = gather_stats(f)
    summary = stats.summary()
    assert "Total words" in summary
    assert "50" in summary
    assert "Sections" in summary
