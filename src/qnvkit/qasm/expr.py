"""
qnvkit.qasm.expr: Safe parameter expression evaluator for OpenQASM 2.0 / 3.0.
Evaluates expressions containing numbers, pi, +, -, *, /, **, sin, cos, tan, exp, etc.
"""

import math
import re

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


def evaluate_expression(expr_str: str) -> float:
    """
    Safely evaluates a mathematical parameter expression string to a float.
    Replaces ^ with **.
    """
    s = expr_str.strip()
    if not s:
        return 0.0
    
    # Quick numeric float parsing
    try:
        return float(s)
    except ValueError:
        pass

    # Clean and check
    if _EXPR_CLEANER.search(s):
        raise ValueError(f"Illegal characters in parameter expression: {expr_str}")

    py_expr = s.replace("^", "**")
    
    # Evaluate in restricted namespace
    try:
        val = eval(py_expr, {"__builtins__": None}, SAFE_MATH_ENV)
        return float(val)
    except Exception as e:
        raise ValueError(f"Failed to evaluate expression '{expr_str}': {e}")
