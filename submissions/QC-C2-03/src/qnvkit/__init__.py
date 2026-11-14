"""
qnvkit: High-Performance Quantum SDK Tooling for C-DAC Qniverse
Supports:
  - QC-C1-01: Circuit Profiling and Limited Basis-Gate Decomposition
  - QC-C2-03: OpenQASM 3.0 Transpiler to Qiskit, Cirq, and CUDA-Q
  - QC-C3-03: Quantum Circuit Optimization Using QSDK
"""

from qnvkit.ir import Op, Register, CircuitIR
from qnvkit.report import ProfileReport, DecomposeResult, UnsupportedReport, OptimizeResult, TranspilerReport
from qnvkit.metrics import profile
from qnvkit.decompose.decomposer import decompose
from qnvkit.transpile.api import transpile
from qnvkit.optimize.optimizer import optimize
from qnvkit.viz import draw_circuit, simulate_circuit

__all__ = [
    "Op",
    "Register",
    "CircuitIR",
    "ProfileReport",
    "DecomposeResult",
    "UnsupportedReport",
    "OptimizeResult",
    "TranspilerReport",
    "profile",
    "decompose",
    "transpile",
    "optimize",
    "draw_circuit",
    "simulate_circuit",
]

