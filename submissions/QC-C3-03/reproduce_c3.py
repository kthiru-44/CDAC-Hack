#!/usr/bin/env python3
"""
QC-C3-03: Quantum Circuit Optimization Using QSDK
Automated Judge Verification & Reproduction Script

Executes all core requirements:
1. Multi-circuit benchmark optimization (GHZ, 4-state superposition, interference state).
2. Mandatory pass set and full fixed-point optimization pipeline.
3. Strict timing boundary preservation (Negative Test: Barrier protects Z gates).
4. Discrete rewrite rule verifications (Tests A through F).
5. 4-Qubit Algorithmic Benchmark.
6. Mathematical Equivalence (Unitary Fidelity > 0.99999999).
7. Functional Immutability Verification (source circuit unchanged).
8. 1024-shot simulation measurement comparison (TVD < 0.05).
"""
import sys, os
sys.path.insert(0, os.path.abspath("src"))

import numpy as np
import qnvkit.qsdk_adapter as adapter
from qnvkit.optimize import optimize
from qnvkit.metrics import profile
from qnvkit.qsdk_adapter import from_qniverse
from qnvkit.sim import unitary_fidelity, total_variation_distance
from qnvkit.viz import simulate_circuit
from Qniverse.QniverseCircuit import *
from Qniverse.gates import *

def build_circuit(choice):
    circ = QniverseCircuit()
    q = QuantumRegister(3, 'q')
    c = ClassicalRegister(3, 'c')
    circ.add_register(q)
    circ.add_register(c)

    if choice == 1:
        # Circuit 1: 3-Qubit GHZ Entanglement with Full Redundancy Suite
        circ.add_gate(h, q[0])
        circ.add_gate(cx, q[0], q[1])
        circ.add_gate(cx, q[1], q[2])
        # Redundancies
        circ.add_gate(h, q[2]); circ.add_gate(h, q[2])
        circ.add_gate(x, q[0]); circ.add_gate(x, q[0])
        circ.add_gate(cx, q[0], q[2]); circ.add_gate(cx, q[0], q[2])
        circ.add_gate(s, q[2]); circ.add_gate(sdg, q[2])
        circ.add_gate(rz(0.3), q[0]); circ.add_gate(rz(0.5), q[0])
        # Barrier
        circ.add_gate(z, q[1])
        circ.add_gate(barrier, q[0], q[2])
        circ.add_gate(z, q[1])
    elif choice == 2:
        # Circuit 2: 3-Qubit Superposition & Entangled State (4-state superposition)
        circ.add_gate(h, q[0]); circ.add_gate(h, q[1]); circ.add_gate(cx, q[0], q[2])
        circ.add_gate(x, q[1]); circ.add_gate(x, q[1])
        circ.add_gate(cx, q[1], q[2]); circ.add_gate(cx, q[1], q[2])
        circ.add_gate(s, q[0]); circ.add_gate(sdg, q[0])
        circ.add_gate(rz(0.4), q[2]); circ.add_gate(rz(0.6), q[2])
        circ.add_gate(z, q[1])
        circ.add_gate(barrier, q[0], q[2])
        circ.add_gate(z, q[1])
    elif choice == 3:
        # Circuit 3: 3-Qubit Quantum Interference State
        circ.add_gate(x, q[1]); circ.add_gate(h, q[0]); circ.add_gate(cx, q[0], q[2]); circ.add_gate(cx, q[0], q[1])
        circ.add_gate(h, q[2]); circ.add_gate(h, q[2])
        circ.add_gate(x, q[2]); circ.add_gate(x, q[2])
        circ.add_gate(cx, q[2], q[0]); circ.add_gate(cx, q[2], q[0])
        circ.add_gate(s, q[1]); circ.add_gate(sdg, q[1])
        circ.add_gate(rx(0.3), q[0]); circ.add_gate(rx(0.5), q[0])
        circ.add_gate(z, q[1])
        circ.add_gate(barrier, q[0], q[2])
        circ.add_gate(z, q[1])

    for i in range(3):
        circ.add_gate(measure, q[i], c[i])
    return circ

