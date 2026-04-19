"""Export document metadata to JSON or plain text."""
from __future__ import annotations
import json
from pathlib import Path
from texflow.metadata import DocumentMetadata, extract_metadata


def export_metadata_json(meta: DocumentMetadata) -> str:
    data = {
        "title": meta.title,
        "author": meta.author,
        "date": meta.date,
        "document_class": meta.document_class,
        "packages": meta.packages,
    }
    return json.dumps(data, indent=2)


def export_metadata_text(meta: DocumentMetadata) -> str:
    lines = []
    if meta.title:
        lines.append(f"title: {meta.title}")
    if meta.author:
        lines.append(f"author: {meta.author}")
    if meta.date:
        lines.append(f"date: {meta.date}")
    if meta.document_class:
        lines.append(f"class: {meta.document_class}")
    for pkg in meta.packages:
        lines.append(f"package: {pkg}")
    return "\n".join(lines)


def metadata_from_file(path: Path) -> DocumentMetadata:
    return extract_metadata(path)


def metadata_summary(path: Path) -> str:
    meta = extract_metadata(path)
    if not meta.ok() and not meta.document_class and not meta.packages:
        return "No metadata found."
    parts = []
    if meta.title:
        parts.append(meta.title)
    if meta.author:
        parts.append(f"by {meta.author}")
    if meta.document_class:
        parts.append(f"[{meta.document_class}]")
    pkg_count = len(meta.packages)
    if pkg_count:
        parts.append(f"{pkg_count} package(s)")
    return " ".join(parts)
