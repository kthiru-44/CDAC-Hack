"""
qnvkit.qasm.expr: Safe parameter expression evaluator for OpenQASM 2.0 / 3.0.

Expressions are parsed with Python's ``ast`` module and evaluated by a small whitelist
interpreter (numbers, constants, + - * / ** %, unary +/-, calls of whitelisted functions).
``eval`` is never used, so no attribute access, subscripts, lambdas or names outside the
whitelist can be reached.
"""

import ast
import math
import operator
import re
from typing import Optional, Dict
from qnvkit.qasm.diagnostics import QASMError

SAFE_MATH_ENV = {
    "pi": math.pi,
    "tau": math.tau,
    "euler": math.e,
    "e": math.e,
}

SAFE_FUNCTIONS = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "exp": math.exp, "sqrt": math.sqrt, "abs": abs,
    "ln": math.log, "log": math.log,
    "arcsin": math.asin, "arccos": math.acos, "arctan": math.atan,
    "floor": math.floor, "ceiling": math.ceil, "ceil": math.ceil,
}

_EXPR_CLEANER = re.compile(r"[^0-9a-zA-Z_\+\-\*\/\^\.\(\)\s,%]")
_ATTRIBUTE_ACCESS = re.compile(r"[A-Za-z_\)\]]\s*\.\s*[A-Za-z_]")

_BIN_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


class ExprEvaluator:
    """Evaluates mathematical expressions with variables and constants."""
    def __init__(self, variables: Optional[Dict[str, float]] = None):
        self.env = dict(SAFE_MATH_ENV)
        if variables:
            self.env.update(variables)

    def _eval(self, node, text):
        if isinstance(node, ast.Expression):
            return self._eval(node.body, text)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                raise QASMError(f"Illegal constant in parameter expression: {text}")
            return node.value
        if isinstance(node, ast.Name):
            if node.id in self.env:
                return self.env[node.id]
            raise NameError(node.id)
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
            return _UNARY_OPS[type(node.op)](self._eval(node.operand, text))
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
            left = self._eval(node.left, text)
            right = self._eval(node.right, text)
            if isinstance(node.op, ast.Pow) and abs(right) > 1000:
                raise QASMError(f"Exponent too large in expression '{text}'")
            return _BIN_OPS[type(node.op)](left, right)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
            fn = SAFE_FUNCTIONS.get(node.func.id)
            if fn is None:
                raise NameError(node.func.id)
            return fn(*[self._eval(a, text) for a in node.args])
        raise QASMError(f"Unsupported syntax in parameter expression '{text}'")

    def evaluate(self, expr_str: str) -> float:
        val = self._evaluate(expr_str)
        if not math.isfinite(val):
            raise QASMError(f"Expression '{expr_str}' is not a finite number")
        return val

    def _evaluate(self, expr_str: str) -> float:
        s = expr_str.strip()
        if not s:
            return 0.0

        try:
            return float(s)
        except ValueError:
            pass

        if _EXPR_CLEANER.search(s):
            raise QASMError(f"Illegal characters in parameter expression: {expr_str}")
        if "__" in s or _ATTRIBUTE_ACCESS.search(s):
            raise QASMError(f"Illegal construct in parameter expression: {expr_str}")

        py_expr = s.replace("^", "**")
        try:
            tree = ast.parse(py_expr, mode="eval")
            return float(self._eval(tree, expr_str))
        except QASMError:
            raise
        except ZeroDivisionError:
            raise QASMError(f"Division by zero in expression '{expr_str}'")
        except (NameError, TypeError) as e:
            raise QASMError(f"Undefined variable in expression '{expr_str}': {e}")
        except SyntaxError:
            raise QASMError(f"Invalid parameter expression '{expr_str}'")
        except Exception as e:
            raise QASMError(f"Failed to evaluate expression '{expr_str}': {e}")


def evaluate_expression(expr_str: str, variables: Optional[Dict[str, float]] = None) -> float:
    """
    Safely evaluates a mathematical parameter expression string to a float.
    Replaces ^ with **. Supports user variables and standard math functions.
    """
    evaluator = ExprEvaluator(variables)
    return evaluator.evaluate(expr_str)
