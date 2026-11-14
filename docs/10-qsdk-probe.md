# 10 — QSDK Probe Findings & Platform Architecture

**Date:** 2026-11-14  
**Author:** Antigravity (PesU C-DAC Quantum Hackathon Team)  
**Status:** Complete  

---

## 1. Package Availability & Installation Probe

- **PyPI Status:** Probed `pip install qniverse` and `pip install Qniverse` against public PyPI. Both return:
  ```
  ERROR: Could not find a version that satisfies the requirement qniverse (from versions: none)
  ERROR: No matching distribution found for qniverse
  ```
- **Platform Reality:** The `Qniverse` Python package is proprietary C-DAC software pre-installed in the Qniverse JupyterLab cloud environment (`Python 3.9.13`, `Qiskit 1.1.1`, `Aer 0.14.2`, `NumPy 1.26.4`).
- **How we handle it:**
  1. `src/qnvkit/qsdk_adapter.py` imports the official `Qniverse` package when it exists (Qniverse JupyterLab).
  2. When it does not exist, a **local stand-in** (`src/qnvkit/shim/Qniverse/`) is put on `sys.path`. It implements the same *documented* calls (gate objects, `q[i]` operands) and rejects any other call style, so local tests exercise exactly the calls the real SDK receives.
  3. The stand-in is **not** the QSDK and has not been compared against it. Its job API simulates locally and labels every result as "not executed on Qniverse".
  4. **Still to confirm inside Qniverse JupyterLab:** whether `qc.qasm()` returns or prints the text (the adapter handles both), the exact QASM spelling of each gate, whether one `barrier` call accepts several qubits (the adapter falls back to one call per qubit), and the result format and bit order of `fetch_job_result`.

---

## 2. Documented QSDK API Surface

### 2.1 Imports & Casing
```python
# Documented imports use CamelCase module name:
from Qniverse.QniverseCircuit import *
from Qniverse.gates import *
from Qniverse.backend import Backend
from Qniverse.api import run, fetch_job_result, job_status, transpiled_code, credit_balance, get_backend
```

### 2.2 Circuit Construction
- **Registers:**
  ```python
  qreg = QuantumRegister(2, 'q')
  creg = ClassicalRegister(2, 'c')
  qc = QniverseCircuit()
  qc.add_register(qreg)
  qc.add_register(creg)
  ```
- **Gate application (gate objects from `Qniverse.gates`, bit objects from the registers):**
  ```python
  from Qniverse.gates import *
  qc.add_gate(h, qreg[0])
  qc.add_gate(rx(np.pi / 2), qreg[1])          # parameterised gates are called with their angles
  qc.add_gate(cx, qreg[0], qreg[1])            # the last qubit is the target
  qc.add_gate(ccx, qreg[0], qreg[1], qreg[2])
  qc.add_gate(measure, qreg[0], creg[0])       # exactly one Qubit then one Clbit
  qc.add_gate(reset, qreg[0])
  qc.add_gate(barrier, qreg[0])
  qc.add_conditional_gate(creg, 1, h, qreg[1]) # value: int or binary string; not measure/barrier/reset
  qc.measure_all()                             # fills existing classical registers, then creates `meas`
  ```
- **Inspection and export:**
  - `qc.qasm()`: OpenQASM 2.0 of the circuit. This is the only documented way to read operations back.
  - `qc.list_gates()`: lists the gates the SDK offers.
  - `qc.draw("file.svg")`, `qc.download_circuit()`.

### 2.3 The 40 Documented Gates
| Category | Gates |
|---|---|
| **1-Qubit Unitary (16)** | `id`, `x`, `y`, `z`, `h`, `s`, `t`, `sdg`, `tdg`, `p`, `rx`, `ry`, `rz`, `u1`, `u2`, `u3` |
| **2-Qubit Unitary (16)** | `cx`, `cy`, `cz`, `ch`, `swap`, `cs`, `ct`, `csdg`, `ctdg`, `cp`, `crx`, `cry`, `crz`, `cu1`, `cu2`, `cu3` |
| **Multi-Qubit Unitary (5)** | `ccx`, `cswap`, `c3x`, `c4x`, `c5x` |
| **Non-Unitary / Meta (3)** | `reset`, `measure`, `barrier` |

*Note for QC-C1-01:* A "basis gate set" in C1-01 is strictly a subset of these 40 documented names.

---

## 3. Backend Hierarchy & Execution Constraints

### 3.1 Strict Configuration Order
The backend builder pattern must be invoked in exact sequence:
```python
# token MUST be defined in global scope or environment
token = os.environ["QNIVERSE_API_KEY"]   # must be a global named `token` before Backend()

backend = Backend()
backend.processor("CPU")            # 1. Processor: "CPU" or "GPU" (see Backend.get_processor())
backend.hpc("QACC_Cluster")         # 2. HPC: "QACC_Cluster", "Param_Utkarsh", etc.
backend.simulator("qasm_simulator") # 3. Simulator name
```
Invoking these methods out of order raises a `ValueError`.

### 3.2 Dynamic Introspection
```python
processors = Backend.get_processor()
hpcs = Backend.get_hpc("CPU")
simulators = Backend.get_simulator("CPU", "QACC_Cluster")
```

### 3.3 Available Simulators & Credit Rates
| Processor | HPC Resource | Simulator | Credit Deduction |
|---|---|---|---|
| CPU | `QACC_Cluster` | `qasm_simulator` | 5 credits |
| CPU | `QACC_Cluster` | `aer_simulator_statevector` | 5 credits |
| CPU | `QACC_Cluster` | `quest_simulator` | 5 credits |
| CPU | `QACC_Cluster` | `cirq_simulator` | 5 credits |
| CPU | `QACC_Cluster` | `qulacs_multicpu_simulator` | 5 credits |
| GPU | `Param_Utkarsh` | `nvidia_cudaq_statevector_simulator` | 10–15 credits |

**Critical Constraint:** All submitted circuits must contain at least one `measure` operation to be accepted by the Qniverse execution engine.

---

## 4. Live REST API Probe (Verified)

Direct verification against the Qniverse cloud REST API:
- Endpoint: `https://qniverse.in/wp-json/qacc/v1/backends`
- Status: `200 OK`
- Active API Key: Loaded securely from `.env` via `os.environ`.
