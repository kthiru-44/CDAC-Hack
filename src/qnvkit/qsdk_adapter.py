"""
qnvkit.qsdk_adapter: the single place where qnvkit talks to the Qniverse QSDK.

Only documented QSDK calls are used:
    QniverseCircuit(), QuantumRegister(n, name), ClassicalRegister(n, name),
    qc.add_register(reg), qc.add_gate(gate_object, *bit_objects),
    qc.add_conditional_gate(creg, value, gate_object, *qubits), qc.qasm()

Reading a circuit goes through qc.qasm() only, so the input object is never mutated.

The real QSDK is available inside Qniverse JupyterLab (it is not on PyPI). When
``import Qniverse`` fails, a local stand-in that implements the same documented calls is
put on sys.path, so the same code runs in both places. ``IS_LIVE_QNIVERSE`` tells which.
"""

import contextlib
import io
import os
import sys
from typing import Any

from qnvkit.ir import CircuitIR
from qnvkit.qasm.parser2 import parse_qasm2

import importlib

_SUBMODULES = ("QniverseCircuit", "gates", "backend", "api", "module", "transpile")


def _load_official_qsdk():
    """
    Imports the official QSDK. The documentation spells the package both `Qniverse` and
    `qniverse`; on Linux these differ, so both are tried. A lowercase install is aliased as
    `Qniverse` (including submodules) so the rest of qnvkit always imports `Qniverse.*`.
    Returns the name that worked, or None.
    """
    for top in ("Qniverse", "qniverse"):
        try:
            pkg = importlib.import_module(top)
        except ImportError:
            continue
        if top != "Qniverse":
            sys.modules["Qniverse"] = pkg
            for sub in _SUBMODULES:
                for cand in (sub, sub.lower(), sub[0].lower() + sub[1:]):
                    try:
                        mod = importlib.import_module("%s.%s" % (top, cand))
                    except ImportError:
                        continue
                    sys.modules["Qniverse." + sub] = mod
                    break
        return top
    return None


QSDK_IMPORT_NAME = _load_official_qsdk()
if QSDK_IMPORT_NAME is None:
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "shim"))
    import Qniverse  # noqa: F401  (local stand-in)
else:
    import Qniverse  # noqa: F401

IS_LIVE_QNIVERSE = not getattr(Qniverse, "IS_LOCAL_STAND_IN", False)

from Qniverse.QniverseCircuit import QniverseCircuit, QuantumRegister, ClassicalRegister  # noqa: E402
import Qniverse.gates as _qgates  # noqa: E402


def _qniverse_circuit_draw(self, *args, **kwargs):
    """
    Renders visual diagram for QniverseCircuit using Qiskit or native QSDK drawer.
    Accepts all QSDK arguments (including silent=True, filename, etc.) without error.
    """
    orig = getattr(self, "_orig_draw", None)
    # Always call official QSDK draw if available to generate self._svg_cache needed for run()
    if callable(orig):
        try:
            res = orig(*args, **kwargs)
            if kwargs.get("silent", False):
                return res
        except Exception:
            pass

    # When called with silent=True (internal to Qniverse run()), do not print anything
    if kwargs.get("silent", False):
        return None

    target_file = kwargs.get("filename") or (args[0] if args and isinstance(args[0], str) else None)
    if target_file and any(target_file.endswith(ext) for ext in (".svg", ".png", ".pdf", ".jpg")):
        if callable(orig):
            try:
                return orig(target_file)
            except Exception:
                pass

    out_fmt = kwargs.get("output", None)
    try:
        from qiskit import QuantumCircuit as QC
        qasm_text = read_qasm(self)
        qc_qk = QC.from_qasm_str(qasm_text)
        try:
            drawn = qc_qk.draw(output=out_fmt or "mpl")
        except Exception:
            drawn = qc_qk.draw(output=out_fmt or "text")
        try:
            from IPython.display import display
            display(drawn)
        except Exception:
            print(drawn)
        return drawn
    except Exception:
        qasm_text = read_qasm(self)
        try:
            from IPython.display import display
            display(qasm_text)
        except Exception:
            print(qasm_text)
        return qasm_text


if not hasattr(QniverseCircuit, "_orig_draw"):
    QniverseCircuit._orig_draw = getattr(QniverseCircuit, "draw", None)
    QniverseCircuit.draw = _qniverse_circuit_draw


