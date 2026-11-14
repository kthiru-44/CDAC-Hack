"""
Cross-framework equivalence verifier.

Every check runs the *generated code* of a target and compares it with qnvkit's own
reference simulation of the original circuit (``qnvkit.sim``):

* Static circuits (no condition, no reset, nothing after a measurement on the same qubit):
  state vectors are compared by fidelity.
* Dynamic circuits: Qiskit (Aer), Cirq, CUDA-Q and the QSDK route are sampled with a fixed
  seed and each count distribution is compared with the exact outcome distribution of the
  original circuit (total variation distance).

``compare_counts`` runs the original circuit and every generated program for the same number
of shots and returns the counts side by side (``format_counts_table`` prints them).

A framework that is missing, or a check that was not run, is reported with
``executed: False`` and a reason; nothing is claimed that did not run.
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
from qnvkit.sim import (
    compute_statevector, convert_statevector_endianness, exact_distribution, sample_counts,
    total_variation_distance,
)
from qnvkit.transpile.qiskit_gen import generate_qiskit_code
from qnvkit.transpile.cirq_gen import generate_cirq_code
from qnvkit.transpile.cudaq_gen import generate_cudaq_code
from qnvkit.transpile.qniverse_gen import generate_qniverse_code

HAS_QISKIT: Optional[bool] = None
HAS_AER: Optional[bool] = None
HAS_CIRQ: Optional[bool] = None
HAS_CUDAQ: Optional[bool] = None


def _has_qiskit() -> bool:
    if HAS_QISKIT is not None:
        return bool(HAS_QISKIT)
    try:
        import qiskit
        from qiskit.quantum_info import Statevector
        return True
    except (ImportError, Exception):
        return False


def _has_aer() -> bool:
    if HAS_AER is not None:
        return bool(HAS_AER)
    try:
        import qiskit_aer
        return True
    except (ImportError, Exception):
        return False


def _has_cirq() -> bool:
    if HAS_CIRQ is not None:
        return bool(HAS_CIRQ)
    try:
        import cirq
        return True
    except (ImportError, Exception):
        return False


def _has_cudaq() -> bool:
    if HAS_CUDAQ is not None:
        return bool(HAS_CUDAQ)
    try:
        import cudaq
        return True
    except (ImportError, Exception):
        return False

def _qiskit_version() -> str:
    try:
        import qiskit
        return getattr(qiskit, "__version__", "")
    except Exception:
        return ""

def _cirq_version() -> str:
    try:
        import cirq
        return getattr(cirq, "__version__", "")
    except Exception:
        return ""

def _cudaq_version() -> str:
    try:
        import cudaq
        return str(getattr(cudaq, "__version__", "")).split(" (")[0]
    except Exception:
        return ""

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
    import qiskit
    from qiskit.quantum_info import Statevector as QiskitStatevector
    ns: Dict[str, Any] = {}
    exec(generate_qiskit_code(circuit).code, ns)
    return np.array(QiskitStatevector(ns["build_circuit"]()))


def _state_cirq(circuit: CircuitIR) -> np.ndarray:
    import cirq
    ns: Dict[str, Any] = {}
    exec(generate_cirq_code(circuit).code, ns)
    c = ns["build_circuit"]()
    order = [cirq.NamedQubit("%s_%d" % (r.name, i)) for r in circuit.qregs for i in range(r.size)]
    sv = cirq.Simulator(dtype=np.complex128).simulate(c, qubit_order=order).final_state_vector
    return convert_statevector_endianness(np.array(sv), circuit.num_qubits)  # cirq: first qubit is MSB


def _cudaq_is_little_endian() -> bool:
    """One-gate calibration: x on qubit 0 of 2 gives index 1 when qubit 0 is the least significant bit."""
    import cudaq
    mod = load_generated_module(
        "import cudaq\n\n@cudaq.kernel\ndef cal():\n    q = cudaq.qvector(2)\n    x(q[0])\n", "cal")
    return int(np.argmax(np.abs(np.array(cudaq.get_state(mod.cal))))) == 1


def _state_cudaq(circuit: CircuitIR):
    import cudaq
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


# ---------------------------------------------------------------- sampling
# Each sampler executes the generated code of one target and returns counts keyed by a
# bitstring over all classical bits, classical bit 0 right-most.
def _counts_qiskit(circuit: CircuitIR, shots: int = SHOTS, seed: int = SEED) -> Dict[str, int]:
    from qiskit import transpile as qk_transpile
    from qiskit_aer import AerSimulator
    ns: Dict[str, Any] = {}
    exec(generate_qiskit_code(circuit).code, ns)
    qc = ns["build_circuit"]()
    sim = AerSimulator(seed_simulator=seed)
    counts = sim.run(qk_transpile(qc, sim), shots=shots).result().get_counts()
    out: Dict[str, int] = {}
    for k, v in counts.items():  # Qiskit separates registers with a space
        out[k.replace(" ", "")] = out.get(k.replace(" ", ""), 0) + v
    return out


def _counts_cirq(circuit: CircuitIR, shots: int = SHOTS, seed: int = SEED) -> Dict[str, int]:
    import cirq
    ns: Dict[str, Any] = {}
    exec(generate_cirq_code(circuit).code, ns)
    c = ns["build_circuit"]()
    res = cirq.Simulator(seed=seed).run(c, repetitions=shots)
    out: Dict[str, int] = {}
    for s in range(shots):
        bits = "".join(str(int(res.records[k][s, -1, 0])) if k else "0" for k in reversed(ns["CLBIT_KEYS"]))
        out[bits] = out.get(bits, 0) + 1
    return out


def _counts_cudaq(circuit: CircuitIR, shots: int = SHOTS, seed: int = SEED) -> Dict[str, int]:
    import cudaq
    mod = load_generated_module(generate_cudaq_code(circuit).code, "cudaq_dynamic")
    cudaq.set_random_seed(seed)
    out: Dict[str, int] = {}
    for bits in cudaq.run(mod.KERNEL, shots_count=shots):
        s = "".join("1" if b else "0" for b in reversed(list(bits)))
        out[s] = out.get(s, 0) + 1
    return out


def _counts_qsdk(circuit: CircuitIR, shots: int = SHOTS, seed: int = SEED) -> Dict[str, int]:
    """Builds the generated QSDK program, reads it back through ``qc.qasm()`` and samples that circuit."""
    import qnvkit.qsdk_adapter as adapter
    res = generate_qniverse_code(circuit)
    if res.report.unsupported_constructs:
        raise RuntimeError("generator reported unsupported constructs: %s" % res.report.unsupported_constructs[0]["construct"])
    ns: Dict[str, Any] = {}
    exec(res.code, ns)
    return sample_counts(adapter.from_qniverse(ns["build_circuit"]()), shots=shots, seed=seed)


def _cudaq_missing_note(circuit: CircuitIR) -> str:
    """Why CUDA-Q was not executed; the generated kernel is at least checked to be valid Python."""
    try:
        import ast
        ast.parse(generate_cudaq_code(circuit).code)
        return "cudaq runtime absent (code syntax and kernel AST verified; execution requires NVIDIA GPU + CUDA-Q)"
    except Exception as e:
        return "cudaq syntax error: %s" % e


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

    has_qk = _has_qiskit()
    has_cq = _has_cirq()
    has_cd = _has_cudaq()

    _record(fw, "qiskit", has_qk, "qiskit not installed on host",
            check(lambda: _state_qiskit(plain), "little-endian (matches reference)"),
            target_version=_qiskit_version() if has_qk else "")
    _record(fw, "cirq", has_cq, "cirq not installed on host",
            check(lambda: _state_cirq(plain), "big-endian (normalised to little-endian, explicit qubit_order)"),
            target_version=_cirq_version() if has_cq else "")

    _record(fw, "cudaq", has_cd, "" if has_cd else _cudaq_missing_note(circuit),
            check(lambda: _state_cudaq(plain), ""),
            target_version=_cudaq_version() if has_cd else "")
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
    results["mode"] = ("sampling (dynamic circuit: each target is sampled and compared with the exact outcome "
                       "distribution of the original circuit); %d shots, seed %d, TVD tolerance %.2f, %s"
                       % (SHOTS, SEED, TVD_TOLERANCE, BIT_ORDER_NOTE))
    reference = exact_distribution(circ)
    results["reference_simulated"] = True
    fw = results["frameworks"]

    def sampler(fn):
        def run():
            dist = _normalise(fn(circ))
            tvd = total_variation_distance(reference, dist)
            return {"counts_support": len(dist), "shots": SHOTS, "tvd": tvd,
                    "tvd_against": "original circuit (qnvkit reference simulator)",
                    "equivalent": bool(tvd <= TVD_TOLERANCE)}
        return run

    has_cd = _has_cudaq()
    _record(fw, "qiskit", _has_qiskit() and _has_aer(), "qiskit and qiskit-aer are needed for sampling; not run",
            sampler(_counts_qiskit))
    _record(fw, "cirq", _has_cirq(), "cirq not installed on host", sampler(_counts_cirq))
    _record(fw, "cudaq", has_cd, "" if has_cd else _cudaq_missing_note(circuit), sampler(_counts_cudaq))

    if generate_qniverse_code(circ).report.unsupported_constructs:
        fw["qniverse"] = {"executed": False,
                          "note": "the QSDK cannot express this dynamic circuit (see unsupported constructs); not sampled"}
    else:
        _record(fw, "qniverse", True, "", sampler(_counts_qsdk),
                note="QSDK circuit built by the generated code against the %s, exported with qasm() and "
                     "sampled by the reference simulator" % _qsdk_kind())


# ---------------------------------------------------------------- side-by-side counts
REFERENCE_LABEL = "original"


def compare_counts(source: Any, shots: int = 1024, seed: int = SEED) -> Dict[str, Any]:
    """
    Runs the original circuit and the generated code of every target for ``shots`` shots.

    ``source`` is OpenQASM text or a ``CircuitIR``. The original circuit is executed by
    qnvkit's reference simulator, which is independent of all target frameworks. Returns::

        {"shots": ..., "seed": ..., "bit_order": ...,
         "exact": {bitstring: probability},            # original circuit, no sampling noise
         "runs": {"original": {"executed": True, "counts": {...}, "tvd": ..., "backend": ...},
                  "qiskit": {...}, "cirq": {...}, "cudaq": {...}, "qniverse": {...}}}

    ``tvd`` is the total variation distance between a run's counts and ``exact``; the result
    also carries ``tolerance`` (see ``sampling_tolerance``). A target that could not be
    executed has ``executed: False`` and a ``note``.
    """
    if not isinstance(source, CircuitIR):
        from qnvkit.qasm.parser3 import parse_qasm3
        source = parse_qasm3(str(source))
    circ = _with_measure_all(source)
    exact = exact_distribution(circ)
    runs: Dict[str, Any] = {}

    def add(name: str, backend: str, available: bool, why_not: str, fn) -> None:
        if not available:
            runs[name] = {"executed": False, "note": why_not}
            return
        try:
            counts = fn()
            runs[name] = {"executed": True, "backend": backend, "counts": counts,
                          "tvd": total_variation_distance(exact, _normalise(counts))}
        except Exception as e:
            runs[name] = {"executed": False, "note": "%s: %s" % (type(e).__name__, e)}

    has_cd = _has_cudaq()
    add(REFERENCE_LABEL, "qnvkit reference simulator (NumPy)", True, "",
        lambda: sample_counts(circ, shots=shots, seed=seed))
    add("qiskit", "generated Qiskit code on AerSimulator", _has_qiskit() and _has_aer(),
        "qiskit / qiskit-aer not installed", lambda: _counts_qiskit(circ, shots, seed))
    add("cirq", "generated Cirq code on cirq.Simulator", _has_cirq(),
        "cirq not installed", lambda: _counts_cirq(circ, shots, seed))
    add("cudaq", "generated CUDA-Q kernel via cudaq.run", has_cd,
        "" if has_cd else _cudaq_missing_note(circ), lambda: _counts_cudaq(circ, shots, seed))
    add("qniverse", "generated QSDK code (%s) -> qasm() -> reference simulator" % _qsdk_kind(), True, "",
        lambda: _counts_qsdk(circ, shots, seed + 1))  # other seed: must not simply replay the reference draw
    return {"shots": shots, "seed": seed, "bit_order": BIT_ORDER_NOTE, "exact": exact, "runs": runs,
            "tolerance": sampling_tolerance(len(exact), shots)}


def sampling_tolerance(num_outcomes: int, shots: int) -> float:
    """
    TVD below which a sampled run counts as matching an exact distribution. The expected TVD
    of ``shots`` samples over K outcomes is at most 0.5 * sqrt(K / shots); twice that is
    allowed, and never less than ``TVD_TOLERANCE``.
    """
    return max(TVD_TOLERANCE, float(np.sqrt(num_outcomes / float(shots))))


def format_counts_table(comparison: Dict[str, Any]) -> str:
    """Text table of a ``compare_counts`` result: one row per outcome, one column per run."""
    runs = comparison["runs"]
    tolerance = comparison["tolerance"]
    done = [n for n, r in runs.items() if r["executed"]]
    outcomes = sorted(set(comparison["exact"]).union(*(runs[n]["counts"] for n in done)))
    width = max(9, max(len(o) for o in outcomes))
    row = "%-" + str(width) + "s %8s" + " %9s" * len(done)
    lines = [
        "%d shots per run; %s" % (comparison["shots"], comparison["bit_order"]),
        row % (("outcome", "exact p") + tuple(done)),
        "-" * (width + 9 + 10 * len(done)),
    ]
    for o in outcomes:
        lines.append(row % ((o, "%.4f" % comparison["exact"].get(o, 0.0))
                            + tuple(runs[n]["counts"].get(o, 0) for n in done)))
    lines.append("-" * (width + 9 + 10 * len(done)))
    lines.append(row % (("TVD", "") + tuple("%.4f" % runs[n]["tvd"] for n in done)))
    lines.append(row % (("match", "") + tuple("yes" if runs[n]["tvd"] <= tolerance else "NO" for n in done)))
    lines.append("TVD = total variation distance to the exact distribution of the original circuit "
                 "(match: TVD <= %.3f, the sampling-noise bound for this many shots and outcomes)." % tolerance)
    for n, r in runs.items():
        lines.append("  %-9s %s" % (n, r["backend"] if r["executed"] else "NOT RUN: " + r["note"]))
    return "\n".join(lines)
