"""
qnvkit.qsdk_adapter: The ONLY file in the repository that imports Qniverse.
Provides seamless, bidirectional, non-mutating translation between QniverseCircuit and CircuitIR.
"""

from typing import Any, Tuple, Optional
from qnvkit.ir import CircuitIR, Register, Op
from qnvkit.qasm.parser2 import parse_qasm2

# Safe import of Qniverse (platform live vs local shim)
try:
    from Qniverse.QniverseCircuit import QniverseCircuit, QuantumRegister, ClassicalRegister
    IS_LIVE_QNIVERSE = True
except ImportError:
    from qnvkit.shim.Qniverse.QniverseCircuit import QniverseCircuit, QuantumRegister, ClassicalRegister
    IS_LIVE_QNIVERSE = False


def from_qniverse(qc: Any) -> CircuitIR:
    """
    Ingests a QniverseCircuit and returns an immutable CircuitIR.
    Reads circuit operations strictly through qc.qasm() without mutating the input object.
    """
    if qc is None:
        raise ValueError("Input circuit cannot be None.")
    if not hasattr(qc, "qasm"):
        raise TypeError(f"Expected circuit with .qasm() export method, got {type(qc)}.")

    qasm_str = qc.qasm()
    if not qasm_str or not isinstance(qasm_str, str):
        raise ValueError("qc.qasm() returned an empty or invalid QASM string.")

    return parse_qasm2(qasm_str)


def to_qniverse(ir: CircuitIR) -> Any:
    """
    Constructs and returns a brand-new QniverseCircuit from CircuitIR
    using only documented QSDK calls: add_register, add_gate, add_conditional_gate.
    """
    if ir is None:
        raise ValueError("CircuitIR cannot be None.")

    qc = QniverseCircuit()

    # Add Quantum Registers
    for qr in ir.qregs:
        qc.add_register(QuantumRegister(qr.size, qr.name))

    # Add Classical Registers
    for cr in ir.cregs:
        qc.add_register(ClassicalRegister(cr.size, cr.name))

    # Wire mapping (0-indexed global -> local register)
    q_map = ir.get_qubit_reg_map()
    c_map = ir.get_clbit_reg_map()

    for op in ir.ops:
        if op.condition:
            cname, cval = op.condition
            # Find the creg object or name
            qc.add_conditional_gate(cname, cval, op.name, *op.qubits)
            continue

        if op.name == "measure":
            # For each qubit/clbit pair
            for q_idx, c_idx in zip(op.qubits, op.clbits):
                # Use measure gate or measure_all
                qc.add_gate("measure", q_idx, c_idx)
        elif op.name == "barrier":
            qc.add_gate("barrier", *op.qubits)
        elif op.name == "reset":
            for q in op.qubits:
                qc.add_gate("reset", q)
        else:
            if op.params:
                qc.add_gate(op.name, *op.qubits, params=list(op.params))
            else:
                qc.add_gate(op.name, *op.qubits)

    return qc
