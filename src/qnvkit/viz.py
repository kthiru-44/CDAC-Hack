"""
qnvkit.viz: Circuit visualization and local simulation execution helpers.

Provides:
- `draw_circuit(circuit)`: Renders text/Unicode box-drawing circuit diagrams.
  Uses Qiskit drawer if available; falls back to built-in ASCII renderer.
- `simulate_circuit(circuit, shots=1024)`: Runs simulation locally using Qiskit
  AerSimulator (if available), Qiskit BasicSimulator fallback, or qnvkit's
  built-in pure-NumPy statevector engine. Zero external dependencies required.
"""

from typing import Any, Dict, Tuple, Optional
from qnvkit.ir import CircuitIR


def to_ir(circuit: Any) -> CircuitIR:
    """Converts a QniverseCircuit, CircuitIR, or OpenQASM 2/3 string into CircuitIR."""
    if isinstance(circuit, CircuitIR):
        return circuit
    if isinstance(circuit, str):
        if "OPENQASM 3" in circuit or "qubit[" in circuit:
            from qnvkit.qasm.parser3 import parse_qasm3
            return parse_qasm3(circuit)
        from qnvkit.qasm.parser2 import parse_qasm2
        return parse_qasm2(circuit)
    if hasattr(circuit, "qasm") and callable(circuit.qasm):
        try:
            from qnvkit.qsdk_adapter import from_qniverse
            return from_qniverse(circuit)
        except Exception:
            from qnvkit.qasm.parser2 import parse_qasm2
            return parse_qasm2(circuit.qasm())
    raise TypeError(f"Cannot convert object of type {type(circuit)} to CircuitIR.")


def to_qasm2_str(circuit: Any) -> str:
    """Converts a QniverseCircuit, CircuitIR, or OpenQASM 2/3 string into OpenQASM 2.0 text."""
    if hasattr(circuit, "qasm") and callable(circuit.qasm):
        return circuit.qasm()
    if isinstance(circuit, str) and "OPENQASM 2" in circuit:
        return circuit
    ir = to_ir(circuit)
    from qnvkit.qasm.emit import emit_qasm2
    return emit_qasm2(ir)


def _draw_ascii_circuit(ir: CircuitIR) -> str:
    """Built-in pure-Python ASCII circuit diagram generator (zero dependencies)."""
    n = ir.num_qubits
    if n == 0:
        return "(empty circuit)"
    lines = [f"q_{i}: ─" for i in range(n)]
    for op in ir.ops:
        name = op.name.upper()
        if op.name == "measure":
            q = op.qubits[0]
            for i in range(n):
                lines[i] += "─[M]─" if i == q else "─────"
        elif op.name == "barrier":
            for i in range(n):
                lines[i] += "──║──"
        elif len(op.qubits) == 1:
            q = op.qubits[0]
            label = f"[{name}]"
            w = len(label)
            for i in range(n):
                lines[i] += f"─{label}─" if i == q else "─" + "─" * w + "─"
        elif len(op.qubits) == 2 and op.name in ("cx", "cnot"):
            c, t = op.qubits[0], op.qubits[1]
            low, high = min(c, t), max(c, t)
            for i in range(n):
                if i == c:
                    lines[i] += "──●──"
                elif i == t:
                    lines[i] += "──X──"
                elif low < i < high:
                    lines[i] += "──┼──"
                else:
                    lines[i] += "─────"
        elif len(op.qubits) == 2 and op.name == "cz":
            c, t = op.qubits[0], op.qubits[1]
            low, high = min(c, t), max(c, t)
            for i in range(n):
                if i in (c, t):
                    lines[i] += "──●──"
                elif low < i < high:
                    lines[i] += "──┼──"
                else:
                    lines[i] += "─────"
        else:
            w = max(len(name) + 2, 5)
            pad = "─" * w
            for i in range(n):
                if i in op.qubits:
                    lines[i] += f"─[{name}]─"
                else:
                    lines[i] += f"─{pad}─"
    return "\n".join(lines)


def draw_circuit(circuit: Any, output: str = "text") -> str:
    """
    Renders a circuit diagram as a string.

    Parameters:
      circuit: QniverseCircuit, CircuitIR, or OpenQASM string.
      output: 'text' for Unicode/ASCII box-drawing diagram.

    Returns:
      String representation of the circuit diagram.
    """
    try:
        from qiskit import QuantumCircuit
        qasm_str = to_qasm2_str(circuit)
        qc = QuantumCircuit.from_qasm_str(qasm_str)
        return str(qc.draw(output=output))
    except Exception:
        pass

    try:
        ir = to_ir(circuit)
        return _draw_ascii_circuit(ir)
    except Exception:
        return to_qasm2_str(circuit).strip()


def _simulate_numpy(ir: CircuitIR, shots: int = 1024) -> Tuple[Dict[str, int], str]:
    """Pure-NumPy local statevector simulation and shot sampling."""
    import numpy as np
    from qnvkit.sim import compute_statevector

    sv = compute_statevector(ir)
    probs = np.abs(sv) ** 2
    prob_sum = float(np.sum(probs))
    if prob_sum > 0:
        probs = probs / prob_sum
    else:
        probs = np.ones_like(probs) / len(probs)

    rng = np.random.default_rng(1234)
    samples = rng.choice(len(probs), size=shots, p=probs)
    n = ir.num_qubits

    measures = [op for op in ir.ops if op.name == "measure"]
    counts: Dict[str, int] = {}
    if measures:
        num_clbits = max(ir.num_clbits, max((op.clbits[0] for op in measures), default=0) + 1)
        for s in samples:
            bits = ["0"] * num_clbits
            for op in measures:
                qubit_val = (int(s) >> op.qubits[0]) & 1
                bits[op.clbits[0]] = str(qubit_val)
            key = "".join(reversed(bits))
            counts[key] = counts.get(key, 0) + 1
    else:
        for s in samples:
            key = format(int(s), f"0{n}b")
            counts[key] = counts.get(key, 0) + 1

    return counts, "qnvkit Builtin Simulator (pure NumPy)"


def simulate_circuit(circuit: Any, shots: int = 1024) -> Tuple[Dict[str, int], str]:
    """
    Runs circuit simulation locally.

    Attempts Qiskit Aer / BasicSimulator first. If Qiskit is not installed,
    falls back cleanly to qnvkit's built-in pure-NumPy exact simulator.

    Parameters:
      circuit: QniverseCircuit, CircuitIR, or OpenQASM string.
      shots: Number of measurement shots (default: 1024).

    Returns:
      Tuple of (measurement_counts_dict, simulator_name_str).
    """
    try:
        from qiskit import QuantumCircuit
        try:
            from qiskit_aer import AerSimulator
            sim = AerSimulator()
            sim_name = "Qiskit AerSimulator"
        except ImportError:
            from qiskit.providers.basic_provider import BasicSimulator
            sim = BasicSimulator()
            sim_name = "Qiskit BasicSimulator (Aer fallback)"

        qasm_str = to_qasm2_str(circuit)
        qc = QuantumCircuit.from_qasm_str(qasm_str)

        has_meas = any(inst.operation.name == "measure" for inst in qc.data)
        if not has_meas:
            qc.measure_all()

        job = sim.run(qc, shots=shots)
        counts = dict(job.result().get_counts())
        return counts, sim_name
    except (ImportError, Exception):
        ir = to_ir(circuit)
        return _simulate_numpy(ir, shots=shots)
