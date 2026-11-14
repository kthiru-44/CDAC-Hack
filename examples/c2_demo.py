#!/usr/bin/env python3
"""
QC-C2-03 Standalone Demonstration: OpenQASM 3.0 Transpiler across Qiskit, Cirq, CUDA-Q, and QSDK.

Demonstrates:
1. Parsing an OpenQASM 3.0 circuit with declarations, gates, parameters, and measurement.
2. Generating target-framework source code for Qiskit >= 1.0, Cirq >= 1.4, CUDA-Q >= 0.8, and C-DAC QSDK.
3. Executing circuits on simulated engines and verifying cross-framework fidelity.
4. Emitting a structured JSON transpile report.
"""

import sys
from pathlib import Path

# Add src to python path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from qnvkit.transpile.api import transpile


QASM3_SAMPLE = """// 3-Qubit Entanglement & Parameterized Phase Rotation Circuit
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[3] c;

// Superposition & Entanglement
h q[0];
cx q[0], q[1];

// Parameterized Rotations
rz(pi / 4) q[1];
rx(pi / 2) q[2];
cx q[1], q[2];

// Measurement
c = measure q;
"""


def main():
    print("=" * 76)
    print("  QC-C2-03: OpenQASM 3.0 Transpiler across Qiskit, Cirq, CUDA-Q, & QSDK")
    print("=" * 76)

    print("\n[1] Input OpenQASM 3.0 Program:")
    print("-" * 50)
    print(QASM3_SAMPLE.strip())
    print("-" * 50)

    print("\n[2] Transpiling to targets: Qiskit, Cirq, CUDA-Q, QSDK...")
    results = transpile(
        QASM3_SAMPLE,
        targets=["qiskit", "cirq", "cudaq", "qniverse"],
        options={"verify": True}
    )

    for target, res in results.items():
        rep = res.report
        print(f"\n==================================================")
        print(f" TARGET: {target.upper()} ({rep.target_version})")
        print(f" Status: {rep.status.upper()}")
        print(f" Metrics: {rep.metrics.get('num_qubits')} qubits, {rep.metrics.get('num_clbits')} clbits, {rep.metrics.get('total_ops')} ops")

        ver = rep.metrics.get("cross_framework_verification")
        if ver and "frameworks" in ver and target in ver["frameworks"]:
            fw = ver["frameworks"][target]
            if fw.get("executed"):
                eq_str = "PASSED" if fw.get("equivalent") else "FAILED"
                print(f" Equivalence Verification: {eq_str} (Fidelity: {fw.get('fidelity'):.8f})")
            else:
                print(f" Verification Note: {fw.get('note', fw.get('error'))}")

        print("--------------------------------------------------")
        print("Generated Code Preview:")
        for line in res.code.strip().splitlines()[:18]:
            print("  " + line)
        print("  ...")

    print("\n[3] Structured JSON Report Sample (Qiskit):")
    print(results["qiskit"].report.to_json(indent=2))

    print("\n🎉 QC-C2-03 Demonstration Completed Successfully!\n")


if __name__ == "__main__":
    main()
