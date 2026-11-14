"""
qnvkit.runner: Safe execution wrapper for C-DAC Qniverse backend with credit protection.
Implements a strict job-count cap to prevent credit burn.
"""

import os
import time
from typing import Dict, Any, Optional

try:
    from Qniverse.backend import Backend
    from Qniverse.api import run, fetch_job_result, job_status, credit_balance
except ImportError:
    from qnvkit.shim.Qniverse.backend import Backend
    from qnvkit.shim.Qniverse.api import run, fetch_job_result, job_status, credit_balance


class QniverseRunner:
    """
    Guarded executor for Qniverse Cloud Jobs.
    Enforces a strict execution quota (default max 10 jobs) to protect account credits.
    """
    def __init__(self, token: Optional[str] = None, max_jobs_quota: int = 10):
        self.token = token or os.environ.get("QNIVERSE_API_KEY", "")
        self.max_jobs_quota = max_jobs_quota
        self.jobs_executed = 0

    def get_balance(self) -> int:
        """Queries current credit balance."""
        return credit_balance(token=self.token)

    def execute_circuit(
        self,
        circuit: Any,
        processor: str = "CPU",
        hpc: str = "QACC_Cluster",
        simulator: str = "qasm_simulator",
        shots: int = 1024,
        job_name: str = "qnvkit_job"
    ) -> Dict[str, Any]:
        """
        Executes circuit on Qniverse backend with strict quota enforcement.
        """
        if self.jobs_executed >= self.max_jobs_quota:
            raise RuntimeError(
                f"CREDIT PROTECTION: Execution limit reached ({self.jobs_executed}/{self.max_jobs_quota}). "
                "Preventing further cloud credit deduction."
            )

        # Build backend hierarchy in documented order
        backend = Backend()
        backend.processor(processor)
        backend.hpc(hpc)
        backend.simulator(simulator)

        job_id = run(circuit, backend, shots=shots, token=self.token, job_name=job_name)
        self.jobs_executed += 1

        # Poll for completion (with timeout)
        start_time = time.time()
        while time.time() - start_time < 60:
            status = job_status(job_id, token=self.token)
            if status in ("COMPLETED", "SUCCESS", "FINISHED"):
                break
            elif status in ("FAILED", "ERROR", "CANCELLED"):
                raise RuntimeError(f"Qniverse Job {job_id} failed with status: {status}")
            time.sleep(2)

        result = fetch_job_result(job_id, token=self.token)
        return {
            "job_id": job_id,
            "simulator": simulator,
            "shots": shots,
            "result": result,
            "jobs_remaining_in_quota": self.max_jobs_quota - self.jobs_executed,
        }
