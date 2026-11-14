"""
qnvkit.metrics: Depth calculation and circuit profiling shared by C1-01 and C3-03.
Implements the exact earliest-available-layer schedule specified in the hackathon guidelines.
"""

from collections import Counter
from typing import Dict, Any, Union
from qnvkit.ir import CircuitIR, Op
from qnvkit.report import ProfileReport


def calculate_scheduled_depth(ir: CircuitIR) -> int:
    """
    Calculates circuit depth using an earliest-available-layer schedule:
    - Each unitary operation occupies 1 layer on all operand qubits simultaneously.
    - Measure and reset take 1 layer on their touched qubits and classical bits.
    - Barrier takes 0 layers but aligns (synchronizes) all touched qubits to max(current_layer).
    - Operations on disjoint qubits execute in parallel on the earliest available layer.
    """
    if ir.num_qubits == 0:
        return 0

    qubit_layers = [0] * ir.num_qubits
    clbit_layers = [0] * ir.num_clbits if ir.num_clbits > 0 else []

    for op in ir.ops:
        if op.name == "barrier":
            if op.qubits:
                barrier_layer = max(qubit_layers[q] for q in op.qubits)
                for q in op.qubits:
                    qubit_layers[q] = barrier_layer
        elif op.name == "measure":
            # Touches both qubits and classical bits
            req = [qubit_layers[q] for q in op.qubits]
            if op.clbits and clbit_layers:
                req.extend(clbit_layers[c] for c in op.clbits if c < len(clbit_layers))
            start = max(req) if req else 0
            next_l = start + 1
            for q in op.qubits:
                qubit_layers[q] = next_l
            if op.clbits and clbit_layers:
                for c in op.clbits:
                    if c < len(clbit_layers):
                        clbit_layers[c] = next_l
        elif op.name == "reset":
            start = max(qubit_layers[q] for q in op.qubits) if op.qubits else 0
            next_l = start + 1
            for q in op.qubits:
                qubit_layers[q] = next_l
        else:
            # Unitary gate
            start = max(qubit_layers[q] for q in op.qubits) if op.qubits else 0
            next_l = start + 1
            for q in op.qubits:
                qubit_layers[q] = next_l

    return max(qubit_layers) if qubit_layers else 0


def profile(circuit: Union[Any, CircuitIR]) -> ProfileReport:
    """
    Generates a structured ProfileReport for a QniverseCircuit or CircuitIR.
    """
    # If passed a QniverseCircuit, convert via adapter
    if not isinstance(circuit, CircuitIR):
        from qnvkit.qsdk_adapter import from_qniverse
        ir = from_qniverse(circuit)
    else:
        ir = circuit

    counts = Counter(op.name for op in ir.ops)
    active_qubits = set()
    single_q = 0
    two_q = 0
    multi_q = 0
    meas = counts.get("measure", 0)
    resets = counts.get("reset", 0)
    barriers = counts.get("barrier", 0)

    for op in ir.ops:
        active_qubits.update(op.qubits)
        if op.name in ("barrier", "measure", "reset"):
            continue
        arity = len(op.qubits)
        if arity == 1:
            single_q += 1
        elif arity == 2:
            two_q += 1
        elif arity > 2:
            multi_q += 1

    total_unitary_gates = single_q + two_q + multi_q
    depth = calculate_scheduled_depth(ir)

    return ProfileReport(
        total_gates=total_unitary_gates,
        gate_counts=dict(sorted(counts.items())),
        qubits_declared=ir.num_qubits,
        qubits_used=len(active_qubits),
        single_qubit_gates=single_q,
        two_qubit_gates=two_q,
        multi_qubit_gates=multi_q,
        depth=depth,
        measurements=meas,
        resets=resets,
        barriers=barriers,
    )
