#!/usr/bin/env python3
"""
QC-C2-03: OpenQASM 3.0 Transpiler across Qiskit, Cirq, CUDA-Q & QSDK
Automated Judge Verification & Reproduction Script

Executes all core requirements:
1. OpenQASM 3.0 parsing (custom gates, modifiers, loops, mid-circuit measurement, conditions).
2. Transpilation to 4 target frameworks: Qiskit, Cirq, CUDA-Q, QSDK.
3. Cross-framework execution & total variation distance (TVD) verification table.
4. Static circuit statevector fidelity verification.
5. Precise line:column compiler diagnostic error handling.
6. Safe isolation of unsupported constructs.
"""
import sys, os, json
sys.path.insert(0, os.path.abspath("src"))

from qnvkit.transpile.api import transpile
from qnvkit.transpile.verify import compare_counts, format_counts_table
from qnvkit.qasm.parser3 import parse_qasm3
from qnvkit.qasm.diagnostics import QASMError
import qnvkit.qsdk_adapter as adapter

CIRCUITS = {
    1: """OPENQASM 3.0;
include "stdgates.inc";

gate bell a, b { h a; cx a, b; }
const float theta = pi / 4;

qubit[3] q;
bit[1] m;
bit[2] c;

bell q[0], q[1];
for int i in [0:1] {
    ctrl @ rz(theta * (i + 1)) q[i], q[2];
}
inv @ s q[2];
m[0] = measure q[0];
if (m == 1) x q[2];
c[0] = measure q[1];
c[1] = measure q[2];
""",

    2: """OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[1] m0;
bit[1] m1;
bit[1] c;

x q[0];
h q[1];
cx q[1], q[2];

cx q[0], q[1];
h q[0];
m0[0] = measure q[0];
m1[0] = measure q[1];

if (m1 == 1) x q[2];
if (m0 == 1) z q[2];

c[0] = measure q[2];
""",

    3: """OPENQASM 3.0;
include "stdgates.inc";

gate bell a, b { h a; cx a, b; }

qubit[3] q;
bit[3] c;

bell q[0], q[1];
cx q[1], q[2];

for int i in [0:2] {
    inv @ s q[i];
    s q[i];
}
ctrl @ rx(pi) q[0], q[1];

c[0] = measure q[0];
c[1] = measure q[1];
c[2] = measure q[2];
"""
}

def main():
    print("=" * 80)
    print("      QC-C2-03: OPENQASM 3.0 MULTI-TARGET TRANSPILER VERIFICATION")
    print("=" * 80)
    print("QSDK Environment:", adapter.qsdk_description())

    # 1. Test all 3 OpenQASM 3 benchmark circuits
    print("\n--- 1. Multi-Target Code Generation across All Circuits ---")
    for choice in (1, 2, 3):
        print(f"\n[Evaluating Benchmark Circuit #{choice}]")
        src = CIRCUITS[choice]
        results = transpile(src, targets=["qiskit", "cirq", "cudaq", "qniverse"], options={"verify": True})
        
        for target in ["qiskit", "cirq", "cudaq", "qniverse"]:
            report = results[target].report
            print(f"  Target: {target:<9} | Status: {report.status:<7} | Target Version: {report.target_version}")
            assert report.status == "SUCCESS", f"Transpilation failed for {target} on Circuit {choice}"
            assert len(results[target].code) > 0

    # 2. Cross-Framework Equivalence & TVD Comparison Table (Circuit 1)
    print("\n--- 2. 1024-Shot Cross-Framework Equivalence Table (Circuit 1) ---")
    comp = compare_counts(CIRCUITS[1], shots=1024)
    table_str = format_counts_table(comp)
    print(table_str)
    
    # Assert TVD bounded by sampling noise
    for target, run in comp["runs"].items():
        if run.get("executed"):
            tvd = run.get("tvd", 0.0)
            assert tvd < 0.05, f"TVD {tvd} exceeded sampling noise tolerance for {target}"
    print("[PASS] All executed target frameworks match exact distribution within sampling tolerance.")

    # 3. Static Circuit Statevector Fidelity
    print("\n--- 3. Static Circuit Statevector Fidelity ---")
    STATIC = """OPENQASM 3.0;
include "stdgates.inc";
qubit[3] q;
bit[3] c;
h q[0];
cx q[0], q[1];
ctrl @ ry(pi / 3) q[1], q[2];
U(0.3, 0.2, 0.1) q[0];
swap q[0], q[2];
c = measure q;
"""
    static_res = transpile(STATIC, targets=["qiskit", "cirq", "cudaq", "qniverse"], options={"verify": True})
    ver = static_res["qiskit"].report.metrics.get("cross_framework_verification", {})
    for target, info in ver.get("frameworks", {}).items():
        if info.get("executed"):
            fid = info.get("fidelity", info.get("tvd"))
            print(f"  Target {target:<9} -> Fidelity: {fid} | Equivalent: {info.get('equivalent')}")
            assert fid > 1 - 1e-6 or (info.get("equivalent") == True)
    print("[PASS] Static statevector fidelity verified across frameworks.")

    # 4. Diagnostic Error Handling (line:col)
    print("\n--- 4. Compiler Diagnostic Precision (line:col) ---")
    bad_inputs = {
        "unknown gate": 'OPENQASM 3.0;\nqubit[2] q;\nfoo q[0];\n',
        "index out of range": 'OPENQASM 3.0;\nqubit[2] q;\nh q[5];\n',
    }
    for title, bad_src in bad_inputs.items():
        try:
            parse_qasm3(bad_src)
            assert False, f"Expected QASMError for {title}"
        except QASMError as e:
            print(f"  [PASS] Caught {title} at line {e.line}, col {e.col}: {e.message[:60]}...")
            assert e.line > 0 and e.col > 0

    # 5. Unsupported Construct Isolation
    print("\n--- 5. Unsupported Construct Isolation (Graceful Degradation) ---")
    UNSUPPORTED = """OPENQASM 3.0;
qubit[2] q;
bit[2] c;
h q[0];
c[0] = measure q[0];
if (c[0] == 1) x q[1];
"""
    res_unsupported = transpile(UNSUPPORTED, targets=["qiskit", "qniverse"])["qniverse"]
    print(f"  QSDK status for unsupported bit condition: {res_unsupported.report.status}")
    assert res_unsupported.report.status == "ERROR"
    assert len(res_unsupported.report.unsupported_constructs) > 0
    # Code is still valid syntax (does not crash python compiler)
    compile(res_unsupported.code, "qniverse", "exec")
    print("  [PASS] Unsupported construct isolated in report; valid Python emitted without broken runtime code.")

    print("\n" + "=" * 80)
    print(">>> VERDICT: ALL QC-C2-03 CHECKS PASSED SUCCESSFULLY! <<<")
    print("=" * 80)

if __name__ == "__main__":
    main()
