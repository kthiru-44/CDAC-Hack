"""
qnvkit.runner: guarded execution on Qniverse backends through the documented QSDK job API:
    Backend().processor(..) -> .hpc(..) -> .simulator(..)
    job = run(qc, backend, shots, token=token, job_name=..)
    job_status(token, job), fetch_job_result(token, job), credit_balance(token)

A hard job-count cap protects the account's credits.
"""

import os
import time
from typing import Any, Dict, Optional

import qnvkit.qsdk_adapter as _adapter  # makes `Qniverse` importable (real SDK or local stand-in)
from Qniverse.backend import Backend
from Qniverse.api import run, fetch_job_result, job_status, credit_balance


class QniverseRunner:
    def __init__(self, token: Optional[str] = None, max_jobs_quota: int = 10):
        self.token = (token or os.environ.get("QNIVERSE_API_KEY", "")).strip()
        self.max_jobs_quota = max_jobs_quota
        self.jobs_executed = 0
        self.is_live = _adapter.IS_LIVE_QNIVERSE
        # The QSDK requires a global variable named `token` to exist before Backend() is created.
        import __main__
        if self.token and not hasattr(__main__, "token"):
            __main__.token = self.token

    def get_balance(self):
        return credit_balance(self.token)

    def execute_circuit(
        self,
        circuit: Any,
        processor: str = "CPU",
        hpc: str = "QACC_Cluster",
        simulator: str = "qasm_simulator",
        shots: int = 1024,
        job_name: str = "qnvkit_job",
        timeout_s: int = 300,
    ) -> Dict[str, Any]:
        if self.jobs_executed >= self.max_jobs_quota:
            raise RuntimeError(
                "CREDIT PROTECTION: job limit reached (%d/%d)." % (self.jobs_executed, self.max_jobs_quota)
            )

        backend = Backend()
        backend.processor(processor)
        backend.hpc(hpc)
        backend.simulator(simulator)

        job = run(circuit, backend, shots, token=self.token, job_name=job_name)
        self.jobs_executed += 1

        start = time.time()
        status = None
        while time.time() - start < timeout_s:
            status = job_status(self.token, job)
            text = str(status).upper()
            if "COMPLETED" in text:
                break
            if "FAILED" in text or "CANCEL" in text:
                raise RuntimeError("Qniverse job %r ended with status: %s" % (job, status))
            time.sleep(3)
        else:
            raise RuntimeError("Qniverse job %r did not complete within %ds (last status: %s)." % (job, timeout_s, status))

        return {
            "job": job,
            "simulator": simulator,
            "shots": shots,
            "result": fetch_job_result(self.token, job),
            "executed_on": "Qniverse" if self.is_live else "local stand-in (NOT Qniverse)",
            "jobs_remaining_in_quota": self.max_jobs_quota - self.jobs_executed,
        }
