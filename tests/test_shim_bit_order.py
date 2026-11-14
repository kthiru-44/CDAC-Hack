import qnvkit.qsdk_adapter  # noqa: F401  (puts the local stand-in on sys.path when needed)
import pytest


def test_run_reports_x_on_qubit0_as_classical_bit0():
    try:
        from Qniverse.QniverseCircuit import QniverseCircuit, QuantumRegister, ClassicalRegister
        from Qniverse.gates import x, measure
        from Qniverse.backend import Backend
        from Qniverse import api
    except ImportError:
        pytest.skip("Qniverse unavailable")
    if not getattr(__import__("Qniverse"), "IS_LOCAL_STAND_IN", False):
        pytest.skip("only the local stand-in is tested")
    qc = QniverseCircuit()
    q = QuantumRegister(2, "q"); c = ClassicalRegister(2, "c")
    qc.add_register(q); qc.add_register(c)
    qc.add_gate(x, q[0])
    qc.add_gate(measure, q[0], c[0]); qc.add_gate(measure, q[1], c[1])
    b = Backend(); b.processor("CPU"); b.hpc("QACC_Cluster"); b.simulator("qasm_simulator")
    job = api.run(qc, b, 50)
    # classical bit 0 is printed right-most: q[0]=1 -> "01"
    assert api.fetch_job_result(None, job)["probability"] == {"01": 50}
