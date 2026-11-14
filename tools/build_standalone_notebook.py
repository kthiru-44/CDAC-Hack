#!/usr/bin/env python3
"""
Builds notebooks/c{1,2,3}_demo_standalone.ipynb: each demo notebook with the whole qnvkit
package embedded, so a single file can be uploaded to Qniverse JupyterLab.

Run this again after any change to src/qnvkit or to a notebooks/c*_demo.ipynb source notebook.

    python tools/build_standalone_notebook.py
"""
import base64
import io
import json
import os
import textwrap
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
    for folder, _, files in os.walk(os.path.join(SRC, "qnvkit")):
        if "__pycache__" in folder:
            continue
        for f in sorted(files):
            if f.endswith(".py"):
                full = os.path.join(folder, f)
                z.write(full, os.path.relpath(full, SRC))
payload = "\n".join(textwrap.wrap(base64.b64encode(buf.getvalue()).decode(), 100))

nb1 = json.load(open(os.path.join(ROOT, "notebooks", "c1_demo.ipynb")))


def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": text.strip("\n").splitlines(True)}


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip("\n").splitlines(True)}


unpack = code('''
# Unpacks the embedded qnvkit package next to this notebook (pure Python, needs only numpy).
import base64, io, os, sys, zipfile
_PKG = """
%s
"""
_dir = os.path.abspath("qnvkit_pkg")
zipfile.ZipFile(io.BytesIO(base64.b64decode(_PKG.replace("\\n", "")))).extractall(_dir)
# Always use THIS embedded copy: put it first and drop any older qnvkit already imported or on the path.
sys.path[:] = [_dir] + [p for p in sys.path if p != _dir]
for _m in [m for m in sys.modules if m == "qnvkit" or m.startswith("qnvkit.")]:
    del sys.modules[_m]
print("qnvkit unpacked to", _dir)
''' % payload)

pip_install_common = code('''
# Cell: Install execution frameworks and graphical drawers (Qiskit, Aer, Matplotlib)
# Purges cache first and uses --no-cache-dir to prevent container disk exhaustion
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "cache", "purge"], capture_output=True)
subprocess.run([sys.executable, "-m", "pip", "install", "--no-cache-dir", "--quiet", "qiskit", "qiskit-aer", "matplotlib", "pylatexenc"], check=False)
''')

diagnose = code('''
# Which QSDK packages does this Python environment have?
import importlib, importlib.util, subprocess, sys
importlib.invalidate_caches()

print("Python", sys.version.split()[0])
for _n in ("Qniverse", "qniverse"):
    print("importable as %r:" % _n, importlib.util.find_spec(_n) is not None)
_pip = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True).stdout
print([l for l in _pip.splitlines() if "niverse" in l.lower() or "qsdk" in l.lower()])
''')

check = code('''
# What the real QSDK does with the constructs this demo uses. Every probe is isolated, so one
# failure does not stop the others. Please keep this output if anything below fails.
import traceback

def _probe(label, build):
    qc = QniverseCircuit()
    q = QuantumRegister(3, 'q'); c = ClassicalRegister(3, 'c')
    qc.add_register(q); qc.add_register(c)
    try:
        build(qc, q, c)
        text = adapter.read_qasm(qc)
        print("[OK]  %s\\n%s\\n" % (label, "\\n".join("      " + l for l in text.splitlines()[4:])))
    except Exception as e:
        print("[ERR] %s -> %s: %s\\n" % (label, type(e).__name__, e))

_probe("h, cp, u3, measure", lambda qc, q, c: (qc.add_gate(h, q[0]), qc.add_gate(cp(0.5), q[0], q[1]),
       qc.add_gate(u3(0.1, 0.2, 0.3), q[1]), qc.add_gate(measure, q[0], c[0])))
_probe("barrier on 2 qubits q[0],q[1]", lambda qc, q, c: (qc.add_gate(h, q[0]), qc.add_gate(barrier, q[0], q[1])))
_probe("barrier on 2 qubits q[0],q[2]", lambda qc, q, c: (qc.add_gate(h, q[0]), qc.add_gate(barrier, q[0], q[2])))
_probe("barrier on 1 qubit", lambda qc, q, c: (qc.add_gate(h, q[0]), qc.add_gate(barrier, q[0])))
_probe("reset + conditional", lambda qc, q, c: (qc.add_gate(measure, q[0], c[0]), qc.add_gate(reset, q[1]),
       qc.add_conditional_gate(c, 1, x, q[1])))
_probe("ccx, swap, crz, measure_all", lambda qc, q, c: (qc.add_gate(ccx, q[0], q[1], q[2]), qc.add_gate(swap, q[0], q[1]),
       qc.add_gate(crz(0.7), q[0], q[1]), qc.measure_all()))

# Source of the SDK's own QASM export around barriers (read-only; for debugging).
try:
    import importlib, inspect
    if not adapter.IS_LIVE_QNIVERSE:
        raise RuntimeError("the official QSDK is not in use, so there is no SDK source to show")
    _m = importlib.import_module(adapter.QSDK_IMPORT_NAME + ".transpile.qasm")
    _lines = inspect.getsource(_m).splitlines()
    _hits = [i for i, l in enumerate(_lines) if "barrier" in l.lower()]
    print("--- SDK source lines mentioning 'barrier' (with context) ---")
    _shown = set()
    for i in _hits:
        for j in range(max(0, i - 6), min(len(_lines), i + 22)):
            if j not in _shown:
                _shown.add(j); print("%4d  %s" % (j + 1, _lines[j]))
        print("      ...")
except Exception as e:
    print("source not available:", e)
''')

