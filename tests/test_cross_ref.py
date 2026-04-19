"""Tests for texflow.cross_ref."""
from pathlib import Path
import pytest
from texflow.cross_ref import build_cross_ref_map, CrossRefEntry, CrossRefMap


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_missing_file_returns_empty(tmp_path):
    xmap = build_cross_ref_map([tmp_path / "ghost.tex"])
    assert not xmap.ok()
    assert xmap.entries == []


def test_single_label(tmp_path):
    f = _write(tmp_path, "a.tex", "Some text \\label{sec:intro} here\n")
    xmap = build_cross_ref_map([f])
    assert xmap.ok()
    assert len(xmap.entries) == 1
    e = xmap.entries[0]
    assert e.label == "sec:intro"
    assert e.line == 1


def test_multiple_labels_same_file(tmp_path):
    content = "\\label{fig:one}\n\\label{fig:two}\n"
    f = _write(tmp_path, "b.tex", content)
    xmap = build_cross_ref_map([f])
    assert len(xmap.entries) == 2
    labels = {e.label for e in xmap.entries}
    assert labels == {"fig:one", "fig:two"}


def test_labels_across_files(tmp_path):
    f1 = _write(tmp_path, "c1.tex", "\\label{ch:one}\n")
    f2 = _write(tmp_path, "c2.tex", "\\label{ch:two}\n")
    xmap = build_cross_ref_map([f1, f2])
    assert len(xmap.entries) == 2


def test_get_existing_label(tmp_path):
    f = _write(tmp_path, "d.tex", "\\label{eq:main}\n")
    xmap = build_cross_ref_map([f])
    entry = xmap.get("eq:main")
    assert entry is not None
    assert entry.label == "eq:main"


def test_get_missing_label(tmp_path):
    f = _write(tmp_path, "e.tex", "no labels here\n")
    xmap = build_cross_ref_map([f])
    assert xmap.get("nope") is None


def test_summary_string(tmp_path):
    f = _write(tmp_path, "f.tex", "\\label{x}\n\\label{y}\n")
    xmap = build_cross_ref_map([f])
    assert "2" in xmap.summary()


def test_as_dict(tmp_path):
    f = _write(tmp_path, "g.tex", "\\label{tab:results}\n")
    xmap = build_cross_ref_map([f])
    d = xmap.as_dict()
    assert "tab:results" in d
    assert isinstance(d["tab:results"], CrossRefEntry)


def test_str_representation(tmp_path):
    f = _write(tmp_path, "h.tex", "\\label{sec:bg} Background section\n")
    xmap = build_cross_ref_map([f])
    s = str(xmap.entries[0])
    assert "sec:bg" in s
