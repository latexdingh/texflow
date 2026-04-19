"""Check LaTeX tables for common issues."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class TableIssue:
    line: int
    message: str

    def __str__(self) -> str:
        return f"Line {self.line}: {self.message}"


@dataclass
class TableCheckResult:
    issues: List[TableIssue] = field(default_factory=list)
    table_count: int = 0

    def ok(self) -> bool:
        return len(self.issues) == 0

    def summary(self) -> str:
        if self.ok():
            return f"Tables OK ({self.table_count} found)"
        return f"{len(self.issues)} issue(s) in {self.table_count} table(s)"


def _count_cols_in_spec(spec: str) -> int:
    return len(re.findall(r'[lcrp]', spec))


def check_tables(path: Path) -> TableCheckResult:
    if not path.exists():
        return TableCheckResult()

    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    issues: List[TableIssue] = []
    table_count = 0
    in_tabular = False
    col_count = 0
    tabular_line = 0

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if re.search(r'\\begin\{tabular\}', stripped):
            in_tabular = True
            table_count += 1
            tabular_line = i
            m = re.search(r'\\begin\{tabular\}\{([^}]+)\}', stripped)
            col_count = _count_cols_in_spec(m.group(1)) if m else 0
        elif re.search(r'\\end\{tabular\}', stripped):
            in_tabular = False
            col_count = 0
        elif in_tabular and col_count > 0:
            if '\\\\' in stripped or stripped.endswith('\\\\'):
                row = re.split(r'(?<!\\)&', stripped.rstrip('\\\\').strip())
                actual = len(row)
                if actual != col_count:
                    issues.append(TableIssue(
                        line=i,
                        message=f"Row has {actual} column(s), expected {col_count} (tabular started at line {tabular_line})"
                    ))

    return TableCheckResult(issues=issues, table_count=table_count)
