# 02 — Questions for the C-DAC representatives (first hour)

The QSDK documentation page was empty when we read it, and every problem requires **documented** QSDK interfaces.
1. Python package name for the QSDK? How do we construct a `QniverseCircuit` and add gates, measurements, barriers, resets?
2. What are the exact gate names and parameter conventions the QSDK supports?
3. How do we read the operation list back out of a `QniverseCircuit` (needed for profiling and optimising)?
4. Can we pip-install qiskit, cirq, cudaq (and pyzx, if used) inside the Qniverse JupyterLab?
5. Is OpenQASM 2.0 / 3.0 import or export available in the SDK, or must we write our own parser?
6. For C2-03: which framework versions should the generated code target?
7. Are the three weights (0.4 / 0.3 / 0.2) final, and how is each class's score computed?
