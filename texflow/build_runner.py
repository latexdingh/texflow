"""Orchestrates compile → parse → diff → report pipeline."""
from pathlib import Path
from typing import Callable, Optional

from texflow.compiler import compile_latex, find_output_pdf
from texflow.parser import parse_log, ParseResult
from texflow.diff_reporter import DiffReporter
from texflow.formatter import format_build_status, format_errors, format_diff


class BuildRunner:
    def __init__(
        self,
        source: Path,
        diff_reporter: DiffReporter,
        use_color: bool = True,
        print_fn: Callable[[str], None] = print,
    ):
        self.source = source
        self.diff_reporter = diff_reporter
        self.use_color = use_color
        self._print = print_fn

    def run(self) -> bool:
        """Run full build pipeline. Returns True on success."""
        result = compile_latex(self.source)
        success = result.returncode == 0

        self._print(format_build_status(success, str(self.source), self.use_color))

        parse_result = parse_log(result.stdout or "")
        if parse_result.errors or parse_result.warnings:
            self._print(format_errors(parse_result, self.use_color))

        pdf = find_output_pdf(self.source)
        if pdf and pdf.exists():
            diff = self.diff_reporter.report(pdf)
            if diff is not None:
                self._print(format_diff(diff, self.use_color))

        return success

    def preload(self) -> None:
        """Snapshot current PDF before first build."""
        pdf = find_output_pdf(self.source)
        if pdf and pdf.exists():
            self.diff_reporter.preload(pdf)
