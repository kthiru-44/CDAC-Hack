import math
import pytest
from qnvkit.qasm.expr import evaluate_expression
from qnvkit.qasm.diagnostics import QASMError


def test_expr_basic():
    assert evaluate_expression("pi") == math.pi
    assert evaluate_expression("pi / 2") == math.pi / 2
    assert evaluate_expression("2 * pi") == 2 * math.pi
    assert evaluate_expression("1.5 + 2.5 * 3") == 9.0


def test_expr_functions():
    assert evaluate_expression("sin(0)") == 0.0
    assert evaluate_expression("cos(0)") == 1.0
    assert evaluate_expression("sqrt(4)") == 2.0
    assert evaluate_expression("exp(0)") == 1.0


def test_expr_variables():
    vars = {"theta": 0.5, "phi": 1.2}
    assert evaluate_expression("theta + phi", variables=vars) == 1.7
    assert evaluate_expression("2 * theta", variables=vars) == 1.0


def test_expr_errors():
    with pytest.raises(QASMError) as excinfo:
        evaluate_expression("1 / 0")
    assert "Division by zero" in str(excinfo.value)

    with pytest.raises(QASMError) as excinfo:
        evaluate_expression("unknown_var")
    assert "Undefined variable" in str(excinfo.value)
