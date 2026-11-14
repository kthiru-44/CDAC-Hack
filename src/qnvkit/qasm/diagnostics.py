"""
qnvkit.qasm.diagnostics: Pinpoint diagnostic reporting with source locations and line:column formatting.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SourceLocation:
    line: int
    col: int
    file: Optional[str] = None

    def __repr__(self) -> str:
        loc = f"{self.line}:{self.col}"
        return f"{self.file}:{loc}" if self.file else loc


@dataclass(frozen=True)
class Diagnostic:
    message: str
    location: Optional[SourceLocation] = None
    severity: str = "ERROR"  # "ERROR", "WARNING", "NOTE"
    source_line: Optional[str] = None

    def format_diagnostic(self) -> str:
        prefix = f"[{self.severity}]"
        if self.location:
            loc_str = f" at line {self.location.line}, col {self.location.col}"
        else:
            loc_str = ""

        lines = [f"{prefix}{loc_str}: {self.message}"]
        if self.source_line and self.location:
            lines.append(f"  | {self.source_line}")
            indent = " " * (self.location.col - 1)
            lines.append(f"  | {indent}^")

        return "\n".join(lines)

    def to_dict(self):
        return {
            "message": self.message,
            "severity": self.severity,
            "line": self.location.line if self.location else None,
            "col": self.location.col if self.location else None,
        }
