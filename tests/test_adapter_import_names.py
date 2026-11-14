"""The adapter must find the official QSDK whether it is installed as `Qniverse` or `qniverse`."""
import os
import shutil
import subprocess
import sys
import textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHIM = os.path.join(ROOT, "src", "qnvkit", "shim", "Qniverse")


def _run(tmp_path, package_dir_name):
    pkg = tmp_path / package_dir_name
    shutil.copytree(SHIM, pkg, ignore=shutil.ignore_patterns("__pycache__"))
    init = pkg / "__init__.py"
    init.write_text(init.read_text().replace("IS_LOCAL_STAND_IN = True", "IS_LOCAL_STAND_IN = False"))
    code = textwrap.dedent("""
        import qnvkit.qsdk_adapter as a
        from Qniverse.QniverseCircuit import QniverseCircuit, QuantumRegister
        from Qniverse.gates import h
        qc = QniverseCircuit(); q = QuantumRegister(1, 'q'); qc.add_register(q); qc.add_gate(h, q[0])
        print(a.IS_LIVE_QNIVERSE, a.QSDK_IMPORT_NAME, a.read_qasm(qc).count('h q[0];'))
    """)
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(tmp_path), os.path.join(ROOT, "src")]))
    out = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, cwd=str(tmp_path))
    assert out.returncode == 0, out.stderr
    return out.stdout.split()


def test_lowercase_install_is_found(tmp_path):
    assert _run(tmp_path, "qniverse") == ["True", "qniverse", "1"]


def test_camelcase_install_is_found(tmp_path):
    assert _run(tmp_path, "Qniverse") == ["True", "Qniverse", "1"]