def main():
    print("=" * 80)
    print("      QC-C3-03: QUANTUM CIRCUIT OPTIMIZER VERIFICATION")
    print("=" * 80)
    print("QSDK Environment:", adapter.qsdk_description())

    all_passes = [
        'remove_identity',
        'cancel_self_inverse',
        'cancel_cx',
        'cancel_extended_self_inverse',
        'cancel_inverse_pairs',
        'merge_rotations',
    ]

    # 1. Benchmark Suite Optimization
    print("\n--- 1. Multi-Circuit Benchmark Optimization ---")
    for choice in (1, 2, 3):
        print(f"\n[Evaluating Benchmark Circuit #{choice}]")
        qc = build_circuit(choice)
        qasm_before = qc.qasm()
        
        prof_before = profile(qc)
        res_opt = optimize(qc, passes=all_passes, fixed_point=True)
        
        print(f"  Gate count reduction : {res_opt.before.total_gates} -> {res_opt.after.total_gates} ({res_opt.reduction_percentage}%)")
        print(f"  Circuit depth reduction: {res_opt.before.depth} -> {res_opt.after.depth} ({res_opt.depth_reduction_percentage}%)")
        
        # Guardrail checks
        z_count = res_opt.after.gate_counts.get("z", 0)
        assert z_count == 2, f"Barrier failed: expected 2 Z gates, got {z_count}"
        print(f"  Barrier Guardrail      : PASSED (both {z_count} Z gates retained)")

        # Fidelity
        fid = unitary_fidelity(from_qniverse(qc), res_opt.ir)
        assert fid > 1 - 1e-9, f"Fidelity check failed: {fid}"
        print(f"  Mathematical Fidelity  : {fid:.8f} (verdict: {res_opt.equivalence_verified})")

        # Immutability
        assert qc.qasm() == qasm_before, "Input circuit was modified in place!"
        assert res_opt.circuit is not qc, "Output is the same object as input!"
        print("  Functional Immutability: PASSED")

        # 1024-shot simulation
        unopt_counts, _ = simulate_circuit(qc, shots=1024)
        opt_counts, _ = simulate_circuit(res_opt.circuit, shots=1024)
        def _dist(counts):
            tot = sum(counts.values()) or 1.0
            return {k: v / tot for k, v in counts.items()}
        tvd = total_variation_distance(_dist(unopt_counts), _dist(opt_counts))
        print(f"  Unoptimized Counts     : {dict(sorted(unopt_counts.items()))}")
        print(f"  Optimized Counts       : {dict(sorted(opt_counts.items()))}")
        print(f"  Total Variation Dist   : {tvd:.4f} (Sampling noise check: {'PASS' if tvd < 0.05 else 'FAIL'})")
        assert tvd < 0.05, f"Distribution TVD {tvd} exceeded sampling threshold"

    # 2. Discrete Rewrite Rule Verifications
    print("\n--- 2. Discrete Rewrite Rule Test Suite (Tests A - F) ---")
    
    # Test A: Identity and Zero Rotations
    q_test = QuantumRegister(2, 'q'); qc_a = QniverseCircuit(); qc_a.add_register(q_test)
    qc_a.add_gate(id, q_test[0]); qc_a.add_gate(rx(0.0), q_test[1]); qc_a.add_gate(rz(2.0 * np.pi), q_test[1])
    res_a = optimize(qc_a, passes=["remove_identity"])
    assert res_a.after.total_gates == 0
    print("  [Test A: remove_identity] PASS (3 identity gates -> 0)")

    # Test B: Self-Inverse Cancellation
    qc_b = QniverseCircuit(); qc_b.add_register(q_test)
    qc_b.add_gate(h, q_test[0]); qc_b.add_gate(h, q_test[0]); qc_b.add_gate(x, q_test[1]); qc_b.add_gate(x, q_test[1])
    res_b = optimize(qc_b, passes=["cancel_self_inverse"])
    assert res_b.after.total_gates == 0
    print("  [Test B: cancel_self_inverse] PASS (4 gates -> 0)")

    # Test C: Consecutive CX Cancellation
    qc_c = QniverseCircuit(); qc_c.add_register(q_test)
    qc_c.add_gate(cx, q_test[0], q_test[1]); qc_c.add_gate(cx, q_test[0], q_test[1])
    res_c = optimize(qc_c, passes=["cancel_cx"])
    assert res_c.after.total_gates == 0
    print("  [Test C: cancel_cx] PASS (2 CX gates -> 0)")

    # Test D: Extended Self-Inverse
    qc_d = QniverseCircuit(); qc_d.add_register(q_test)
    qc_d.add_gate(swap, q_test[0], q_test[1]); qc_d.add_gate(swap, q_test[0], q_test[1])
    qc_d.add_gate(cz, q_test[0], q_test[1]); qc_d.add_gate(cz, q_test[0], q_test[1])
    res_d = optimize(qc_d, passes=["cancel_extended_self_inverse"])
    assert res_d.after.total_gates == 0
    print("  [Test D: cancel_extended_self_inverse] PASS (SWAP+CZ -> 0)")

    # Test E: Adjoint Pairs
    qc_e = QniverseCircuit(); qc_e.add_register(q_test)
    qc_e.add_gate(s, q_test[0]); qc_e.add_gate(sdg, q_test[0]); qc_e.add_gate(t, q_test[1]); qc_e.add_gate(tdg, q_test[1])
    res_e = optimize(qc_e, passes=["cancel_inverse_pairs"])
    assert res_e.after.total_gates == 0
    print("  [Test E: cancel_inverse_pairs] PASS (S/Sdg and T/Tdg -> 0)")

    # Test F: Continuous Rotation Merging
    qc_f = QniverseCircuit(); qc_f.add_register(q_test)
    qc_f.add_gate(rx(0.25 * np.pi), q_test[0]); qc_f.add_gate(rx(0.75 * np.pi), q_test[0])
    res_f = optimize(qc_f, passes=["merge_rotations"])
    assert res_f.after.total_gates == 1
    print("  [Test F: merge_rotations] PASS (Rx(pi/4) + Rx(3pi/4) -> Rx(pi))")

    # 3. 4-Qubit Benchmark
    print("\n--- 3. 4-Qubit Algorithmic Benchmark ---")
    q4 = QuantumRegister(4, 'q'); c4 = ClassicalRegister(4, 'c')
    qc_bench = QniverseCircuit(); qc_bench.add_register(q4); qc_bench.add_register(c4)
    for i in range(4):
        qc_bench.add_gate(h, q4[i]); qc_bench.add_gate(h, q4[i]); qc_bench.add_gate(x, q4[i])
    qc_bench.add_gate(cx, q4[0], q4[1]); qc_bench.add_gate(cx, q4[0], q4[1])
    qc_bench.add_gate(cx, q4[2], q4[3]); qc_bench.add_gate(cx, q4[2], q4[3])
    qc_bench.add_gate(s, q4[0]); qc_bench.add_gate(sdg, q4[0])
    qc_bench.add_gate(t, q4[1]); qc_bench.add_gate(tdg, q4[1])
    qc_bench.add_gate(rz(np.pi / 4), q4[2]); qc_bench.add_gate(rz(np.pi / 4), q4[2])
    qc_bench.add_gate(cx, q4[0], q4[1]); qc_bench.add_gate(cx, q4[1], q4[2]); qc_bench.add_gate(cx, q4[2], q4[3])
    for i in range(4): qc_bench.add_gate(measure, q4[i], c4[i])

    res_bench = optimize(qc_bench, passes=all_passes, fixed_point=True)
    print(f"  4-Qubit Gate reduction : {res_bench.before.total_gates} -> {res_bench.after.total_gates} ({res_bench.reduction_percentage}%)")
    fid_4q = unitary_fidelity(from_qniverse(qc_bench), res_bench.ir)
    print(f"  4-Qubit Unitary Fidelity: {fid_4q:.8f}")
    assert fid_4q > 1 - 1e-9
    assert res_bench.reduction_percentage > 50.0
    print("  [PASS] 4-Qubit algorithmic benchmark verified.")

    print("\n" + "=" * 80)
    print(">>> VERDICT: ALL QC-C3-03 CHECKS PASSED SUCCESSFULLY! <<<")
    print("=" * 80)

if __name__ == "__main__":
    main()
