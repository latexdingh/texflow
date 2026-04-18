"""Tests for BookmarkStore and Bookmark."""
import pytest
from pathlib import Path
from texflow.bookmark import Bookmark, BookmarkStore


def _store(tmp_path: Path) -> BookmarkStore:
    return BookmarkStore(path=tmp_path / "bookmarks.json")


def test_add_and_get(tmp_path):
    store = _store(tmp_path)
    bm = Bookmark(label="intro", file="main.tex", line=10, note="start")
    store.add(bm)
    result = store.get("intro")
    assert result is not None
    assert result.line == 10
    assert result.note == "start"


def test_missing_label_returns_none(tmp_path):
    store = _store(tmp_path)
    assert store.get("nope") is None


def test_remove_existing(tmp_path):
    store = _store(tmp_path)
    store.add(Bookmark("x", "a.tex", 5))
    assert store.remove("x") is True
    assert store.get("x") is None


def test_remove_missing_returns_false(tmp_path):
    store = _store(tmp_path)
    assert store.remove("ghost") is False


def test_all_returns_list(tmp_path):
    store = _store(tmp_path)
    store.add(Bookmark("a", "f.tex", 1))
    store.add(Bookmark("b", "f.tex", 2))
    assert len(store.all()) == 2


def test_persistence(tmp_path):
    p = tmp_path / "bm.json"
    s1 = BookmarkStore(path=p)
    s1.add(Bookmark("persist", "main.tex", 42))
    s2 = BookmarkStore(path=p)
    assert s2.get("persist").line == 42


def test_overwrite_label(tmp_path):
    store = _store(tmp_path)
    store.add(Bookmark("dup", "a.tex", 1))
    store.add(Bookmark("dup", "a.tex", 99))
    assert store.get("dup").line == 99
    assert len(store.all()) == 1


def test_str_with_note():
    bm = Bookmark("sec", "main.tex", 20, note="intro section")
    assert "intro section" in str(bm)
    assert "main.tex:20" in str(bm)


def test_str_without_note():
    bm = Bookmark("sec", "main.tex", 5)
    assert str(bm) == "[sec] main.tex:5"
