from qnvkit.report import Diagnostic, TranspileReport, TranspileResult


def test_transpile_report_success():
    rep = TranspileReport(target="qiskit", target_version=">=1.0.0")
    assert rep.status.lower() == "success"
    assert len(rep.warnings) == 0
    assert len(rep.unsupported_constructs) == 0

    d = rep.to_dict()
    assert d["status"].lower() == "success"
    assert d["target"] == "qiskit"


def test_transpile_report_warnings_and_errors():
    rep = TranspileReport(target="cudaq", target_version=">=0.8.0")
    rep.add_warning("Dynamic circuit unrolled")
    assert rep.status.lower() == "warning"

    rep.add_unsupported("while-loop", line=12, col=5)
    assert rep.status.lower() == "error"
    assert len(rep.unsupported_constructs) == 1
    assert rep.unsupported_constructs[0]["line"] == 12
    assert rep.unsupported_constructs[0]["col"] == 5

    res = TranspileResult(target="cudaq", code="// code", report=rep)
    j = res.to_json()
    assert "Unsupported construct: while-loop" in j
