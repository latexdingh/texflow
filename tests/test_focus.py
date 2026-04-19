"""Tests for texflow.focus and texflow.focus_cli."""
from pathlib import Path
import pytest
from click.testing import CliRunner
from texflow.focus import find_focus, FocusRegion
from texflow.focus_cli import focus_group

TEX = """
\\section{Introduction}
Some intro text.
More intro.

\\subsection{Background}
Background details.

\\section{Methods}
Method content.
""".strip()


def _write(tmp_path: Path, content: str = TEX) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content)
    return p


def test_missing_file_returns_error():
    result = find_focus(Path("/nonexistent/main.tex"), "Introduction")
    assert not result.ok()
    assert "not found" in result.error


def test_finds_section(tmp_path):
    p = _write(tmp_path)
    result = find_focus(p, "Introduction")
    assert result.ok()
    assert result.region is not None
    assert result.region.label == "Introduction"


def test_case_insensitive_match(tmp_path):
    p = _write(tmp_path)
    result = find_focus(p, "intro")
    assert result.ok()
    assert "Introduction" in result.region.label


def test_region_content_includes_section_line(tmp_path):
    p = _write(tmp_path)
    result = find_focus(p, "Introduction")
    assert "\\section{Introduction}" in result.region.content
    assert "Some intro text." in result.region.content


def test_region_ends_before_next_section(tmp_path):
    p = _write(tmp_path)
    result = find_focus(p, "Introduction")
    assert "Method content." not in result.region.content


def test_no_match_returns_error(tmp_path):
    p = _write(tmp_path)
    result = find_focus(p, "Conclusion")
    assert not result.ok()
    assert "Conclusion" in result.error


def test_line_count(tmp_path):
    p = _write(tmp_path)
    result = find_focus(p, "Methods")
    assert result.ok()
    assert result.region.line_count() >= 1


def test_subsection_included_in_parent_section(tmp_path):
    """Content under a subsection should appear in the enclosing section's region."""
    p = _write(tmp_path)
    result = find_focus(p, "Introduction")
    assert result.ok()
    assert "Background details." in result.region.content


# --- CLI ---

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_show(runner, tmp_path):
    p = _write(tmp_path)
    res = runner.invoke(focus_group, ["show", str(p), "Introduction", "--no-color"])
    assert res.exit_code == 0
    assert "Introduction" in res.output


def test_cli_info(runner, tmp_path):
    p = _write(tmp_path)
    res = runner.invoke(focus_group, ["info", str(p), "Methods"])
    assert res.exit_code == 0
    assert "Methods" in res.output


def test_cli_missing_label(runner, tmp_path):
    p = _write(tmp_path)
    res = runner.invoke(focus_group, ["show", str(p), "Nonexistent", "--no-color"])
    assert res.exit_code != 0