# --- Build C1 standalone ---
cells1 = nb1["cells"]
cells1[1] = code('''
import qnvkit, qnvkit.qsdk_adapter as adapter          # must be imported before Qniverse
from qnvkit.metrics import profile
from qnvkit.decompose.decomposer import decompose

from Qniverse.QniverseCircuit import *
from Qniverse.gates import *
import numpy as np

print("qnvkit loaded from:", os.path.dirname(qnvkit.__file__))
print("QSDK in use:", adapter.qsdk_description())
''')
cells1[0] = md('''
# QC-C1-01: Circuit Profiling and Limited Basis-Gate Decomposition
PESU – C-DAC Quantum Hackathon 2026

**Single-file version:** upload only this notebook to Qniverse JupyterLab and run all cells. The first cell unpacks the embedded `qnvkit` package; the second reports whether the **official Qniverse QSDK** is in use.
''')
nb1["cells"] = [cells1[0], unpack, pip_install_common, diagnose, cells1[1], check] + cells1[3:]
out1 = os.path.join(ROOT, "notebooks", "c1_demo_standalone.ipynb")
json.dump(nb1, open(out1, "w"), indent=1)
print("wrote", out1, "(%d KB)" % (os.path.getsize(out1) // 1024))

# --- Build C2 standalone ---
c2_path = os.path.join(ROOT, "notebooks", "c2_demo.ipynb")
if os.path.exists(c2_path):
    nb2 = json.load(open(c2_path))
    cells2 = nb2["cells"]
    # c2_demo.ipynb starts with: title, pip install, imports. All three are replaced here.
    imports_c2 = code('''
import os, sys, json
import qnvkit
from qnvkit.transpile.api import transpile
from qnvkit.transpile.verify import compare_counts, format_counts_table
from qnvkit.qasm.parser3 import parse_qasm3
from qnvkit.qasm.diagnostics import QASMError

print("qnvkit loaded from:", os.path.dirname(qnvkit.__file__))
print("qnvkit transpiler ready!")
''')
    pip_c2 = code('''
# Cell: Install execution frameworks for cross-framework verification (Qiskit, Aer, Cirq, Matplotlib)
# Purges cache first and uses --no-cache-dir to prevent container disk exhaustion
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "cache", "purge"], capture_output=True)
subprocess.run([sys.executable, "-m", "pip", "install", "--no-cache-dir", "--quiet", "qiskit", "qiskit-aer", "cirq-core", "matplotlib", "pylatexenc"], check=False)
''')
    framework_check = code('''
# Check available target frameworks in this Python environment.
# Note: Code generation works for ALL targets (Qiskit, Cirq, CUDA-Q, QSDK).
# Both Qiskit and Cirq enable cross-framework execution and equivalence checking.
import importlib, importlib.util, sys
importlib.invalidate_caches()
print("Python", sys.version.split()[0])
for _m in ("qiskit", "qiskit_aer", "cirq", "cudaq", "Qniverse", "qniverse"):
    status = "AVAILABLE (simulation & verification active)" if importlib.util.find_spec(_m) is not None else "not installed (code generated & AST verified)"
    print("%-12s %s" % (_m, status))
''')
    cells2[0] = md('''
# QC-C2-03: OpenQASM 3.0 Transpiler across Qiskit, Cirq, CUDA-Q & QSDK
PESU – C-DAC Quantum Hackathon 2026

**Single-file version:** upload only this notebook to Qniverse JupyterLab and run all cells. The first cell unpacks the embedded `qnvkit` package; the second installs target frameworks for verification.
''')
    nb2["cells"] = [cells2[0], unpack, pip_c2, framework_check, imports_c2] + cells2[3:]
    out2 = os.path.join(ROOT, "notebooks", "c2_demo_standalone.ipynb")
    json.dump(nb2, open(out2, "w"), indent=1)
    print("wrote", out2, "(%d KB)" % (os.path.getsize(out2) // 1024))

# --- Build C3 standalone ---
c3_path = os.path.join(ROOT, "notebooks", "c3_demo.ipynb")
if os.path.exists(c3_path):
    nb3 = json.load(open(c3_path))
    cells3 = nb3["cells"]
    cells3[1] = code('''
import os, sys
import qnvkit, qnvkit.qsdk_adapter as adapter          # must be imported before Qniverse
from qnvkit.optimize import optimize
from qnvkit.metrics import profile
from qnvkit.qsdk_adapter import from_qniverse, to_qniverse
from qnvkit.sim import check_unitary_equivalence

from Qniverse.QniverseCircuit import *
from Qniverse.gates import *
import numpy as np

print("qnvkit loaded from:", os.path.dirname(qnvkit.__file__))
print("QSDK in use:", adapter.qsdk_description())
print("qnvkit optimizer ready!")
''')
    cells3[0] = md('''
# QC-C3-03: Quantum Circuit Optimization Using QSDK
PESU – C-DAC Quantum Hackathon 2026

**Single-file version:** upload only this notebook to Qniverse JupyterLab and run all cells. The first cell unpacks the embedded `qnvkit` package; the second installs target frameworks for verification.
''')
    nb3["cells"] = [cells3[0], unpack, pip_install_common, diagnose, cells3[1], check] + cells3[3:]
    out3 = os.path.join(ROOT, "notebooks", "c3_demo_standalone.ipynb")
    json.dump(nb3, open(out3, "w"), indent=1)
    print("wrote", out3, "(%d KB)" % (os.path.getsize(out3) // 1024))
