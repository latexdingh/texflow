"""Tests for texflow.todo."""
from pathlib import Path
import pytest
from texflow.todo import scan_todos, scan_todos_multi, TodoResult


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_missing_file_returns_empty(tmp_path: Path) -> None:
    result = scan_todos(tmp_path / "ghost.tex")
    assert result.ok
    assert result.items == []


def test_no_todos_returns_ok(tmp_path: Path) -> None:
    f = _write(tmp_path, "clean.tex", "\\section{Intro}\nHello world.\n")
    result = scan_todos(f)
    assert result.ok


def test_detects_todo(tmp_path: Path) -> None:
    f = _write(tmp_path, "a.tex", "Some text\n% TODO: finish this\nMore text\n")
    result = scan_todos(f)
    assert not result.ok
    assert len(result.items) == 1
    assert result.items[0].kind == "TODO"
    assert result.items[0].line == 2
    assert "finish this" in result.items[0].message


def test_detects_fixme(tmp_path: Path) -> None:
    f = _write(tmp_path, "b.tex", "% FIXME: broken\n")
    result = scan_todos(f)
    assert result.items[0].kind == "FIXME"


def test_case_insensitive(tmp_path: Path) -> None:
    f = _write(tmp_path, "c.tex", "% todo: lowercase\n")
    result = scan_todos(f)
    assert result.items[0].kind == "TODO"


def test_by_kind_filters(tmp_path: Path) -> None:
    f = _write(tmp_path, "d.tex", "% TODO: one\n% FIXME: two\n% NOTE: three\n")
    result = scan_todos(f)
    assert len(result.by_kind("TODO")) == 1
    assert len(result.by_kind("FIXME")) == 1
    assert len(result.by_kind("NOTE")) == 1
    assert len(result.by_kind("HACK")) == 0


def test_summary_counts(tmp_path: Path) -> None:
    f = _write(tmp_path, "e.tex", "% TODO: a\n% TODO: b\n% FIXME: c\n")
    result = scan_todos(f)
    s = result.summary()
    assert "3 item" in s
    assert "FIXME" in s
    assert "TODO" in s


def test_scan_multi(tmp_path: Path) -> None:
    f1 = _write(tmp_path, "f1.tex", "% TODO: first\n")
    f2 = _write(tmp_path, "f2.tex", "% FIXME: second\n")
    result = scan_todos_multi([f1, f2])
    assert len(result.items) == 2


def test_str_representation(tmp_path: Path) -> None:
    f = _write(tmp_path, "g.tex", "% TODO: check this\n")
    result = scan_todos(f)
    s = str(result.items[0])
    assert "TODO" in s
    assert "check this" in s
