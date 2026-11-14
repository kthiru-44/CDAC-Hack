#!/usr/bin/env python3
"""
Builds notebooks/c1_demo_standalone.ipynb: the C1-01 demo notebook with the whole qnvkit
package embedded, so a single file can be uploaded to Qniverse JupyterLab.

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

nb = json.load(open(os.path.join(ROOT, "notebooks", "c1_demo.ipynb")))


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
if _dir not in sys.path:
    sys.path.insert(0, _dir)
print("qnvkit unpacked to", _dir)
''' % payload)

check = code('''
# What the QSDK itself reports (useful if anything below fails).
_probe = QniverseCircuit()
_q = QuantumRegister(2, 'q'); _c = ClassicalRegister(2, 'c')
_probe.add_register(_q); _probe.add_register(_c)
_probe.add_gate(h, _q[0]); _probe.add_gate(cp(0.5), _q[0], _q[1]); _probe.add_gate(u3(0.1, 0.2, 0.3), _q[1])
_probe.add_gate(barrier, _q[0]); _probe.add_gate(measure, _q[0], _c[0])
_ret = _probe.qasm()
print("qc.qasm() returned:", type(_ret).__name__)
print(adapter.read_qasm(_probe))
''')

cells = nb["cells"]
cells[0] = md('''
# QC-C1-01: Circuit Profiling and Limited Basis-Gate Decomposition
PESU – C-DAC Quantum Hackathon 2026

**Single-file version:** upload only this notebook to Qniverse JupyterLab and run all cells. The first cell unpacks the embedded `qnvkit` package; the second reports whether the **official Qniverse QSDK** is in use.
''')
nb["cells"] = [cells[0], unpack, cells[1], check] + cells[2:]
out = os.path.join(ROOT, "notebooks", "c1_demo_standalone.ipynb")
json.dump(nb, open(out, "w"), indent=1)
print("wrote", out, "(%d KB)" % (os.path.getsize(out) // 1024))
