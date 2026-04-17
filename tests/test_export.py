"""Tests for texflow.export."""
from pathlib import Path

import pytest

from texflow.export import export_pdf, list_exports, ExportResult


def _make_pdf(tmp_path: Path, name: str = "output.pdf") -> Path:
    p = tmp_path / name
    p.write_bytes(b"%PDF-1.4 fake")
    return p


def test_export_copies_file(tmp_path):
    src = _make_pdf(tmp_path)
    dest_dir = tmp_path / "exports"
    result = export_pdf(src, dest_dir)
    assert result.success
    assert (dest_dir / "output.pdf").exists()


def test_export_custom_name(tmp_path):
    src = _make_pdf(tmp_path)
    dest_dir = tmp_path / "exports"
    result = export_pdf(src, dest_dir, name="final")
    assert result.success
    assert (dest_dir / "final.pdf").exists()


def test_export_stamp_creates_unique_file(tmp_path):
    src = _make_pdf(tmp_path)
    dest_dir = tmp_path / "exports"
    result = export_pdf(src, dest_dir, name="report", stamp=True)
    assert result.success
    files = list(dest_dir.glob("report_*.pdf"))
    assert len(files) == 1


def test_export_missing_source(tmp_path):
    result = export_pdf(tmp_path / "nope.pdf", tmp_path / "exports")
    assert not result.success
    assert "not found" in result.message


def test_list_exports_sorted(tmp_path):
    dest = tmp_path / "exports"
    dest.mkdir()
    import time
    a = dest / "a.pdf"
    a.write_bytes(b"a")
    time.sleep(0.01)
    b = dest / "b.pdf"
    b.write_bytes(b"b")
    pdfs = list_exports(dest)
    assert pdfs[0].name == "b.pdf"


def test_list_exports_empty(tmp_path):
    assert list_exports(tmp_path / "missing") == []
