"""
qnvkit.qasm.expr: Safe parameter expression evaluator for OpenQASM 2.0 / 3.0.
Evaluates expressions containing numbers, pi, +, -, *, /, **, sin, cos, tan, exp, etc.
"""

import math
import re
from typing import Optional, Dict
from qnvkit.qasm.diagnostics import QASMError

SAFE_MATH_ENV = {
    "pi": math.pi,
    "e": math.e,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "exp": math.exp,
    "sqrt": math.sqrt,
    "abs": abs,
}

_EXPR_CLEANER = re.compile(r"[^0-9a-zA-Z_\+\-\*\/\^\.\(\)\s,]")


class ExprEvaluator:
    """Evaluates mathematical AST / expressions with variables and constants."""
    def __init__(self, variables: Optional[Dict[str, float]] = None):
        self.env = dict(SAFE_MATH_ENV)
        if variables:
            self.env.update(variables)

    def evaluate(self, expr_str: str) -> float:
        s = expr_str.strip()
        if not s:
            return 0.0

        try:
            return float(s)
        except ValueError:
            pass

        if _EXPR_CLEANER.search(s):
            raise QASMError(f"Illegal characters in parameter expression: {expr_str}")

        py_expr = s.replace("^", "**")
        try:
            val = eval(py_expr, {"__builtins__": None}, self.env)
            return float(val)
        except ZeroDivisionError:
            raise QASMError(f"Division by zero in expression '{expr_str}'")
        except (NameError, TypeError) as e:
            raise QASMError(f"Undefined variable in expression '{expr_str}': {e}")
        except Exception as e:
            raise QASMError(f"Failed to evaluate expression '{expr_str}': {e}")



def evaluate_expression(expr_str: str, variables: Optional[Dict[str, float]] = None) -> float:
    """
    Safely evaluates a mathematical parameter expression string to a float.
    Replaces ^ with **. Supports user variables and standard math functions.
    """
    evaluator = ExprEvaluator(variables)
    return evaluator.evaluate(expr_str)

