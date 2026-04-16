"""Tests for the LaTeX file watcher module."""

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from texflow.watcher import LatexFileHandler, LatexWatcher


class FakeEvent:
    def __init__(self, src_path: str, is_directory: bool = False):
        self.src_path = src_path
        self.is_directory = is_directory


class TestLatexFileHandler:
    def test_ignores_directory_events(self):
        cb = MagicMock()
        handler = LatexFileHandler(cb)
        handler.on_modified(FakeEvent("/some/dir", is_directory=True))
        cb.assert_not_called()

    def test_ignores_non_tex_files(self):
        cb = MagicMock()
        handler = LatexFileHandler(cb)
        handler.on_modified(FakeEvent("/some/file.pdf"))
        cb.assert_not_called()

    def test_triggers_on_tex_file(self, tmp_path):
        tex_file = tmp_path / "main.tex"
        tex_file.touch()
        cb = MagicMock()
        handler = LatexFileHandler(cb, debounce_seconds=0)
        handler.on_modified(FakeEvent(str(tex_file)))
        cb.assert_called_once_with(tex_file.resolve())

    def test_debounce_suppresses_rapid_calls(self, tmp_path):
        tex_file = tmp_path / "main.tex"
        tex_file.touch()
        cb = MagicMock()
        handler = LatexFileHandler(cb, debounce_seconds=1.0)
        handler.on_modified(FakeEvent(str(tex_file)))
        handler.on_modified(FakeEvent(str(tex_file)))
        assert cb.call_count == 1

    def test_on_created_triggers_callback(self, tmp_path):
        tex_file = tmp_path / "new.tex"
        tex_file.touch()
        cb = MagicMock()
        handler = LatexFileHandler(cb, debounce_seconds=0)
        handler.on_created(FakeEvent(str(tex_file)))
        cb.assert_called_once()


class TestLatexWatcher:
    def test_context_manager_starts_and_stops(self, tmp_path):
        cb = MagicMock()
        watcher = LatexWatcher(tmp_path, cb)
        with patch("texflow.watcher.Observer") as MockObserver:
            mock_obs = MockObserver.return_value
            with watcher:
                mock_obs.start.assert_called_once()
            mock_obs.stop.assert_called_once()
            mock_obs.join.assert_called_once()
