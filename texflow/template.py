"""LaTeX project template scaffolding."""
from __future__ import annotations
import shutil
from pathlib import Path
from dataclasses import dataclass

TEMPLATES_DIR = Path(__file__).parent / "templates"

BUILTIN_TEMPLATES = ["article", "beamer", "report"]


@dataclass
class TemplateResult:
    success: bool
    path: Path | None = None
    error: str | None = None


def list_templates() -> list[str]:
    names = list(BUILTIN_TEMPLATES)
    if TEMPLATES_DIR.exists():
        for p in TEMPLATES_DIR.iterdir():
            if p.is_dir() and p.name not in names:
                names.append(p.name)
    return names


def scaffold(template: str, dest: Path, project_name: str) -> TemplateResult:
    src = TEMPLATES_DIR / template
    if not src.exists():
        return TemplateResult(success=False, error=f"Template '{template}' not found.")
    if dest.exists() and any(dest.iterdir()):
        return TemplateResult(success=False, error=f"Destination '{dest}' is not empty.")
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest, dirs_exist_ok=True)
    _replace_placeholder(dest, project_name)
    main_tex = dest / "main.tex"
    return TemplateResult(success=True, path=main_tex if main_tex.exists() else dest)


def _replace_placeholder(dest: Path, project_name: str) -> None:
    for tex_file in dest.rglob("*.tex"):
        text = tex_file.read_text(encoding="utf-8")
        tex_file.write_text(text.replace("{{PROJECT_NAME}}", project_name), encoding="utf-8")
