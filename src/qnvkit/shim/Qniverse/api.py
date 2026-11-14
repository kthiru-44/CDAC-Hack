"""
qnvkit.shim.Qniverse.api: Mock QSDK API execution functions for local development and testing.
"""

from typing import Dict, Any, Optional
import uuid


def run(qc: Any, backend: Any, shots: int = 1024, token: Optional[str] = None, job_name: str = "job") -> str:
    """Returns a mock job ID for local testing."""
    return f"mock_job_{uuid.uuid4().hex[:8]}"


def fetch_job_result(job_id: str, token: Optional[str] = None) -> Dict[str, Any]:
    """Returns standard job results dictionary."""
    return {
        "job_id": job_id,
        "status": "COMPLETED",
        "counts": {"00": 512, "11": 512},
        "shots": 1024,
    }


def job_status(job_id: str, token: Optional[str] = None) -> str:
    return "COMPLETED"


def transpiled_code(job_id: str, token: Optional[str] = None) -> str:
    return "OPENQASM 2.0;"


def credit_balance(token: Optional[str] = None) -> int:
    return 50
