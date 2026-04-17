"""Desktop notification support for build results."""
from __future__ import annotations
import shutil
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class NotifyConfig:
    enabled: bool = True
    on_success: bool = True
    on_failure: bool = True
    sound: bool = False


def _notifier() -> Optional[str]:
    for cmd in ("notify-send", "osascript", "terminal-notifier"):
        if shutil.which(cmd):
            return cmd
    return None


def _send_linux(title: str, body: str, sound: bool) -> bool:
    cmd = ["notify-send", title, body, "--app-name=texflow"]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def _send_macos(title: str, body: str, sound: bool) -> bool:
    sound_part = "with sound" if sound else ""
    script = (
        f'display notification "{body}" with title "{title}" '
        f'subtitle "texflow" {sound_part}'
    )
    try:
        subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def send_notification(title: str, body: str, config: NotifyConfig) -> bool:
    """Send a desktop notification. Returns True if sent successfully."""
    if not config.enabled:
        return False
    notifier = _notifier()
    if notifier is None:
        return False
    if notifier == "notify-send":
        return _send_linux(title, body, config.sound)
    if notifier in ("osascript", "terminal-notifier"):
        return _send_macos(title, body, config.sound)
    return False


def notify_build(success: bool, source: str, config: NotifyConfig) -> bool:
    """Notify about a build result."""
    if success not config.on_success:
        return False
    if not success and not config.on_failure:
        return False
    title = "✅ Build succeeded" if success else "❌ Build failed"
    body = f"{source}"
    return send_notification(title, body, config)
