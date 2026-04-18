import pytest
from pathlib import Path
from texflow.snippet import extract_snippets, Snippet


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content, encoding="utf-8")
    return p


def test_missing_file_returns_error(tmp_path):
    result = extract_snippets(tmp_path / "nope.tex")
    assert not result.ok
    assert result.snippets == []


def test_no_snippets_returns_empty(tmp_path):
    p = _write(tmp_path, "\\section{Hello}\nNo snippets here.\n")
    result = extract_snippets(p)
    assert result.ok
    assert result.snippets == []


def test_single_snippet(tmp_path):
    p = _write(tmp_path, "% snippet: myblock\n\\textbf{hi}\n% end-snippet\n")
    result = extract_snippets(p)
    assert result.ok
    assert len(result.snippets) == 1
    s = result.snippets[0]
    assert s.label == "myblock"
    assert "textbf" in s.content
    assert s.start_line == 2


def test_multiple_snippets(tmp_path):
    content = (
        "% snippet: a\nfoo\n% end-snippet\n"
        "middle line\n"
        "% snippet: b\nbar\nbaz\n% end-snippet\n"
    )
    p = _write(tmp_path, content)
    result = extract_snippets(p)
    assert len(result.snippets) == 2
    assert result.get("a").content.strip() == "foo"
    assert result.get("b").content.strip() == "bar\nbaz"


def test_unclosed_snippet_is_error(tmp_path):
    p = _write(tmp_path, "% snippet: broken\nsome content\n")
    result = extract_snippets(p)
    assert not result.ok
    assert "broken" in result.errors[0]


def test_get_missing_returns_none(tmp_path):
    p = _write(tmp_path, "% snippet: x\nhello\n% end-snippet\n")
    result = extract_snippets(p)
    assert result.get("z") is None


def test_snippet_str(tmp_path):
    p = _write(tmp_path, "% snippet: demo\n\\emph{test}\n% end-snippet\n")
    result = extract_snippets(p)
    s = result.snippets[0]
    out = str(s)
    assert "demo" in out
    assert "emph" in out
