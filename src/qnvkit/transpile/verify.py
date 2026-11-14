"""
Cross-framework equivalence verifier.

Static circuits (no condition, no reset, nothing after a measurement on the same qubit):
the generated code is executed and its state vector compared with the reference simulator
(fidelity). Dynamic circuits cannot be modelled by the reference simulator, so Qiskit (Aer),
Cirq and CUDA-Q are sampled with a fixed seed and the count distributions are compared
pairwise (total variation distance). A framework that is missing, or a check that was not
run, is reported with ``executed: False`` and a reason; nothing is claimed that did not run.
"""

from __future__ import annotations
import atexit
import dataclasses
import importlib.util
import itertools
import os
import shutil
import tempfile
from typing import Any, Dict, List, Optional

import numpy as np

from qnvkit.ir import CircuitIR, Op, Register
from qnvkit.sim import compute_statevector, convert_statevector_endianness, total_variation_distance
from qnvkit.transpile.qiskit_gen import generate_qiskit_code
from qnvkit.transpile.cirq_gen import generate_cirq_code
from qnvkit.transpile.cudaq_gen import generate_cudaq_code
from qnvkit.transpile.qniverse_gen import generate_qniverse_code

try:
    import qiskit
    from qiskit.quantum_info import Statevector as QiskitStatevector
    HAS_QISKIT = True
except ImportError:
    HAS_QISKIT = False

try:
    import qiskit_aer
    HAS_AER = True
except ImportError:
    HAS_AER = False

try:
    import cirq
    HAS_CIRQ = True
except ImportError:
    HAS_CIRQ = False

try:
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import cudaq
    HAS_CUDAQ = True
except Exception:
    HAS_CUDAQ = False

SHOTS = 4000
TVD_TOLERANCE = 0.05
SEED = 1234
BIT_ORDER_NOTE = "bitstrings cover all classical bits, classical bit 0 right-most"

_TMP_DIRS: List[str] = []
atexit.register(lambda: [shutil.rmtree(d, ignore_errors=True) for d in _TMP_DIRS])


