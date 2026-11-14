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


def draw_circuit(circuit: Any, output: Optional[str] = None) -> Any:
    """
    Renders a circuit diagram using Qiskit qc.draw() (graphical image where supported).

    Parameters:
      circuit: QniverseCircuit, CircuitIR, or OpenQASM string.
      output: 'mpl' for matplotlib image, 'text' for Unicode box-drawing, or None (auto-detect).

    Returns:
      Matplotlib Figure (if mpl), TextDrawing, or string representation.
    """
    if hasattr(circuit, "draw") and callable(circuit.draw):
        try:
            return circuit.draw(output=output)
        except Exception:
            pass

    try:
        from qiskit import QuantumCircuit
        qasm_str = to_qasm2_str(circuit)
        qc = QuantumCircuit.from_qasm_str(qasm_str)
        try:
            drawn = qc.draw(output=output or "mpl")
        except Exception:
            drawn = qc.draw(output=output or "text")
        try:
            from IPython.display import display
            display(drawn)
        except Exception:
            print(drawn)
        return drawn
    except Exception:
        text = to_qasm2_str(circuit).strip()
        try:
            from IPython.display import display
            display(text)
        except Exception:
            print(text)
        return text


def _simulate_numpy(ir: CircuitIR, shots: int = 1024) -> Tuple[Dict[str, int], str]:
    """Pure-NumPy reference execution (handles mid-circuit measurement, reset and conditions)."""
    from qnvkit.sim import sample_counts
    return sample_counts(ir, shots=shots), "qnvkit Builtin Simulator (pure NumPy)"


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
