#!/usr/bin/env python3
"""
QC-C1-01 Demonstration Script: Circuit Profiling and Limited Basis-Gate Decomposition
PESU - C-DAC Quantum Hackathon

Usage:
  python examples/c1_demo.py
  python examples/c1_demo.py --live   # (Optional: dispatches 1 sample job to Qniverse cloud)
"""

import sys
import argparse
from qnvkit.ir import CircuitIR, Register, Op
from qnvkit.metrics import profile
from qnvkit.decompose.decomposer import decompose
from qnvkit.qsdk_adapter import from_qniverse, to_qniverse
from qnvkit.shim.Qniverse.QniverseCircuit import QniverseCircuit, QuantumRegister, ClassicalRegister


def create_sample_quantum_circuit() -> QniverseCircuit:
    """Builds a benchmark 3-qubit quantum circuit containing single, two, and multi-qubit gates."""
    qc = QniverseCircuit()
    qc.add_register(QuantumRegister(3, 'q'))
    qc.add_register(ClassicalRegister(3, 'c'))

    # Superposition and phase
    qc.add_gate("h", 0)
    qc.add_gate("s", 1)
    qc.add_gate("t", 2)

    # Entanglement
    qc.add_gate("cx", 0, 1)
    qc.add_gate("cz", 1, 2)
    qc.add_gate("swap", 0, 2)

    # Multi-qubit Toffoli
    qc.add_gate("ccx", 0, 1, 2)

    # Barriers and measurement
    qc.add_gate("barrier", 0, 1, 2)
    qc.add_gate("measure", 0, 0)
    qc.add_gate("measure", 1, 1)
    qc.add_gate("measure", 2, 2)

    return qc


def main():
    parser = argparse.ArgumentParser(description="QC-C1-01 Circuit Profiling & Decomposition Demo")
    parser.add_argument("--live", action="store_true", help="Submit decomposed circuit to Qniverse cloud")
    args = parser.parse_args()

    print("================================================================================")
    print("      PESU – C-DAC QUANTUM HACKATHON: QC-C1-01 VERIFICATION DEMO")
    print("      Module: Circuit Profiling & Limited Basis-Gate Decomposition")
    print("================================================================================\n")

    # 1. Create and Profile Sample Circuit
    qc = create_sample_quantum_circuit()
    print("1. PROFILING INPUT QUANTUM CIRCUIT:")
    initial_profile = profile(qc)
    print(initial_profile.summary())
    print("\nOriginal OpenQASM 2.0 Export:")
    print("-----------------------------")
    print(qc.qasm().strip())
    print("-----------------------------\n")

    # 2. Decompose into C-DAC Native Basis: {rx, ry, rz, cx}
    print("2. DECOMPOSING INTO NATIVE QNIVERSE BASIS: {rx, ry, rz, cx}")
    basis_native = {"rx", "ry", "rz", "cx"}
    res_native = decompose(qc, basis_native)
    print(res_native.summary())
    print("Decomposed QASM Sample (first 10 lines):")
    decomposed_qasm = res_native.circuit.qasm().splitlines()
    for line in decomposed_qasm[:12]:
        print(f"  {line}")
    if len(decomposed_qasm) > 12:
        print(f"  ... ({len(decomposed_qasm) - 12} more lines)")
    print()

    # 3. Decompose into Universal U3 Basis: {u3, cx}
    print("3. DECOMPOSING INTO UNIVERSAL BASIS: {u3, cx}")
    basis_u3 = {"u3", "cx"}
    res_u3 = decompose(qc, basis_u3)
    print(f"  Status: {'SUCCESS' if res_u3.circuit else 'FAILED'}")
    print(f"  Equivalence Verified: {res_u3.verified}")
    print(f"  Gate Count: {res_u3.before.total_gates} -> {res_u3.after.total_gates}")
    print(f"  Scheduled Depth: {res_u3.before.depth} -> {res_u3.after.depth}")
    print(f"  Gate Breakdown: {res_u3.after.gate_counts}\n")

    # 4. Demonstrate Negative Test: Unsupported Basis Decomposition
    print("4. NEGATIVE TEST: UNSUPPORTED OPERATION REPORTING")
    print("Attempting to decompose an entangling circuit into a 1-qubit-only basis: {rx, ry, rz}")
    basis_unsupported = {"rx", "ry", "rz"}
    res_unsupported = decompose(qc, basis_unsupported)
    print(f"  Circuit emitted: {res_unsupported.circuit} (Strictly None to prevent silent invalid emission)")
    print(f"  Unsupported Report Present: {res_unsupported.unsupported is not None}")
    if res_unsupported.unsupported:
        print(res_unsupported.unsupported.summary())
    print()

    # 5. Live Qniverse Cloud Dispatch (Optional)
    if args.live:
        print("5. DISPATCHING TO C-DAC QNIVERSE CLOUD (Credit Guard Active):")
        from qnvkit.runner import QniverseRunner
        runner = QniverseRunner(max_jobs_quota=2)
        try:
            balance = runner.get_balance()
            print(f"  Current Credit Balance: {balance} credits")
            print("  Submitting decomposed circuit to CPU qasm_simulator on QACC_Cluster...")
            res = runner.execute_circuit(res_native.circuit, processor="CPU", hpc="QACC_Cluster", simulator="qasm_simulator")
            print(f"  Job Success! Job ID: {res['job_id']}")
            print(f"  Execution Counts: {res['result'].get('counts')}")
        except Exception as e:
            print(f"  Cloud dispatch note: {e}")

    print("\nQC-C1-01 Demonstration Completed Successfully.")


if __name__ == "__main__":
    main()
