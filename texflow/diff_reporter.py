"""Combines snapshot + diff to report changes on file modification."""
from __future__ import annotations

from texflow.diff import compute_diff, format_diff
from texflow.snapshot import SnapshotStore


class DiffReporter:
    """Given a SnapshotStore, compute and format diffs when files change."""

    def __init__(self, store: SnapshotStore, use_color: bool = True, context: int = 3) -> None:
        self._store = store
        self._use_color = use_color
        self._context = context

    def report(self, path: str) -> str:
        """Compute diff for path between stored snapshot and current disk content.

        Updates the snapshot after computing the diff.
        Returns a formatted diff string.
        """
        old_content = self._store.get(path) or ''
        new_content = self._store.read_and_store(path)
        diff = compute_diff(old_content, new_content, context=self._context)
        return format_diff(diff, use_color=self._use_color)

    def preload(self, directory: str) -> None:
        self._store.preload(directory)
