"""Every valid program x every target compiles; the generated code is executed and checked."""
import pytest
from qnvkit.qasm.parser3 import parse_qasm3
from qnvkit.transpile.api import transpile
from qnvkit.transpile import verify as V
from c2_programs import PROGRAMS, QSDK_UNSUPPORTED

TARGETS = ("qiskit", "cirq", "cudaq", "qniverse")


@pytest.fixture(scope="module")
def results():
    return {n: transpile(s, targets=TARGETS) for n, s in PROGRAMS.items()}


@pytest.mark.parametrize("name", sorted(PROGRAMS))
@pytest.mark.parametrize("target", TARGETS)
def test_compiles_and_status(results, name, target):
    r = results[name][target]
    compile(r.code, "%s_%s" % (name, target), "exec")
    if target == "qniverse" and name in QSDK_UNSUPPORTED:
        assert r.report.status == "ERROR"
        u = r.report.unsupported_constructs[0]
        assert u["line"] is not None and u["col"] is not None
    else:
        assert r.report.status in ("SUCCESS", "WARNING"), r.report.unsupported_constructs


def test_unsupported_construct_never_emits_broken_code(results):
    r = results["cond_bit"]["qniverse"]
    compile(r.code, "x", "exec")
    assert "add_conditional_gate" not in r.code


@pytest.mark.parametrize("name", sorted(PROGRAMS))
def test_generated_code_executes_and_matches_reference(name):
    ir = parse_qasm3(PROGRAMS[name])
    rep = V.verify_equivalence(ir)
    assert "error" not in rep, rep.get("error")
    for fw, info in rep["frameworks"].items():
        if not info.get("executed"):
            assert info.get("note") or info.get("error")
            assert "error" not in info, (fw, info)
            continue
        assert info["equivalent"], (name, fw, info)
        if "fidelity" in info:
            assert info["fidelity"] >= 1 - 1e-9
        if "tvd" in info:
            assert info["tvd"] <= V.TVD_TOLERANCE


@pytest.mark.parametrize("name", sorted(PROGRAMS))
def test_qsdk_code_runs_against_standin(results, name):
    import qnvkit.qsdk_adapter  # puts the stand-in on sys.path
    r = results[name]["qniverse"]
    if r.report.status == "ERROR":
        pytest.skip("unsupported on the QSDK, reported")
    ns = {}
    exec(r.code, ns)
    qc = ns["build_circuit"]()
    assert "OPENQASM" in qc.qasm()
    assert "import qnvkit" not in r.code and "from qnvkit" not in r.code


def test_generated_qsdk_code_has_no_forbidden_imports(results):
    code = results["basic"]["qniverse"].code
    assert "from qnvkit" not in code and ".api" not in code and "QniverseCircuit()" in code


def test_cudaq_static_state_executed_not_claimed():
    pytest.importorskip("cudaq")
    rep = V.verify_equivalence(parse_qasm3(PROGRAMS["allstd"]))
    c = rep["frameworks"]["cudaq"]
    assert c["executed"] is True and c["fidelity"] >= 1 - 1e-9 and "calibrated" in c["endianness"]


def test_verify_reports_missing_framework_as_not_run(monkeypatch):
    monkeypatch.setattr(V, "HAS_CUDAQ", False)
    rep = V.verify_equivalence(parse_qasm3(PROGRAMS["basic"]))
    c = rep["frameworks"]["cudaq"]
    assert c["executed"] is False and "equivalent" not in c
    res = transpile(PROGRAMS["basic"], targets=("cudaq",), options={"verify": True})
    assert res["cudaq"].report.equivalence_verified is None


def test_cirq_conditions_on_bits_of_larger_register():
    pytest.importorskip("cirq")
    src = ('OPENQASM 3.0; qubit[3] q; bit[2] c; x q[0]; c[0] = measure q[0]; c[1] = measure q[1]; '
           'if (c[0] == 1) x q[2]; if (c[1] == 1) h q[2];')
    code = transpile(src, targets=("cirq",))["cirq"].code
    ns = {}
    exec(code, ns)
    import cirq
    res = cirq.Simulator(seed=3).run(ns["build_circuit"](), repetitions=20)
    assert set(res.records) == {"c_0", "c_1"}
