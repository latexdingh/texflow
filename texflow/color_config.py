"""Detect and configure color output support."""
import os
import sys


def supports_color(stream=None) -> bool:
    """Return True if the given stream supports ANSI color codes."""
    if stream is None:
        stream = sys.stdout
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if not hasattr(stream, "isatty"):
        return False
    return stream.isatty()


def color_flag(stream=None) -> bool:
    """Convenience wrapper used by CLI and BuildRunner."""
    return supports_color(stream)
