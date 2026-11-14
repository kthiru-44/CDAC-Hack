#!/usr/bin/env python3
"""
QC-C1-01 demo: circuit profiling and limited basis-gate decomposition.

    python examples/c1_demo.py            # no jobs submitted
    python examples/c1_demo.py --live     # also submits ONE job through the QSDK job API

Circuits are built with the documented QSDK calls. Inside Qniverse JupyterLab the official
`Qniverse` package is used; elsewhere a local stand-in with the same calls is used, and the
script says which one is active.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import qnvkit.qsdk_adapter as adapter  # noqa: E402  (must come before `import Qniverse`)
from qnvkit.metrics import profile  # noqa: E402
from qnvkit.decompose.decomposer import decompose  # noqa: E402
from Qniverse.QniverseCircuit import QniverseCircuit, QuantumRegister, ClassicalRegister  # noqa: E402
from Qniverse.gates import h, s, t, cx, cz, swap, ccx, crz, barrier, measure  # noqa: E402


def build_sample_circuit():
    qc = QniverseCircuit()
    q = QuantumRegister(3, "q")
    c = ClassicalRegister(3, "c")
    qc.add_register(q)
    qc.add_register(c)

    qc.add_gate(h, q[0])
    qc.add_gate(s, q[1])
    qc.add_gate(t, q[2])
    qc.add_gate(cx, q[0], q[1])
    qc.add_gate(cz, q[1], q[2])
    qc.add_gate(swap, q[0], q[2])
    qc.add_gate(crz(0.7), q[0], q[1])
    qc.add_gate(ccx, q[0], q[1], q[2])
    qc.add_gate(barrier, q[0], q[1], q[2])
    for i in range(3):
        qc.add_gate(measure, q[i], c[i])
    return qc


def section(title):
    print("\n" + "=" * 78 + "\n" + title + "\n" + "=" * 78)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="submit one job through the QSDK job API")
    args = parser.parse_args()

    print("QC-C1-01: Circuit Profiling and Limited Basis-Gate Decomposition")
    print("QSDK in use:", adapter.qsdk_description())

    qc = build_sample_circuit()
    original_qasm = adapter.read_qasm(qc)

    section("1. Input circuit (qc.qasm()) and its profile")
    print(original_qasm.strip())
    print()
    print(profile(qc).summary())

    section("2. Decompose into basis {rx, ry, rz, cx}")
    res = decompose(qc, {"rx", "ry", "rz", "cx"})
    print(res.summary())
    print("Decomposed circuit (new QniverseCircuit), first lines:")
    lines = adapter.read_qasm(res.circuit).splitlines()
    for line in lines[:14]:
        print("  " + line)
    print("  ... (%d more lines)" % max(0, len(lines) - 14))

    section("3. Other bases on the same circuit")
    for basis in ({"u3", "cx"}, {"rz", "ry", "cz"}, {"rx", "rz", "cx"}, {"p", "ry", "cx"}):
        r = decompose(qc, basis)
        if r.circuit is None:
            print("%-22s -> unsupported" % sorted(basis))
            continue
        print("%-26s gates %2d -> %3d | depth %2d -> %3d | verified=%s | %s" % (
            sorted(basis), r.before.total_gates, r.after.total_gates,
            r.before.depth, r.after.depth, r.verified, r.after.gate_counts))

    section("4. Unsupported cases: explicit report, no circuit emitted")
    for basis, why in (
        ({"rx", "ry", "rz"}, "no entangling gate in the basis"),
        ({"h", "t", "cx"}, "discrete basis cannot express crz(0.7) exactly"),
    ):
        r = decompose(qc, basis)
        print("Basis %s (%s)" % (sorted(basis), why))
        print("  circuit returned:", r.circuit)
        print("  " + r.unsupported.summary().replace("\n", "\n  "))
    for bad_basis in (set(), {"cx", "sx"}):
        try:
            decompose(qc, bad_basis)
        except ValueError as e:
            print("Basis %s rejected: %s" % (sorted(bad_basis), str(e)[:110]))

    section("5. Input circuit unchanged")
    print("qc.qasm() identical before and after all calls:", adapter.read_qasm(qc) == original_qasm)

    if args.live:
        section("6. Run original and decomposed circuits through the QSDK job API")
        from qnvkit.runner import QniverseRunner
        runner = QniverseRunner(max_jobs_quota=2)
        if runner.is_live and not runner.token:
            print("Set QNIVERSE_API_KEY (or define `token`) first; no job submitted.")
            return
        print("Credit balance:", runner.get_balance())
        for label, circ in (("original", qc), ("decomposed", res.circuit)):
            out = runner.execute_circuit(circ, "CPU", "QACC_Cluster", "qasm_simulator", shots=1024,
                                         job_name="c1_demo_" + label)
            print("%-10s executed on: %s | result: %s" % (label, out["executed_on"], out["result"]))


if __name__ == "__main__":
    main()
