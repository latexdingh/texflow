"""Tests for SnapshotStore and DiffReporter."""
import os
import tempfile
import pytest

from texflow.snapshot import SnapshotStore
from texflow.diff_reporter import DiffReporter


def write(path, content):
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(content)


def test_snapshot_read_and_store():
    with tempfile.NamedTemporaryFile('w', suffix='.tex', delete=False) as f:
        f.write('hello world')
        name = f.name
    try:
        store = SnapshotStore()
        content = store.read_and_store(name)
        assert content == 'hello world'
        assert store.get(name) == 'hello world'
    finally:
        os.unlink(name)


def test_snapshot_missing_file_returns_empty():
    store = SnapshotStore()
    content = store.read_and_store('/nonexistent/file.tex')
    assert content == ''


def test_snapshot_preload():
    with tempfile.TemporaryDirectory() as tmpdir:
        write(os.path.join(tmpdir, 'a.tex'), 'aaa')
        write(os.path.join(tmpdir, 'b.tex'), 'bbb')
        write(os.path.join(tmpdir, 'c.txt'), 'ccc')
        store = SnapshotStore()
        store.preload(tmpdir)
        assert store.get(os.path.join(tmpdir, 'a.tex')) == 'aaa'
        assert store.get(os.path.join(tmpdir, 'b.tex')) == 'bbb'
        assert store.get(os.path.join(tmpdir, 'c.txt')) is None


def test_diff_reporter_detects_change():
    with tempfile.NamedTemporaryFile('w', suffix='.tex', delete=False) as f:
        f.write('original content\n')
        name = f.name
    try:
        store = SnapshotStore()
        store.read_and_store(name)
        write(name, 'modified content\n')
        reporter = DiffReporter(store, use_color=False)
        report = reporter.report(name)
        assert '+' in report or '-' in report
    finally:
        os.unlink(name)


def test_diff_reporter_no_change():
    with tempfile.NamedTemporaryFile('w', suffix='.tex', delete=False) as f:
        f.write('same\n')
        name = f.name
    try:
        store = SnapshotStore()
        store.read_and_store(name)
        reporter = DiffReporter(store, use_color=False)
        report = reporter.report(name)
        assert report == '(no changes)'
    finally:
        os.unlink(name)
