"""Tests for PinStore and PinnedBuild."""
import pytest
from pathlib import Path
from texflow.pin import PinStore, PinnedBuild


def _make_pin(label="v1", pdf="out.pdf", note="") -> PinnedBuild:
    return PinnedBuild(label=label, pdf_path=pdf, tex_snapshot="hello", timestamp="2024-01-01T00:00:00Z", note=note)


def test_add_and_get(tmp_path):
    store = PinStore(tmp_path / "pins.json")
    pin = _make_pin("v1")
    store.add(pin)
    result = store.get("v1")
    assert result is not None
    assert result.label == "v1"
    assert result.pdf_path == "out.pdf"


def test_missing_label_returns_none(tmp_path):
    store = PinStore(tmp_path / "pins.json")
    assert store.get("nope") is None


def test_remove_existing(tmp_path):
    store = PinStore(tmp_path / "pins.json")
    store.add(_make_pin("v1"))
    assert store.remove("v1") is True
    assert store.get("v1") is None


def test_remove_missing_returns_false(tmp_path):
    store = PinStore(tmp_path / "pins.json")
    assert store.remove("ghost") is False


def test_all_returns_all(tmp_path):
    store = PinStore(tmp_path / "pins.json")
    store.add(_make_pin("v1"))
    store.add(_make_pin("v2", pdf="other.pdf"))
    assert len(store.all()) == 2


def test_persistence(tmp_path):
    pin_file = tmp_path / "pins.json"
    store = PinStore(pin_file)
    store.add(_make_pin("v1", note="first"))
    store2 = PinStore(pin_file)
    pin = store2.get("v1")
    assert pin is not None
    assert pin.note == "first"


def test_overwrite_same_label(tmp_path):
    store = PinStore(tmp_path / "pins.json")
    store.add(_make_pin("v1", pdf="old.pdf"))
    store.add(_make_pin("v1", pdf="new.pdf"))
    assert store.get("v1").pdf_path == "new.pdf"
    assert len(store.all()) == 1
