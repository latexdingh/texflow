"""Tests for texflow.multi_file."""
from pathlib import Path
import pytest
from texflow.multi_file import collect_includes, find_root, project_files


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')
    return p


def test_collect_includes_single_file(tmp_path):
    root = _write(tmp_path, 'main.tex', r'\documentclass{article}\begin{document}hi\end{document}')
    files = collect_includes(root)
    assert files == [root.resolve()]


def test_collect_includes_nested(tmp_path):
    _write(tmp_path, 'chap.tex', 'chapter content')
    root = _write(tmp_path, 'main.tex', r'\documentclass{article}\input{chap}')
    files = collect_includes(root)
    assert len(files) == 2
    assert (tmp_path / 'chap.tex').resolve() in files


def test_collect_includes_missing_child(tmp_path):
    root = _write(tmp_path, 'main.tex', r'\input{ghost}')
    files = collect_includes(root)
    assert files == [root.resolve()]


def test_collect_includes_no_cycle(tmp_path):
    a = _write(tmp_path, 'a.tex', r'\input{b}')
    _write(tmp_path, 'b.tex', r'\input{a}')
    files = collect_includes(a)
    paths = [str(f) for f in files]
    assert paths.count(str(a.resolve())) == 1


def test_find_root_detects_documentclass(tmp_path):
    root = _write(tmp_path, 'main.tex', r'\documentclass{article}')
    _write(tmp_path, 'other.tex', 'no class here')
    found = find_root(tmp_path / 'other.tex')
    assert found == root.resolve()


def test_find_root_returns_candidate_when_no_class(tmp_path):
    candidate = _write(tmp_path, 'main.tex', 'nothing special')
    result = find_root(candidate)
    assert result == candidate


def test_project_files_returns_all(tmp_path):
    _write(tmp_path, 'sec.tex', 'section content')
    _write(tmp_path, 'main.tex', r'\documentclass{article}\input{sec}')
    files = project_files(tmp_path / 'main.tex')
    names = {f.name for f in files}
    assert 'main.tex' in names
    assert 'sec.tex' in names
