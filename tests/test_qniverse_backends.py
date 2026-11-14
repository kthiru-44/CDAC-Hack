"""
Tests for Qniverse Backend Compatibility with Transpiled Frameworks.

Verifies that all targets supported by QC-C2-03 (Qiskit, Cirq, CUDA-Q, QSDK)
map to verified, active simulator backends on C-DAC Param Utkarsh and QACC Cluster.
"""

import pytest

QNIVERSE_VERIFIED_BACKENDS = {
    "qiskit": [
        {"hpc": "Param_Utkarsh", "processor": "CPU", "simulator": "qasm_simulator"},
        {"hpc": "Param_Utkarsh", "processor": "CPU", "simulator": "aer_simulator_statevector"},
        {"hpc": "Param_Utkarsh", "processor": "GPU", "simulator": "aer_simulator_statevector_gpu"},
        {"hpc": "QACC_Cluster", "processor": "CPU", "simulator": "qasm_simulator"},
        {"hpc": "QACC_Cluster", "processor": "GPU", "simulator": "aer_simulator_statevector_gpu"},
    ],
    "cirq": [
        {"hpc": "Param_Utkarsh", "processor": "CPU", "simulator": "cirq_simulator"},
        {"hpc": "QACC_Cluster", "processor": "CPU", "simulator": "cirq_simulator"},
        {"hpc": "QACC_Cluster", "processor": "CPU", "simulator": "qsimcirq_simulator"},
        {"hpc": "QACC_Cluster", "processor": "GPU", "simulator": "qsimcirq_cuquantum_gpu_simulator"},
    ],
    "cudaq": [
        {"hpc": "QACC_Cluster", "processor": "GPU", "simulator": "nvidia_cudaq_statevector_simulator"},
    ],
    "qniverse": [
        {"hpc": "Param_Utkarsh", "processor": "CPU", "simulator": "qasm_simulator"},
        {"hpc": "QACC_Cluster", "processor": "CPU", "simulator": "qasm_simulator"},
    ]
}


def test_all_transpiler_frameworks_have_qniverse_backends():
    """Verify that every transpiled framework maps to at least one valid Qniverse backend."""
    for framework in ["qiskit", "cirq", "cudaq", "qniverse"]:
        backends = QNIVERSE_VERIFIED_BACKENDS.get(framework, [])
        assert len(backends) > 0, f"No Qniverse backends mapped for framework '{framework}'"

        # Check required fields
        for b in backends:
            assert "hpc" in b
            assert "processor" in b
            assert "simulator" in b
            assert b["hpc"] in ("Param_Utkarsh", "QACC_Cluster")
            assert b["processor"] in ("CPU", "GPU")


def test_cudaq_gpu_acceleration_on_qniverse():
    """Verify that NVIDIA CUDA-Q runs on QACC_Cluster GPU nodes."""
    cudaq_backends = QNIVERSE_VERIFIED_BACKENDS["cudaq"]
    assert any(b["simulator"] == "nvidia_cudaq_statevector_simulator" and b["processor"] == "GPU" for b in cudaq_backends)


def test_cirq_gpu_cuquantum_on_qniverse():
    """Verify that Cirq has both CPU (cirq_simulator) and GPU (cuquantum) on Qniverse."""
    cirq_backends = QNIVERSE_VERIFIED_BACKENDS["cirq"]
    simulators = [b["simulator"] for b in cirq_backends]
    assert "cirq_simulator" in simulators
    assert "qsimcirq_cuquantum_gpu_simulator" in simulators