def load_generated_module(code: str, tag: str = "generated"):
    """Imports generated code from a real file (CUDA-Q kernels need their source file)."""
    d = tempfile.mkdtemp(prefix="qnvkit_gen_")
    _TMP_DIRS.append(d)
    path = os.path.join(d, "%s.py" % tag)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(code)
    spec = importlib.util.spec_from_file_location("qnvkit_gen_%s_%d" % (tag, len(_TMP_DIRS)), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def is_static(circuit: CircuitIR) -> bool:
    """True when the circuit is unitary up to final measurements."""
    measured = set()
    for op in circuit.ops:
        if op.condition or op.name == "reset":
            return False
        if op.name == "measure":
            measured.add(op.qubits[0])
        elif op.name != "barrier" and any(q in measured for q in op.qubits):
            return False
    return True


def _strip_measurements(circuit: CircuitIR) -> CircuitIR:
    return dataclasses.replace(circuit, ops=tuple(o for o in circuit.ops if o.name != "measure"))


def _with_measure_all(circuit: CircuitIR) -> CircuitIR:
    if circuit.num_clbits:
        return circuit
    ops = tuple(circuit.ops) + tuple(
        Op("measure", qubits=(i,), clbits=(i,)) for i in range(circuit.num_qubits))
    return dataclasses.replace(
        circuit, num_clbits=circuit.num_qubits,
        cregs=(Register("m", circuit.num_qubits, is_classical=True),), ops=ops)


def _fid(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.abs(np.vdot(a, b)) ** 2)


def _normalise(counts: Dict[str, int]) -> Dict[str, float]:
    total = float(sum(counts.values())) or 1.0
    return {k: v / total for k, v in counts.items()}


# ---------------------------------------------------------------- static: state vectors
def _state_qiskit(circuit: CircuitIR) -> np.ndarray:
    ns: Dict[str, Any] = {}
    exec(generate_qiskit_code(circuit).code, ns)
    return np.array(QiskitStatevector(ns["build_circuit"]()))


def _state_cirq(circuit: CircuitIR) -> np.ndarray:
    ns: Dict[str, Any] = {}
    exec(generate_cirq_code(circuit).code, ns)
    c = ns["build_circuit"]()
    order = [cirq.NamedQubit("%s_%d" % (r.name, i)) for r in circuit.qregs for i in range(r.size)]
    sv = cirq.Simulator(dtype=np.complex128).simulate(c, qubit_order=order).final_state_vector
    return convert_statevector_endianness(np.array(sv), circuit.num_qubits)  # cirq: first qubit is MSB


def _cudaq_is_little_endian() -> bool:
    """One-gate calibration: x on qubit 0 of 2 gives index 1 when qubit 0 is the least significant bit."""
    mod = load_generated_module(
        "import cudaq\n\n@cudaq.kernel\ndef cal():\n    q = cudaq.qvector(2)\n    x(q[0])\n", "cal")
    return int(np.argmax(np.abs(np.array(cudaq.get_state(mod.cal))))) == 1


def _state_cudaq(circuit: CircuitIR):
    little = _cudaq_is_little_endian()
    mod = load_generated_module(generate_cudaq_code(circuit).code, "cudaq_static")
    sv = np.array(cudaq.get_state(mod.KERNEL))
    if not little:
        sv = convert_statevector_endianness(sv, circuit.num_qubits)
    return sv, little


def _state_qsdk(circuit: CircuitIR) -> np.ndarray:
    import qnvkit.qsdk_adapter as adapter
    res = generate_qniverse_code(circuit)
    if res.report.unsupported_constructs:
        raise RuntimeError("generator reported unsupported constructs: %s" % res.report.unsupported_constructs[0]["construct"])
    ns: Dict[str, Any] = {}
    exec(res.code, ns)
    return compute_statevector(adapter.from_qniverse(ns["build_circuit"]()))


# ---------------------------------------------------------------- dynamic: sampling
def _counts_qiskit(circuit: CircuitIR) -> Dict[str, int]:
    from qiskit import transpile as qk_transpile
    from qiskit_aer import AerSimulator
    ns: Dict[str, Any] = {}
    exec(generate_qiskit_code(circuit).code, ns)
    qc = ns["build_circuit"]()
    sim = AerSimulator(seed_simulator=SEED)
    counts = sim.run(qk_transpile(qc, sim), shots=SHOTS).result().get_counts()
    out: Dict[str, int] = {}
    for k, v in counts.items():
        out[k.replace(" ", "")] = out.get(k.replace(" ", ""), 0) + v
    return out


def _counts_cirq(circuit: CircuitIR) -> Dict[str, int]:
    ns: Dict[str, Any] = {}
    exec(generate_cirq_code(circuit).code, ns)
    c = ns["build_circuit"]()
    res = cirq.Simulator(seed=SEED).run(c, repetitions=SHOTS)
    out: Dict[str, int] = {}
    for s in range(SHOTS):
        bits = "".join(str(int(res.records[k][s, -1, 0])) if k else "0" for k in reversed(ns["CLBIT_KEYS"]))
        out[bits] = out.get(bits, 0) + 1
    return out


def _counts_cudaq(circuit: CircuitIR) -> Dict[str, int]:
    mod = load_generated_module(generate_cudaq_code(circuit).code, "cudaq_dynamic")
    cudaq.set_random_seed(SEED)
    out: Dict[str, int] = {}
    for bits in cudaq.run(mod.KERNEL, shots_count=SHOTS):
        s = "".join("1" if b else "0" for b in reversed(list(bits)))
        out[s] = out.get(s, 0) + 1
    return out


def verify_equivalence(circuit: CircuitIR, atol: float = 1e-5) -> Dict[str, Any]:
    """
    Verifies the generated code of every target against the reference. Returns a structured
    report: per framework ``executed``, ``equivalent`` (only when a check ran), ``fidelity`` or
    ``tvd``, the bit order, and the reason for anything not run.
    """
    results: Dict[str, Any] = {
        "num_qubits": circuit.num_qubits,
        "reference_simulated": False,
        "frameworks": {},
    }
    fw = results["frameworks"]
    try:
        if is_static(circuit):
            _verify_static(circuit, atol, results)
        else:
            _verify_dynamic(circuit, results)
    except Exception as e:  # verification must never break transpilation
        results["error"] = "verification failed: %s: %s" % (type(e).__name__, e)
    return results


def _record(fw: Dict[str, Any], name: str, available: bool, why_not: str, fn, **extra) -> None:
    if not available:
        fw[name] = {"executed": False, "note": why_not}
        return
    try:
        fw[name] = dict(fn(), executed=True, **extra)
    except Exception as e:
        fw[name] = {"executed": False, "error": "%s: %s" % (type(e).__name__, e)}


def _verify_static(circuit: CircuitIR, atol: float, results: Dict[str, Any]) -> None:
    results["mode"] = "statevector (static circuit; final measurements removed before comparison)"
    plain = _strip_measurements(circuit)
    ref = compute_statevector(plain)
    results["reference_simulated"] = True
    fw = results["frameworks"]

    def check(state_fn, endianness):
        def run():
            out = state_fn()
            sv = out[0] if isinstance(out, tuple) else out
            f = _fid(ref, sv)
            d = {"equivalent": bool(f >= 1.0 - atol), "fidelity": f, "endianness": endianness}
            if isinstance(out, tuple):
                d["endianness"] = ("little-endian (calibrated at runtime)" if out[1]
                                   else "big-endian (calibrated at runtime, normalised)")
            return d
        return run

    _record(fw, "qiskit", HAS_QISKIT, "qiskit not installed on host",
            check(lambda: _state_qiskit(plain), "little-endian (matches reference)"),
            target_version=getattr(qiskit, "__version__", "") if HAS_QISKIT else "")
    _record(fw, "cirq", HAS_CIRQ, "cirq not installed on host",
            check(lambda: _state_cirq(plain), "big-endian (normalised to little-endian, explicit qubit_order)"),
            target_version=getattr(cirq, "__version__", "") if HAS_CIRQ else "")
    _record(fw, "cudaq", HAS_CUDAQ, "cudaq not installed on host; not executed",
            check(lambda: _state_cudaq(plain), ""),
            target_version=str(getattr(cudaq, "__version__", "")).split(" (")[0] if HAS_CUDAQ else "")
    _record(fw, "qniverse", True, "",
            check(lambda: _state_qsdk(plain), "little-endian (via QSDK circuit -> qasm() -> reference simulator)"),
            note="generated QSDK code was run against the %s" % _qsdk_kind())


def _qsdk_kind() -> str:
    try:
        import qnvkit.qsdk_adapter as adapter
        return "installed QSDK" if getattr(adapter, "IS_LIVE_QNIVERSE", False) else "local QSDK stand-in (not the real Qniverse)"
    except Exception:
        return "QSDK stand-in"


def _verify_dynamic(circuit: CircuitIR, results: Dict[str, Any]) -> None:
    circ = _with_measure_all(circuit)
    results["mode"] = ("sampling (dynamic circuit: reference simulator cannot model conditions or mid-circuit "
                       "measurement); %d shots, seed %d, TVD tolerance %.2f, %s" % (SHOTS, SEED, TVD_TOLERANCE, BIT_ORDER_NOTE))
    fw = results["frameworks"]
    dists: Dict[str, Dict[str, float]] = {}

    def sampler(name, fn):
        def run():
            dists[name] = _normalise(fn(circ))
            return {"counts_support": len(dists[name]), "shots": SHOTS}
        return run

    _record(fw, "qiskit", HAS_QISKIT and HAS_AER, "qiskit and qiskit-aer are needed for sampling; not run",
            sampler("qiskit", _counts_qiskit))
    _record(fw, "cirq", HAS_CIRQ, "cirq not installed on host", sampler("cirq", _counts_cirq))
    _record(fw, "cudaq", HAS_CUDAQ, "cudaq not installed on host; not executed", sampler("cudaq", _counts_cudaq))
    fw["qniverse"] = {"executed": False,
                      "note": "dynamic circuit: the QSDK stand-in cannot execute conditions; output only built and exported, not sampled"}
    names = [n for n in ("qiskit", "cirq", "cudaq") if n in dists]
    if len(names) >= 2:
        base = names[0]
        for n in names[1:]:
            tvd = total_variation_distance(dists[base], dists[n])
            fw[n]["tvd"] = tvd
            fw[n]["tvd_against"] = base
            fw[n]["equivalent"] = bool(tvd <= TVD_TOLERANCE)
        fw[base]["tvd"] = 0.0
        fw[base]["tvd_against"] = "(reference sampler)"
        fw[base]["equivalent"] = all(fw[n]["equivalent"] for n in names[1:])
    else:
        for n in names:
            fw[n]["note"] = "only one sampling framework available; no pairwise comparison possible"
