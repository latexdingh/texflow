"""Tests for remote push targets."""
import json
from pathlib import Path
import pytest

from texflow.remote import RemoteTarget, PushResult, push_to_target
from texflow.remote_store import RemoteStore


# ---------------------------------------------------------------------------
# RemoteTarget
# ---------------------------------------------------------------------------

def test_to_dict_roundtrip():
    t = RemoteTarget(name="ci", kind="directory", path="/out", auto_push=True)
    assert RemoteTarget.from_dict(t.to_dict()) == t


def test_push_result_str_ok():
    r = PushResult(True, "ci", "/out/main.pdf")
    assert "OK" in str(r)


def test_push_result_str_fail():
    r = PushResult(False, "ci", "/out", message="disk full")
    assert "FAIL" in str(r) and "disk full" in str(r)


# ---------------------------------------------------------------------------
# push_to_target
# ---------------------------------------------------------------------------

def test_push_missing_pdf(tmp_path):
    target = RemoteTarget("x", "directory", str(tmp_path / "dest"))
    result = push_to_target(tmp_path / "missing.pdf", target)
    assert not result.success


def test_push_directory_copies_file(tmp_path):
    pdf = tmp_path / "main.pdf"
    pdf.write_bytes(b"%PDF")
    dest_dir = tmp_path / "dest"
    target = RemoteTarget("local", "directory", str(dest_dir))
    result = push_to_target(pdf, target)
    assert result.success
    assert (dest_dir / "main.pdf").exists()


def test_push_directory_creates_dest_if_missing(tmp_path):
    """Destination directory should be created automatically if it doesn't exist."""
    pdf = tmp_path / "main.pdf"
    pdf.write_bytes(b"%PDF")
    dest_dir = tmp_path / "nested" / "dest"
    target = RemoteTarget("local", "directory", str(dest_dir))
    result = push_to_target(pdf, target)
    assert result.success
    assert (dest_dir / "main.pdf").exists()


def test_push_unsupported_kind(tmp_path):
    pdf = tmp_path / "main.pdf"
    pdf.write_bytes(b"%PDF")
    target = RemoteTarget("ftp", "ftp", "ftp://example.com")
    result = push_to_target(pdf, target)
    assert not result.success
    assert "unsupported" in result.message


# ---------------------------------------------------------------------------
# RemoteStore
# ---------------------------------------------------------------------------

def test_add_and_get(tmp_path):
    store = RemoteStore(tmp_path / "remotes.json")
    t = RemoteTarget("prod", "directory", "/publish")
    assert store.add(t)
    assert store.get("prod") == t


def test_add_duplicate_returns_false(tmp_path):
    store = RemoteStore(tmp_path / "remotes.json")
    t = RemoteTarget("prod", "directory", "/publish")
    store.add(t)
    assert not store.add(t)


def test_remove_existing(tmp_path):
    store = RemoteStore(tmp_path / "remotes.json")
    store.add(RemoteTarget("ci", "directory", "/ci"))
    assert store.remove("ci")
    assert store.get("ci") is None


def test_remove_nonexistent_returns_false(tmp_path):
    """Removing a target that doesn't exist should return False without error."""
    store = RemoteStore(tmp_path / "remotes.json")
    assert not store.remove("ghost")


def test_persists_across_instances(tmp_path):
    p = tmp_path / "remotes.json"
    RemoteStore(p).add(RemoteTarget("a", "directory", "/a"))
    assert RemoteStore(p).get("a") is not None