def qsdk_description() -> str:
    if IS_LIVE_QNIVERSE:
        return "official Qniverse QSDK (imported as '%s')" % QSDK_IMPORT_NAME
    return "LOCAL STAND-IN for the QSDK (official package not installed here)"


def _gate_object(name: str, params=()):
    """Returns the documented QSDK gate object, e.g. h, or rx(theta) for parameterised gates."""
    try:
        gate = getattr(_qgates, name)
    except AttributeError:
        raise ValueError("Gate '%s' is not provided by Qniverse.gates." % name)
    if params:
        gate = gate(*[float(p) for p in params])
    return gate


def read_qasm(qc: Any) -> str:
    """Returns the OpenQASM 2.0 text of a QniverseCircuit via the documented qc.qasm()."""
    if qc is None:
        raise ValueError("Input circuit cannot be None.")
    if not callable(getattr(qc, "qasm", None)):
        raise TypeError("Expected a QniverseCircuit (object with a qasm() method), got %s." % type(qc).__name__)
    # qc.qasm() may return the text or print it, depending on the SDK version: handle both.
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            text = qc.qasm()
        except TypeError:
            text = qc.qasm(1)  # some SDK versions require the `shots` argument
    if not isinstance(text, str) or "OPENQASM" not in text:
        text = buf.getvalue()
    if not isinstance(text, str) or "OPENQASM" not in text:
        raise ValueError("qc.qasm() did not produce OpenQASM text; the circuit is missing or malformed.")
    return text


def from_qniverse(qc: Any) -> CircuitIR:
    """Reads a QniverseCircuit into an immutable CircuitIR (input is not modified)."""
    return parse_qasm2(read_qasm(qc))


def unrepresentable_barriers(ir: CircuitIR) -> int:
    """Number of barrier ops whose wires cannot be represented in QSDK (e.g. < 2 qubits per register)."""
    count = 0
    reg_map = ir.get_qubit_reg_map()
    for op in ir.ops:
        if op.name == "barrier":
            by_reg = {}
            for q in op.qubits:
                r_name = reg_map[q][0] if q in reg_map else "q"
                by_reg.setdefault(r_name, []).append(q)
            if not any(len(g) >= 2 for g in by_reg.values()):
                count += 1
    return count


def to_qniverse(ir: CircuitIR) -> Any:
    """Builds a brand-new QniverseCircuit from a CircuitIR using documented QSDK calls only."""
    if ir is None:
        raise ValueError("CircuitIR cannot be None.")

    qc = QniverseCircuit()
    qbits, cbits, cregs = [], [], {}
    for r in ir.qregs:
        reg = QuantumRegister(r.size, r.name)
        qc.add_register(reg)
        qbits.extend(reg[i] for i in range(r.size))
    for r in ir.cregs:
        reg = ClassicalRegister(r.size, r.name)
        qc.add_register(reg)
        cregs[r.name] = reg
        cbits.extend(reg[i] for i in range(r.size))

    reg_map = ir.get_qubit_reg_map()
    for op in ir.ops:
        qs = [qbits[q] for q in op.qubits]
        if op.name == "measure":
            for q, c in zip(op.qubits, op.clbits):
                qc.add_gate(_gate_object("measure"), qbits[q], cbits[c])
        elif op.name == "reset":
            for q in qs:
                qc.add_gate(_gate_object("reset"), q)
        elif op.name == "barrier":
            # The official SDK (qniverse 1.0.6) raises "Barrier requires at least two qubits" in
            # qc.qasm() for a one-qubit barrier, so such barriers cannot be represented. A barrier
            # has no effect on the unitary; it is omitted here (the IR keeps it, see unrepresentable_barriers).
            # add_gate accepts a barrier with exactly two qubits: the start and end of a span within a register.
            by_reg = {}
            for q in op.qubits:
                r_name = reg_map[q][0] if q in reg_map else "q"
                by_reg.setdefault(r_name, []).append(q)
            for r_name, group in by_reg.items():
                if len(group) >= 2:
                    qc.add_gate(_gate_object("barrier"), qbits[min(group)], qbits[max(group)])
        elif op.condition:
            if not isinstance(op.condition, tuple):
                raise ValueError("The QSDK only supports register-level conditions, got %r." % (op.condition,))
            cname, cval = op.condition
            qc.add_conditional_gate(cregs[cname], int(cval), _gate_object(op.name, op.params), *qs)
        else:
            qc.add_gate(_gate_object(op.name, op.params), *qs)
    return qc
