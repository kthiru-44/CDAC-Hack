"""
Local stand-in for ``Qniverse.api`` (used only when the real QSDK is not installed).

Nothing is sent to Qniverse. ``run`` simulates the circuit locally with qnvkit's numpy
simulator and every result is labelled as coming from the local stand-in.
"""

_JOBS = {}


def run(qc, backend, shots, token=None, job_name="job"):
    if backend._simulator is None:
        raise ValueError("Processor and HPC must be set before setting Simulator.")
    from qnvkit.qasm.parser2 import parse_qasm2
    from qnvkit.sim import sample_counts

    ir = parse_qasm2(qc.qasm())
    if not any(op.name == "measure" for op in ir.ops):
        raise RuntimeError("Circuit has no measurements to sample.")
    counts = sample_counts(ir, shots=shots)  # keys: classical bit 0 printed right-most
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
