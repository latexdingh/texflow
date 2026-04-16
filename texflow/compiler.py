"""LaTeX compilation helpers."""
from __future__ import annotations
import os
import subprocess
from dataclasses import dataclass
from typing import Optional
from texflow.profile import BuildProfile, load_profile


@dataclass
class CompileResult:
    success: bool
    stdout: str
    stderr: str
    returncode: int


def compile_latex(
    tex_file: str,
    profile: Optional[BuildProfile] = None,
) -> CompileResult:
    if profile is None:
        profile = load_profile()

    output_dir = profile.output_dir
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        profile.engine,
        "-interaction=nonstopmode",
        f"-output-directory={output_dir}",
        *profile.extra_args,
        tex_file,
    ]

    for _ in range(max(1, profile.max_runs)):
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

    return CompileResult(
        success=result.returncode == 0,
        stdout=result.stdout,
        stderr=result.stderr,
        returncode=result.returncode,
    )


def find_output_pdf(tex_file: str, profile: Optional[BuildProfile] = None) -> Optional[str]:
    if profile is None:
        profile = load_profile()
    base = os.path.splitext(os.path.basename(tex_file))[0]
    candidate = os.path.join(profile.output_dir, base + ".pdf")
    return candidate if os.path.exists(candidate) else None
