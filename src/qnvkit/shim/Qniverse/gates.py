"""
qnvkit.shim.Qniverse.gates: Documented QSDK gate constants.
"""

from qnvkit.gates import DOCUMENTED_GATE_NAMES

for name in DOCUMENTED_GATE_NAMES:
    globals()[name] = name
