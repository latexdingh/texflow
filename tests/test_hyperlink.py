"""Tests for texflow.hyperlink."""
import pytest
from pathlib import Path
from texflow.hyperlink import extract_hyperlinks, HyperlinkItem


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content, encoding="utf-8")
    return p


def test_missing_file_returns_error(tmp_path: Path) -> None:
    result = extract_hyperlinks(tmp_path / "ghost.tex")
    assert not result.ok()
    assert "not found" in result.error


def test_no_links_returns_empty(tmp_path: Path) -> None:
    p = _write(tmp_path, "Hello world\n")
    result = extract_hyperlinks(p)
    assert result.ok()
    assert result.links == []
    assert "No hyperlinks" in result.summary()


def test_href_detected(tmp_path: Path) -> None:
    p = _write(tmp_path, r"See \href{https://example.com}{here}." + "\n")
    result = extract_hyperlinks(p)
    assert result.ok()
    assert any(lnk.kind == "href" and "example.com" in lnk.url for lnk in result.links)


def test_url_command_detected(tmp_path: Path) -> None:
    p = _write(tmp_path, r"Visit \url{https://latex.org}." + "\n")
    result = extract_hyperlinks(p)
    assert any(lnk.kind == "url" for lnk in result.links)


def test_hyperref_detected(tmp_path: Path) -> None:
    p = _write(tmp_path, r"See \hyperref[sec:intro]{Introduction}." + "\n")
    result = extract_hyperlinks(p)
    assert any(lnk.kind == "hyperref" and lnk.url == "sec:intro" for lnk in result.links)


def test_line_number_correct(tmp_path: Path) -> None:
    p = _write(tmp_path, "line one\n" + r"\url{https://foo.bar}" + "\n")
    result = extract_hyperlinks(p)
    assert result.links[0].line == 2


def test_comment_line_skipped(tmp_path: Path) -> None:
    p = _write(tmp_path, r"% \url{https://ignored.com}" + "\n")
    result = extract_hyperlinks(p)
    assert result.links == []


def test_summary_counts(tmp_path: Path) -> None:
    p = _write(tmp_path,
        r"\href{https://a.com}{A}" + "\n" +
        r"\url{https://b.com}" + "\n"
    )
    result = extract_hyperlinks(p)
    assert "2 hyperlink" in result.summary()


def test_str_representation() -> None:
    item = HyperlinkItem(line=5, url="https://x.com", kind="href")
    s = str(item)
    assert "5" in s and "href" in s and "https://x.com" in s
