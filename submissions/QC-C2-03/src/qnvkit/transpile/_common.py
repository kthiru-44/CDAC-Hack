"""
Shared helpers for the code generators: operand formatting, condition terms,
gate fallback through the C1 decomposer, and safe Python identifiers.
"""

from __future__ import annotations
import keyword
from typing import Dict, Iterable, List, Optional, Set, Tuple

from qnvkit.ir import CircuitIR, Condition, Op
from qnvkit.report import TranspilerReport

NON_UNITARY = {"measure", "reset", "barrier"}

# Names used by generated code; a register may not take them.
RESERVED = {
    "qc", "np", "circuit", "cirq", "cudaq", "sympy", "build_circuit", "numpy", "qiskit",
    "result", "result_bits", "counts", "sim", "KERNEL", "SHOTS", "CLBIT_KEYS", "NUM_CLBITS",
    "QniverseCircuit", "QuantumRegister", "ClassicalRegister", "QuantumCircuit", "Statevector",
}


def py_name(name: str) -> str:
    """A register name that is a safe Python identifier in generated code."""
    out = "".join(ch if (ch.isalnum() or ch == "_") else "_" for ch in name) or "r"
    if out[0].isdigit():
        out = "r_" + out
    if keyword.iskeyword(out) or out in RESERVED or out.startswith("__"):
        out = out + "_"
    return out


def fmt_param(p: float) -> str:
    return repr(float(p))


def qubit_names(circuit: CircuitIR) -> Dict[int, str]:
    return {i: "%s[%d]" % (py_name(r), k) for i, (r, k) in circuit.get_qubit_reg_map().items()}


def clbit_names(circuit: CircuitIR) -> Dict[int, str]:
    return {i: "%s[%d]" % (py_name(r), k) for i, (r, k) in circuit.get_clbit_reg_map().items()}


def clbit_keys(circuit: CircuitIR) -> Dict[int, str]:
    """Flat classical bit -> per-bit key/variable name such as ``c_0``."""
    return {i: "%s_%d" % (r, k) for i, (r, k) in circuit.get_clbit_reg_map().items()}


def _creg_range(circuit: CircuitIR, name: str) -> Tuple[int, int]:
    off = 0
    for r in circuit.cregs:
        if r.name == name:
            return off, r.size
        off += r.size
    raise KeyError(name)


def condition_terms(circuit: CircuitIR, op: Op) -> List[Tuple[int, int]]:
    """``[(flat_clbit, required_bit), ...]``: the bits that must all match for the op to run."""
    cond = op.condition
    if not cond:
        return []
    if isinstance(cond, Condition):
        reg, value, index = cond.register, cond.value, cond.index
    else:
        reg, value = cond[0], cond[1]
        index = None
    off, size = _creg_range(circuit, reg)
    if index is not None:
        return [(off + index, value & 1)]
    return [(off + i, (value >> i) & 1) for i in range(size)]


def prepare_ops(
    circuit: CircuitIR,
    native_gates: Iterable[str],
    fallback_basis: Iterable[str],
    report: TranspilerReport,
    target_label: str,
) -> List[Op]:
    """
    The op list for one target. Gates outside ``native_gates`` are rewritten with the C1
    decomposer into ``native_gates | fallback_basis``; a gate that cannot be rewritten is
    reported (with line and column) and skipped.
    """
    from qnvkit.decompose.decomposer import _expand_op_recursive

    native: Set[str] = set(native_gates)
    basis = native | set(fallback_basis)
    out: List[Op] = []
    noted: Set[str] = set()
    for op in circuit.ops:
        if op.name in NON_UNITARY or op.name in native:
            out.append(op)
            continue
        try:
            expanded = _expand_op_recursive(op, basis)
        except Exception:
            expanded = None
        if expanded is None:
            report.add_unsupported(
                "Gate '%s' has no native form in %s and could not be decomposed" % (op.name, target_label),
                op.line, op.col)
            continue
        if op.name not in noted:
            noted.add(op.name)
            report.add_note("'%s' is not native in %s; rewritten with the C1 decomposer into %s "
                            "(equal up to global phase)" % (op.name, target_label, sorted({o.name for o in expanded})))
        out.extend(expanded)
    return out


def gate_counts(circuit: CircuitIR) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for op in circuit.ops:
        counts[op.name] = counts.get(op.name, 0) + 1
    return counts


def set_metrics(report: TranspilerReport, circuit: CircuitIR) -> None:
    report.metrics = {
        "num_qubits": circuit.num_qubits,
        "num_clbits": circuit.num_clbits,
        "total_ops": len(circuit.ops),
        "gate_counts": gate_counts(circuit),
    }
    for r in circuit.qregs:
        report.qubit_mapping[r.name] = r.size
    for c in circuit.cregs:
        report.clbit_mapping[c.name] = c.size
