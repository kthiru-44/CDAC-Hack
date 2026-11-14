#!/usr/bin/env python3
"""QC-C2-03 demonstration (same content as notebooks/c2_demo.ipynb)."""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

print("\n" + "#" * 70)
print('QC-C2-03: OpenQASM 3.0 Transpiler across Qiskit, Cirq, CUDA-Q & QSDK')


import json
from qnvkit.transpile.api import transpile
from qnvkit.qasm.parser3 import parse_qasm3
from qnvkit.qasm.diagnostics import QASMError
print("qnvkit transpiler ready")

print("\n" + "#" * 70)
print('1. One OpenQASM 3 program: custom gate, modifiers, loop, measurement, condition')

QASM3_SOURCE = """OPENQASM 3.0;
include "stdgates.inc";

gate bell a, b { h a; cx a, b; }      // custom gate
const float theta = pi / 4;

qubit[3] q;
bit[1] m;
bit[2] c;

bell q[0], q[1];
for int i in [0:1] {                   // loop, unrolled
    ctrl @ rz(theta * (i + 1)) q[i], q[2];   // modifier -> crz
}
inv @ s q[2];                          // modifier -> sdg
m[0] = measure q[0];
if (m == 1) x q[2];                    // classical condition
c[0] = measure q[1];
c[1] = measure q[2];
"""
print(QASM3_SOURCE)

print("\n" + "#" * 70)
print('2. Generated code, verified (executed) per target')

results = transpile(QASM3_SOURCE, targets=["qiskit", "cirq", "cudaq", "qniverse"], options={"verify": True})
for target, res in results.items():
    print("=" * 70)
    print(target.upper(), "|", res.report.target_version, "| status:", res.report.status)
    print("-" * 70)
    print(res.code)

print("\n" + "#" * 70)
print('3. Structured report (CUDA-Q shown)')

print(results["cudaq"].report.to_json(indent=2))

print("\n" + "#" * 70)
print('4. Equivalence table')

ver = results["qiskit"].report.metrics["cross_framework_verification"]
print("mode:", ver.get("mode"))
print("%-9s %-9s %-11s %-10s %s" % ("target", "executed", "equivalent", "fid/tvd", "note"))
for name, info in ver["frameworks"].items():
    val = info.get("fidelity", info.get("tvd"))
    print("%-9s %-9s %-11s %-10s %s" % (
        name, info.get("executed"), info.get("equivalent", "-"),
        "-" if val is None else "%.4f" % val, info.get("note") or info.get("error") or ""))

print("\n" + "#" * 70)
print('5. Invalid input: precise `line:column` diagnostics')

bad_programs = {
    "unknown gate": 'OPENQASM 3.0;\nqubit[2] q;\nfoo q[0];\n',
    "index out of range": 'OPENQASM 3.0;\nqubit[2] q;\nh q[5];\n',
}
for title, src in bad_programs.items():
    try:
        parse_qasm3(src)
    except QASMError as e:
        print("[%s] line %d, col %d" % (title, e.line, e.col))
        print(e)
        print()

print("\n" + "#" * 70)
print('6. An unsupported construct is reported, never emitted as broken code')

UNSUPPORTED = """OPENQASM 3.0;
qubit[2] q;
bit[2] c;
h q[0];
c[0] = measure q[0];
if (c[0] == 1) x q[1];
"""
res = transpile(UNSUPPORTED, targets=["qiskit", "qniverse"])["qniverse"]
print("status:", res.report.status)
print(json.dumps(res.report.unsupported_constructs, indent=2))
compile(res.code, "qniverse", "exec")
print("generated QSDK code is still valid Python and omits the unsupported operation")

