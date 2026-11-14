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


class QASMError(ValueError):
    """Exception raised for syntax or semantic errors in QASM source."""
    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        col: Optional[int] = None,
        source_text: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.line = line
        self.col = col
        self.source_text = source_text

    def __str__(self) -> str:
        loc = f" at line {self.line}, col {self.col}" if self.line is not None else ""
        msg = f"QASM Error{loc}: {self.message}"
        if self.source_text and self.line is not None:
            lines = self.source_text.splitlines()
            if 0 < self.line <= len(lines):
                line_content = lines[self.line - 1]
                msg += f"\n  | {line_content}"
                if self.col is not None and self.col > 0:
                    msg += f"\n  | {' ' * (self.col - 1)}^"
        return msg

