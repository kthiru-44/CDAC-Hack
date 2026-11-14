"""
qnvkit.viz: Circuit visualization and local simulation execution helpers.

Provides:
- `draw_circuit(circuit)`: Renders text/Unicode box-drawing circuit diagrams.
- `simulate_circuit(circuit, shots=1024)`: Runs simulation locally using Qiskit
  AerSimulator (if available) or Qiskit BasicSimulator fallback.
"""

from typing import Any, Dict, Tuple, Optional
from qnvkit.ir import CircuitIR


def to_qasm2_str(circuit: Any) -> str:
    """Converts a QniverseCircuit, CircuitIR, or OpenQASM 2/3 string into OpenQASM 2.0 text."""
    if hasattr(circuit, "qasm") and callable(circuit.qasm):
        return circuit.qasm()
    if isinstance(circuit, CircuitIR):
        from qnvkit.qasm.emit import emit_qasm2
        return emit_qasm2(circuit)
    if isinstance(circuit, str):
        if "OPENQASM 3" in circuit or "qubit[" in circuit:
            from qnvkit.qasm.parser3 import parse_qasm3
            from qnvkit.qasm.emit import emit_qasm2
            return emit_qasm2(parse_qasm3(circuit))
        return circuit
    raise TypeError(f"Cannot convert object of type {type(circuit)} to OpenQASM.")


def draw_circuit(circuit: Any, output: str = "text") -> str:
    """
    Renders a circuit diagram as a string.

    Parameters:
      circuit: QniverseCircuit, CircuitIR, or OpenQASM string.
      output: 'text' for Unicode/ASCII box-drawing diagram.

    Returns:
      String representation of the circuit diagram.
    """
    qasm_str = to_qasm2_str(circuit)
    try:
        from qiskit import QuantumCircuit
        qc = QuantumCircuit.from_qasm_str(qasm_str)
        return str(qc.draw(output=output))
    except Exception:
        return qasm_str.strip()


def simulate_circuit(circuit: Any, shots: int = 1024) -> Tuple[Dict[str, int], str]:
    """
    Runs circuit simulation locally using Qiskit Aer (or BasicSimulator fallback).

    Parameters:
      circuit: QniverseCircuit, CircuitIR, or OpenQASM string.
      shots: Number of measurement shots (default: 1024).

    Returns:
      Tuple of (measurement_counts_dict, simulator_name_str).
    """
    qasm_str = to_qasm2_str(circuit)
    from qiskit import QuantumCircuit

    try:
        from qiskit_aer import AerSimulator
        sim = AerSimulator()
        sim_name = "Qiskit AerSimulator"
    except ImportError:
        from qiskit.providers.basic_provider import BasicSimulator
        sim = BasicSimulator()
        sim_name = "Qiskit BasicSimulator (Aer fallback)"

    qc = QuantumCircuit.from_qasm_str(qasm_str)

    # Ensure measurements exist; if not, measure all qubits
    has_meas = any(inst.operation.name == "measure" for inst in qc.data)
    if not has_meas:
        qc.measure_all()

    job = sim.run(qc, shots=shots)
    counts = dict(job.result().get_counts())
    return counts, sim_name
