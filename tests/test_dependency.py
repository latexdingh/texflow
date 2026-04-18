"""Tests for texflow.dependency."""
from pathlib import Path
import pytest

from texflow.dependency import build_graph, DependencyGraph


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_single_file_no_deps(tmp_path):
    root = _write(tmp_path, "main.tex", r"\documentclass{article}\begin{document}Hello\end{document}")
    graph = build_graph(root)
    assert not graph.is_empty()
    node = list(graph.nodes.values())[0]
    assert node.depends_on == []


def test_detects_input(tmp_path):
    _write(tmp_path, "chapter.tex", "Some content.")
    root = _write(tmp_path, "main.tex", r"\input{chapter}")
    graph = build_graph(root)
    main_node = graph.nodes[str(root.resolve())]
    assert len(main_node.depends_on) == 1
    assert main_node.depends_on[0].name == "chapter.tex"


def test_detects_include(tmp_path):
    _write(tmp_path, "sec.tex", "Section content.")
    root = _write(tmp_path, "main.tex", r"\include{sec}")
    graph = build_graph(root)
    main_node = graph.nodes[str(root.resolve())]
    assert any(p.name == "sec.tex" for p in main_node.depends_on)


def test_nested_deps(tmp_path):
    _write(tmp_path, "leaf.tex", "Leaf.")
    child = _write(tmp_path, "child.tex", r"\input{leaf}")
    root = _write(tmp_path, "main.tex", r"\input{child}")
    graph = build_graph(root)
    assert str(child.resolve()) in graph.nodes
    assert str((tmp_path / "leaf.tex").resolve()) in graph.nodes


def test_no_cycle_infinite_loop(tmp_path):
    # a includes b, b includes a — should not loop
    a = _write(tmp_path, "a.tex", r"\input{b}")
    _write(tmp_path, "b.tex", r"\input{a}")
    graph = build_graph(a)  # must terminate
    assert not graph.is_empty()


def test_dependents_of(tmp_path):
    child = _write(tmp_path, "child.tex", "Content.")
    root = _write(tmp_path, "main.tex", r"\input{child}")
    graph = build_graph(root)
    deps = graph.dependents_of(child)
    assert any(p.resolve() == root.resolve() for p in deps)


def test_dependents_of_unrelated(tmp_path):
    _write(tmp_path, "other.tex", "Other.")
    root = _write(tmp_path, "main.tex", "No includes.")
    graph = build_graph(root)
    other = tmp_path / "other.tex"
    assert graph.dependents_of(other) == []


def test_summary_empty():
    graph = DependencyGraph()
    assert "No dependency" in graph.summary()


def test_summary_non_empty(tmp_path):
    root = _write(tmp_path, "main.tex", "Hello.")
    graph = build_graph(root)
    summary = graph.summary()
    assert "main.tex" in summary
