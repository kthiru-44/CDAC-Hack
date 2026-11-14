# QC-C2-03 user guide: OpenQASM 3 transpiler

```python
from qnvkit.transpile.api import transpile
results = transpile(source, targets=["qiskit", "cirq", "cudaq", "qniverse"], options={"verify": True})
results["cirq"].code      # standalone Python
results["cirq"].report    # structured report (status, warnings, notes, unsupported constructs with line/col, equivalence)
```

Invalid OpenQASM raises `QASMError` (a `ValueError`) with `.line` and `.col`. Unsupported but valid constructs never become
broken code: the report gets an entry with line and column, status becomes `ERROR`, the generated code stays valid Python and
omits that operation.

## Supported OpenQASM 3 subset
- Header, `include`, comments, `qubit[n] q;` / `qubit q;`, `bit[n] c;` / `bit c;`, OpenQASM 2 `qreg`/`creg`, `const` values.
- Standard gates plus the 40 QSDK gates; aliases `U/u`, `phase`, `cphase`, `cnot`, `CX`, `toffoli` are normalised.
- Register broadcasting, `for` loops (unrolled, negative steps allowed), parameter expressions (`pi`, `tau`, `euler`, `sin`, `ln`, ...; no attribute access).
- `gate` definitions (inlined, parameters allowed, work on any qubit); `gphase` (accepted, dropped; rejected under `ctrl`).
- Modifiers `inv @`, `pow(k) @`, `ctrl(n) @`, `negctrl(n) @`, in any order, also on custom gates. They are exact rewrites;
  a gate with no controlled/inverse/power form in the gate set is rejected with a location (for example `ctrl @ sx`, `pow(0.3) @ h`).
- `measure`, `reset`, `barrier`, `if (c == k)` and `if (c[i] == k)`. Only `==` is supported; `!=`, `<`, ... are rejected.
- Not supported (reported with location): `while`, `def`, `extern`, `delay`, `cal`/`defcal`, `input`/`output`.

## Gate mapping
| Gate | Qiskit | Cirq | CUDA-Q (kernel) | QSDK |
|---|---|---|---|---|
| 1-qubit Clifford+T, rx/ry/rz | same-named method | `cirq.X/H/S/T...`, `**-1` for dagger, `cirq.rx` | `h(q)`, `s.adj(q)`, `rx(a, q)` | gate object |
| p, u1 | `p` | `ZPowGate(a/pi)` | `r1(a, q)` | native |
| u2, u3 | `u` | decomposed (rz, ry) | `u3(...)` | native |
| sx, sxdg | native | `X**0.5` | decomposed | decomposed to `u3` (not a QSDK gate) |
| cx cy cz ch | native | native / `controlled_by` | `x.ctrl(c, t)` ... | native |
| cp, cu1 | `cp` | `CZPowGate(a/pi)` | `r1.ctrl(a, c, t)` | native |
| crx cry crz | native | `controlled_by` | `rx.ctrl(a, c, t)` ... | native |
| cs ct csdg ctdg | native / `cp` | `controlled_by` | `s.ctrl`, `t.ctrl`, `r1.ctrl(-pi/2..)` | native |
| cu3, cu2, cu | `cu` | decomposed | `u3.ctrl` / decomposed | `cu3` native; `cu2` native; `cu` decomposed |
| ccx, c3x-c5x, cswap | `ccx`, `mcx`, `cswap` | `CCNOT`, `controlled_by`, `CSWAP` | `x.ctrl([...], t)`, `swap.ctrl` | native |
| barrier | `qc.barrier` | omitted (note) | omitted (note) | span of two qubits per register; a one-qubit barrier is omitted (note) |

"Decomposed" uses the C1 decomposer; the report lists one note per gate type. Decompositions are exact for multi-qubit
gates and equal up to global phase for single-qubit gates.

QSDK specifics: `QniverseCircuit()` takes no arguments; the generated code imports only the QSDK (`Qniverse` or `qniverse`).
Register names must be alphabetic and may not equal a gate name, so other names are renamed (noted in the report).
Bit-level conditions on registers larger than one bit, and conditional measure/reset, are reported as unsupported.

## Conditions and bit order
- Qiskit: `with qc.if_test((creg, value))` or `((creg[i], value))`.
- Cirq: per-bit measurement keys `c_0`, `with_classical_controls(sympy.Eq(Symbol('c_0'), 1), ...)`. A bit tested before it was ever measured is 0: a "must be 0" term is dropped, a "must be 1" operation is skipped with a warning.
- CUDA-Q: `c_0 = mz(q[0])`, nested `if c_0:` / `if not c_0:`. A kernel with measurements returns `list[bool]` (all classical bits) and is run with `cudaq.run`; CUDA-Q 0.16 no longer allows `cudaq.sample` on kernels that branch on measurements.
- Conditional measurement is unsupported on Cirq, CUDA-Q and the QSDK.
- Bit order: qubit `q[i]` / classical bit `i` is bit `i` (little-endian). Printed bitstrings cover all classical bits with classical bit 0 right-most. Cirq state vectors are converted with an explicit qubit order; CUDA-Q's index order is calibrated at runtime with a one-gate circuit.

## Verification (`options={"verify": True}`)
- Static circuits: each target's generated code is executed and its state vector compared with the reference simulator (fidelity). The QSDK route is `build_circuit()` -> `qc.qasm()` -> reference simulator.
- Dynamic circuits (conditions, reset, gates after a measurement): the reference simulator cannot model them, so Qiskit (Aer), Cirq and CUDA-Q are sampled (4000 shots, seed 1234) and compared pairwise by total variation distance (tolerance 0.05). The QSDK stand-in is not sampled for these.
- A missing framework or a check that did not run is reported `executed: False` with the reason; `equivalence_verified` stays `None`.
- The QSDK check runs against the local stand-in unless the real Qniverse SDK is importable; the report says which.

## Versions tested
qiskit 2.6.2, qiskit-aer 0.18.2, cirq-core 1.7.0, cudaq 0.16.0, Python 3.12 (all four frameworks) and Python 3.9 (core only, framework tests skipped).

## Known limitations
- `pow(k)` with non-integer k works only for a single rotation/phase gate (angle scaling) or the exact roots `z->s->t`, `x->sx`.
- `if` conditions on `!=`, `<`, `>`; `while`; subroutines; timing; pulse-level constructs.
- Barriers are dropped on Cirq and CUDA-Q.
- The reference simulator ignores conditions, so dynamic circuits are compared statistically, not exactly.
- Nothing was run on the real Qniverse platform; only the local stand-in.
