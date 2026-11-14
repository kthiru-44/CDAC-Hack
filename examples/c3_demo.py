#!/usr/bin/env python3
"""
QC-C3-03 Demonstration Script: Quantum Circuit Optimization Using QSDK
PESU - C-DAC Quantum Hackathon

Usage:
  python examples/c3_demo.py
  python examples/c3_demo.py --live   # (Optional: dispatches 1 optimized job to Qniverse cloud)
"""

import sys
import os
import argparse
import numpy as np

# Ensure src is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from qnvkit.ir import CircuitIR, Register, Op
from qnvkit.metrics import profile
from qnvkit.optimize.optimizer import optimize
from qnvkit.qsdk_adapter import from_qniverse, to_qniverse
from Qniverse.QniverseCircuit import QniverseCircuit, QuantumRegister, ClassicalRegister
from Qniverse.gates import h, x, y, z, s, sdg, t, tdg, rz, cx, cz, swap, barrier, measure


def build_redundant_circuit() -> QniverseCircuit:
    """
    Constructs a 3-qubit circuit containing redundant gate sequences:
    - Explicit identity/zero-rotation
    - Self-inverse pairs (X-X, H-H)
    - Consecutive identical CX pairs
    - Consecutive inverse pairs (S-Sdg)
    - Consecutive rotations that merge (Rz(0.3) + Rz(0.5) -> Rz(0.8))
    - An intentional barrier protecting a pair from being cancelled
    """
    qc = QniverseCircuit()
    q = QuantumRegister(3, "q")
    c = ClassicalRegister(3, "c")
    qc.add_register(q)
    qc.add_register(c)

    # 1. Self-inverse H-H and X-X pairs
    qc.add_gate(h, q[0])
    qc.add_gate(h, q[0])          # Should cancel with H(0)
    qc.add_gate(x, q[1])
    qc.add_gate(x, q[1])          # Should cancel with X(1)

    # 2. CX-CX cancellation
    qc.add_gate(cx, q[0], q[1])
    qc.add_gate(cx, q[0], q[1])   # Should cancel with CX(0,1)

    # 3. Inverse pair S-Sdg
    qc.add_gate(s, q[2])
    qc.add_gate(sdg, q[2])        # Should cancel with S(2)

    # 4. Continuous rotation merging
    qc.add_gate(rz(0.3), q[0])
    qc.add_gate(rz(0.5), q[0])    # Should merge to Rz(0.8)

    # 5. Intentional pair PROTECTED by a barrier (Negative Test)
    qc.add_gate(z, q[1])
    qc.add_gate(barrier, q[0], q[2])  # Barrier spans wires
    qc.add_gate(z, q[1])          # MUST NOT cancel because of barrier!

    # 6. Real computational gate and measurements
    qc.add_gate(cx, q[1], q[2])
    for i in range(3):
        qc.add_gate(measure, q[i], c[i])

    return qc


def main():
    parser = argparse.ArgumentParser(description="QC-C3-03 Circuit Optimizer Demo")
    parser.add_argument("--live", action="store_true", help="Submit optimized circuit to Qniverse cloud")
    args = parser.parse_args()

    print("================================================================================")
    print("      PESU – C-DAC QUANTUM HACKATHON: QC-C3-03 VERIFICATION DEMO")
    print("      Module: Quantum Circuit Optimization Using QSDK")
    print("================================================================================\n")

    qc = build_redundant_circuit()

    print("1. PROFILING UNOPTIMIZED QUANTUM CIRCUIT:")
    initial_profile = profile(qc)
    print(initial_profile.summary())
    print("\nOriginal OpenQASM 2.0 Export:")
    print("-----------------------------")
    print(qc.qasm().strip())
    print("-----------------------------\n")

    # 2. Run Mandatory Optimization Passes
    print("2. APPLYING MANDATORY PASSES: ['remove_identity', 'cancel_self_inverse', 'cancel_cx']")
    res_mandatory = optimize(qc, passes=["remove_identity", "cancel_self_inverse", "cancel_cx"])
    print("  " + res_mandatory.summary().replace("\n", "\n  "))

    # 3. Run Full Pipeline with Extras (Inverse pairs, Rotation merging, Fixed Point)
    print("3. APPLYING FULL OPTIMIZATION PIPELINE (WITH EXTRAS & FIXED POINT):")
    all_passes = [
        "remove_identity",
        "cancel_self_inverse",
        "cancel_cx",
        "cancel_extended_self_inverse",
        "cancel_inverse_pairs",
        "merge_rotations",
    ]
    res_full = optimize(qc, passes=all_passes, fixed_point=True)
    print("  " + res_full.summary().replace("\n", "\n  "))
    print("\nOptimized OpenQASM 2.0 Export:")
    print("------------------------------")
    print(res_full.circuit.qasm().strip())
    print("------------------------------\n")

    # 4. Verify Barrier Guard (Negative Test)
    print("4. NEGATIVE TEST VERIFICATION (BARRIER PROTECTION):")
    # Z(1) before barrier and Z(1) after barrier should STILL be present!
    z_count = res_full.after.gate_counts.get("z", 0)
    print(f"  Remaining 'z' gates: {z_count} (Expected: 2, protected by barrier)")
    assert z_count == 2, "Security guardrail failed: barrier did not protect gates!"
    print("  [PASSED] Barrier strictly prevented cancellation across timing boundary.\n")

    # 5. Live Qniverse Cloud Dispatch (Optional)
    if args.live:
        print("5. DISPATCHING OPTIMIZED CIRCUIT TO C-DAC QNIVERSE CLOUD:")
        from qnvkit.runner import QniverseRunner
        runner = QniverseRunner(max_jobs_quota=2)
        try:
            balance = runner.get_balance()
            print(f"  Current Credit Balance: {balance} credits")
            print("  Submitting optimized circuit to CPU qasm_simulator on QACC_Cluster...")
            res = runner.execute_circuit(res_full.circuit, processor="CPU", hpc="QACC_Cluster", simulator="qasm_simulator")
            print(f"  Job Success! Job ID: {res['job']} ({res['executed_on']})")
            print(f"  Execution Result: {res['result']}")
        except Exception as e:
            print(f"  Cloud dispatch note: {e}")

    print("\nQC-C3-03 Demonstration Completed Successfully.")


if __name__ == "__main__":
    main()
