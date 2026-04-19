"""Tests for texflow.metadata."""
from pathlib import Path
import pytest
from texflow.metadata import extract_metadata, DocumentMetadata


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content)
    return p


def test_missing_file_returns_empty():
    meta = extract_metadata(Path("/nonexistent/file.tex"))
    assert not meta.ok()
    assert meta.title is None


def test_extracts_title(tmp_path):
    p = _write(tmp_path, r"\documentclass{article}" + "\n" + r"\title{My Paper}" + "\n")
    meta = extract_metadata(p)
    assert meta.title == "My Paper"


def test_extracts_author(tmp_path):
    p = _write(tmp_path, r"\author{Jane Doe}" + "\n")
    meta = extract_metadata(p)
    assert meta.author == "Jane Doe"


def test_extracts_date(tmp_path):
    p = _write(tmp_path, r"\date{2024-01-01}" + "\n")
    meta = extract_metadata(p)
    assert meta.date == "2024-01-01"


def test_extracts_document_class(tmp_path):
    p = _write(tmp_path, r"\documentclass[12pt]{report}" + "\n")
    meta = extract_metadata(p)
    assert meta.document_class == "report"


def test_extracts_packages(tmp_path):
    content = "\n".join([
        r"\usepackage{amsmath}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage{graphicx}",
    ])
    p = _write(tmp_path, content)
    meta = extract_metadata(p)
    assert "amsmath" in meta.packages
    assert "graphicx" in meta.packages
    assert len(meta.packages) == 3


def test_ok_false_when_no_metadata(tmp_path):
    p = _write(tmp_path, r"\begin{document}Hello\end{document}")
    meta = extract_metadata(p)
    assert not meta.ok()


def test_summary_contains_title(tmp_path):
    p = _write(tmp_path, r"\title{Great Work}" + "\n" + r"\author{Bob}")
    meta = extract_metadata(p)
    s = meta.summary()
    assert "Great Work" in s
    assert "Bob" in s
