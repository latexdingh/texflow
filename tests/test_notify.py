"""Tests for texflow.notify."""
from unittest.mock import patch, MagicMock
import pytest
from texflow.notify import NotifyConfig, send_notification, notify_build


def _cfg(**kw) -> NotifyConfig:
    return NotifyConfig(**kw)


def test_send_disabled_returns_false():
    cfg = _cfg(enabled=False)
    result = send_notification("title", "body", cfg)
    assert result is False


def test_no_notifier_returns_false():
    cfg = _cfg(enabled=True)
    with patch("texflow.notify._notifier", return_value=None):
        result = send_notification("title", "body", cfg)
    assert result is False


def test_send_linux_success():
    cfg = _cfg(enabled=True)
    with patch("texflow.notify._notifier", return_value="notify-send"), \
         patch("texflow.notify._send_linux", return_value=True) as mock:
        result = send_notification("t", "b", cfg)
    assert result is True
    mock.assert_called_once_with("t", "b", cfg.sound)


def test_send_macos_success():
    cfg = _cfg(enabled=True)
    with patch("texflow.notify._notifier", return_value="osascript"), \
         patch("texflow.notify._send_macos", return_value=True) as mock:
        result = send_notification("t", "b", cfg)
    assert result is True
    mock.assert_called_once_with("t", "b", cfg.sound)


def test_notify_build_success_suppressed():
    cfg = _cfg(enabled=True, on_success=False)
    result = notify_build(success=True, source="main.tex", config=cfg)
    assert result is False


def test_notify_build_failure_suppressed():
    cfg = _cfg(enabled=True, on_failure=False)
    result = notify_build(success=False, source="main.tex", config=cfg)
    assert result is False


def test_notify_build_success_sends():
    cfg = _cfg(enabled=True, on_success=True)
    with patch("texflow.notify.send_notification", return_value=True) as mock:
        result = notify_build(success=True, source="main.tex", config=cfg)
    assert result is True
    args = mock.call_args[0]
    assert "succeeded" in args[0]
    assert "main.tex" in args[1]


def test_notify_build_failure_sends():
    cfg = _cfg(enabled=True, on_failure=True)
    with patch("texflow.notify.send_notification", return_value=True) as mock:
        result = notify_build(success=False, source="main.tex", config=cfg)
    assert result is True
    args = mock.call_args[0]
    assert "failed" in args[0]
