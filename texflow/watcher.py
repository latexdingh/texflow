"""File system watcher for LaTeX source files."""

import time
from pathlib import Path
from typing import Callable, Optional

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


class LatexFileHandler(FileSystemEventHandler):
    """Handles file system events for .tex files."""

    def __init__(self, callback: Callable[[Path], None], debounce_seconds: float = 0.5):
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self._last_triggered: dict[str, float] = {}

    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix != ".tex":
            return
        self._debounce_trigger(path)

    def on_created(self, event: FileSystemEvent) -> None:
        self.on_modified(event)

    def _debounce_trigger(self, path: Path) -> None:
        now = time.time()
        key = str(path.resolve())
        last = self._last_triggered.get(key, 0)
        if now - last >= self.debounce_seconds:
            self._last_triggered[key] = now
            self.callback(path)


class LatexWatcher:
    """Watches a directory for changes to .tex files."""

    def __init__(self, watch_dir: Path, callback: Callable[[Path], None], debounce_seconds: float = 0.5):
        self.watch_dir = watch_dir
        self.handler = LatexFileHandler(callback, debounce_seconds)
        self.observer: Optional[Observer] = None

    def start(self) -> None:
        self.observer = Observer()
        self.observer.schedule(self.handler, str(self.watch_dir), recursive=True)
        self.observer.start()

    def stop(self) -> None:
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None

    def __enter__(self) -> "LatexWatcher":
        self.start()
        return self

    def __exit__(self, *args) -> None:
        self.stop()
