"""
Unified Public Transpiler API for OpenQASM 3.0 / 2.0.

Provides the main entrypoint:
`transpile(source, targets=("qiskit", "cirq", "cudaq"), options=None)`
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Union, Sequence, Dict, Optional, Any
from qnvkit.ir import CircuitIR
from qnvkit.qasm.parser3 import parse_qasm3
from qnvkit.report import TranspileResult, TranspilerReport
from qnvkit.transpile.qiskit_gen import generate_qiskit_code
from qnvkit.transpile.cirq_gen import generate_cirq_code
from qnvkit.transpile.cudaq_gen import generate_cudaq_code
from qnvkit.transpile.qniverse_gen import generate_qniverse_code
from qnvkit.transpile.verify import verify_equivalence

SUPPORTED_TARGETS = {
    "qiskit": generate_qiskit_code,
    "cirq": generate_cirq_code,
    "cudaq": generate_cudaq_code,
    "qniverse": generate_qniverse_code,
    "qsdk": generate_qniverse_code,
}


def transpile(
    source: Union[str, Path, CircuitIR],
    targets: Sequence[str] = ("qiskit", "cirq", "cudaq"),
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, TranspileResult]:
    """
    Transpile OpenQASM 3.0 / 2.0 source code to one or more quantum framework targets.

    Parameters:
    -----------
    source: str, Path, or CircuitIR
        OpenQASM source code string, path to a .qasm file, or pre-built CircuitIR.
    targets: Sequence[str]
        One or more target framework names: 'qiskit', 'cirq', 'cudaq', 'qniverse'.
    options: Dict[str, Any], optional
        Additional transpilation settings:
        - 'verify': bool - if True, execute circuits and verify cross-framework mathematical equivalence.
        - 'atol': float - tolerance for statevector fidelity check (default 1e-5).

    Returns:
    --------
    Dict[str, TranspileResult]
        Dictionary mapping target names to TranspileResult objects containing generated code and structured report.
    """
    options = options or {}

    if isinstance(source, CircuitIR):
        circuit = source
    elif hasattr(source, "qasm"):
        from qnvkit.qsdk_adapter import from_qniverse
        circuit = from_qniverse(source)
    else:
        source_text = source
        if isinstance(source, Path) or (isinstance(source, str) and (os.path.isfile(source) or source.endswith(".qasm"))):
            path = Path(source)
            if path.is_file():
                source_text = path.read_text(encoding="utf-8")
        circuit = parse_qasm3(str(source_text))

    # Equivalence verification
    verify_report = None
    if options.get("verify", False):
        atol = options.get("atol", 1e-5)
        try:
            verify_report = verify_equivalence(circuit, atol=atol)
        except Exception as e:  # verification must never break transpilation
            verify_report = {"error": "verification failed: %s: %s" % (type(e).__name__, e), "frameworks": {}}

    # Generate code for requested targets
    results: Dict[str, TranspileResult] = {}
    for target in targets:
        target_norm = target.lower().strip()
        if target_norm not in SUPPORTED_TARGETS:
            rep = TranspilerReport(target=target_norm, status="ERROR", target_version="unknown")
            rep.add_unsupported(f"Unknown target framework '{target}'. Supported: {list(SUPPORTED_TARGETS.keys())}")
            results[target_norm] = TranspileResult(target=target_norm, code="", report=rep)
            continue

        generator_fn = SUPPORTED_TARGETS[target_norm]
        res = generator_fn(circuit)

        if verify_report:
            res.report.metrics["cross_framework_verification"] = verify_report
            fw_key = "qniverse" if target_norm == "qsdk" else target_norm
            fw_info = verify_report.get("frameworks", {}).get(fw_key, {})
            if fw_info.get("executed") and "equivalent" in fw_info:
                res.report.equivalence_verified = fw_info["equivalent"]
            if fw_info.get("executed") and "fidelity" in fw_info:
                res.report.fidelity = fw_info["fidelity"]
            note = fw_info.get("note") or fw_info.get("error") or verify_report.get("error")
            if fw_info.get("executed"):
                note = "; ".join(x for x in (verify_report.get("mode"), fw_info.get("note")) if x)
            if note:
                res.report.execution_notes = note

        results[target_norm] = res

    return results
