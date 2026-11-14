"""
Local stand-in for ``Qniverse.api`` (used only when the real QSDK is not installed).

Nothing is sent to Qniverse. ``run`` simulates the circuit locally with qnvkit's numpy
simulator and every result is labelled as coming from the local stand-in.
"""

import numpy as np

_JOBS = {}


def run(qc, backend, shots, token=None, job_name="job"):
    if backend._simulator is None:
        raise ValueError("Processor and HPC must be set before setting Simulator.")
    from qnvkit.qasm.parser2 import parse_qasm2
    from qnvkit.sim import compute_statevector

    ir = parse_qasm2(qc.qasm())
    measures = [op for op in ir.ops if op.name == "measure"]
    if not measures:
        raise RuntimeError("Circuit has no measurements to sample.")
    probs = np.abs(compute_statevector(ir)) ** 2
    rng = np.random.default_rng(1234)
    samples = rng.choice(len(probs), size=shots, p=probs / probs.sum())
    n = ir.num_qubits
    counts = {}
    for s in samples:
        bits = ["0"] * ir.num_clbits
        for op in measures:
            # statevector index is little-endian: qubit q is bit q
            bits[op.clbits[0]] = str((int(s) >> op.qubits[0]) & 1)
        key = "".join(reversed(bits))  # classical bit 0 printed right-most
        counts[key] = counts.get(key, 0) + 1
    job_id = len(_JOBS) + 1
    _JOBS[job_id] = {
        "probability": counts, "shots": shots,
        "backend": "LOCAL STAND-IN (not executed on Qniverse)", "job_name": job_name,
    }
    return job_id


def fetch_job_result(token, job):
    return dict(_JOBS[job])


def job_status(token, job):
    return "COMPLETED"


def job_details(token, job):
    return {"job_id": job, "job_name": _JOBS[job]["job_name"], "backend": _JOBS[job]["backend"]}


def transpiled_code(token, job):
    return ""


def credit_balance(token):
    return 0


def get_backend(token):
    from .backend import _SIMS
    return {"%s/%s" % k: v for k, v in _SIMS.items()}
