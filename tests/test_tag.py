"""Tests for texflow.tag."""
import pytest
from pathlib import Path
from texflow.tag import BuildTag, TagStore


def _store(tmp_path: Path) -> TagStore:
    return TagStore(store_path=tmp_path / "tags.json")


def test_add_and_get(tmp_path):
    s = _store(tmp_path)
    tag = BuildTag(label="v1", source="main.tex", note="first release")
    s.add(tag)
    result = s.get("v1")
    assert result is not None
    assert result.label == "v1"
    assert result.source == "main.tex"
    assert result.note == "first release"


def test_missing_label_returns_none(tmp_path):
    s = _store(tmp_path)
    assert s.get("ghost") is None


def test_remove_existing(tmp_path):
    s = _store(tmp_path)
    s.add(BuildTag(label="draft", source="main.tex"))
    assert s.remove("draft") is True
    assert s.get("draft") is None


def test_remove_missing_returns_false(tmp_path):
    s = _store(tmp_path)
    assert s.remove("nope") is False


def test_all_returns_list(tmp_path):
    s = _store(tmp_path)
    s.add(BuildTag(label="a", source="a.tex"))
    s.add(BuildTag(label="b", source="b.tex"))
    labels = [t.label for t in s.all()]
    assert set(labels) == {"a", "b"}


def test_persistence(tmp_path):
    p = tmp_path / "tags.json"
    s1 = TagStore(store_path=p)
    s1.add(BuildTag(label="saved", source="doc.tex"))
    s2 = TagStore(store_path=p)
    assert s2.get("saved") is not None


def test_str_with_note():
    tag = BuildTag(label="rc1", source="main.tex", created_at="2024-01-01T00:00:00", note="candidate")
    assert "rc1" in str(tag)
    assert "candidate" in str(tag)


def test_str_without_note():
    tag = BuildTag(label="rc2", source="main.tex", created_at="2024-01-01T00:00:00")
    assert "#" not in str(tag)


def test_to_dict_roundtrip():
    tag = BuildTag(label="x", source="x.tex", note="hi")
    restored = BuildTag.from_dict(tag.to_dict())
    assert restored.label == tag.label
    assert restored.note == tag.note
