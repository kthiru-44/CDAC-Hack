# QC-C3-03 — Quantum Circuit Optimization Using QSDK
**PESU – C-DAC Quantum Hackathon: user guide**

`qnvkit.optimize` takes a `QniverseCircuit` (or a `CircuitIR`), removes redundant gates with a documented set of
local rewrite rules, and returns a **new** `QniverseCircuit` with a lower gate count and scheduled depth.
The input is never modified, and the result is checked to implement the same unitary.

---

## 1. Quick start

```python
import qnvkit.qsdk_adapter                      # import before Qniverse: selects the real QSDK or the local stand-in
from qnvkit.optimize import optimize
from Qniverse.QniverseCircuit import QniverseCircuit, QuantumRegister
from Qniverse.gates import h, cx, rz

qc = QniverseCircuit()
q = QuantumRegister(2, "q")
qc.add_register(q)
qc.add_gate(h, q[0]); qc.add_gate(h, q[0])                   # H H        -> removed
qc.add_gate(cx, q[0], q[1]); qc.add_gate(cx, q[0], q[1])     # CX CX      -> removed
qc.add_gate(rz(0.3), q[1]); qc.add_gate(rz(0.5), q[1])       # Rz Rz      -> Rz(0.8)

result = optimize(qc, passes="all", fixed_point=True)
print(result.summary())
optimized_qc = result.circuit                                # new QniverseCircuit; qc is unchanged
print(optimized_qc.qasm())
```

```
--- Optimization Report ---
Passes: remove_identity, cancel_self_inverse, cancel_cx, cancel_extended_self_inverse, cancel_inverse_pairs, merge_rotations (2 rounds)
Gates: 6 -> 1 (5 removed, 83.33%)
Depth: 5 -> 1 (80.0%)
Operation counts after: {'rz': 1}
Equivalence: verified (equal up to global phase)
```

---

## 2. API

### `optimize(circuit, passes=None, fixed_point=False) -> OptimizeResult`

| Argument | Values | Meaning |
|---|---|---|
| `circuit` | `QniverseCircuit` or `CircuitIR` | The circuit to optimize. Never modified. |
| `passes` | `None` (default) | The three mandatory passes, in order: `remove_identity`, `cancel_self_inverse`, `cancel_cx`. |
| | `"all"` | Every pass in section 3, mandatory ones first. |
| | list of names | Exactly those passes, in the order given. |
| `fixed_point` | `False` (default) | Run the pass list once. |
| | `True` | Repeat the pass list until a full round removes nothing. Needed for nested redundancy such as `X H H X`: round 1 removes `H H`, round 2 removes the now-adjacent `X X`. |

Raises `ValueError` for a `None` circuit, an empty pass list or an unknown pass name (the message lists the valid names).

### `OptimizeResult`

| Field | Meaning |
|---|---|
| `circuit` | New optimized `QniverseCircuit`. |
| `ir` | The same circuit as `CircuitIR`. |
| `before`, `after` | `ProfileReport` of input and output: `total_gates`, `depth`, `gate_counts`, ... |
| `reduction_percentage` | Drop in gate count, in percent. |
| `depth_reduction_percentage` | Drop in scheduled depth, in percent. |
| `gates_removed` | `before.total_gates - after.total_gates`. |
| `passes_applied`, `rounds` | The pass list used and how many times it was applied. |
| `equivalence_verified` | `True`: output checked equal to the input up to global phase. `None`: check not run (see `warnings`). `False`: check failed and the original circuit was returned. |
| `warnings` | Tuple of messages; empty on a normal run. |
| `summary()` / `to_dict()` | Readable report / JSON-ready dictionary. |

---

## 3. Rewrite passes

**Mandatory (default)**

| Pass | Rule |
|---|---|
| `remove_identity` | Removes `id`; a rotation whose angle is a multiple of its period; `u3` with all angles multiples of $2\pi$. |
| `cancel_self_inverse` | $X X$, $Y Y$, $Z Z$, $H H \to \emptyset$ on the same qubit. |
| `cancel_cx` | $CX(c,t)\,CX(c,t) \to \emptyset$, same control and same target. `CX(0,1) CX(1,0)` is kept. |

**Opt-in (`passes="all"` or by name)**

| Pass | Rule |
|---|---|
| `cancel_extended_self_inverse` | $CZ\,CZ$, $SWAP\,SWAP$, $CH\,CH$, $CCX\,CCX$, $CSWAP\,CSWAP \to \emptyset$. Operand order is ignored only where the gate is symmetric (CZ, SWAP, the two CCX controls, the two CSWAP targets). |
| `cancel_inverse_pairs` | $S\,S^\dagger$, $T\,T^\dagger$, $CS\,CS^\dagger$, $CT\,CT^\dagger \to \emptyset$, in either order. |
| `merge_rotations` | $R(\alpha)\,R(\beta) \to R(\alpha+\beta)$ for `rx ry rz p u1 crx cry crz cp cu1` on the same qubits; the pair disappears when $\alpha+\beta$ is a multiple of the period. |

**Rotation periods.** `rx`, `ry`, `rz` equal $-I$ at $2\pi$, which is only a global phase, so their period is $2\pi$
(as for `p`, `u1`, `cp`, `cu1`). Once controlled, that $-1$ becomes a relative phase on the control qubit:
`crz(2π)` is a `Z` on the control. `crx`, `cry`, `crz` are therefore removed only at multiples of $4\pi$.

---

## 4. When a rewrite is allowed (the causal wire model)

List order is not physical order: in `X q0; H q1; X q0` the two X gates are neighbours on wire `q0`. The optimizer
keeps, for each qubit, the ordered list of operations touching it (`CausalWireTracker`, `optimize/causal_dag.py`).
Two gates $A$, $B$ are **strictly adjacent** when they act on the same qubits and, on every one of those wires, $B$ is
the very next operation after $A$. Only strictly adjacent pairs are rewritten. Consequently a pair is **kept** when:

1. a `barrier` lies between them on a shared wire;
2. a `measure` or `reset` lies between them;
3. any other gate touches one of their wires in between;
4. either gate is classically conditioned (`if (c == k)`).

Gates on other wires do not block a rewrite, so `X q0; H q1; X q0; H q1` reduces to nothing.

---

## 5. Safety guarantees

- **Input untouched.** The IR is immutable and a fingerprint of the input is compared before and after.
- **Never more gates.** Every pass only removes gates or replaces two by one.
- **Checked result.** The optimized circuit is compared with the input: full unitary
  $|\mathrm{Tr}(U_{orig}^\dagger U_{opt})| / 2^n \ge 1 - 10^{-5}$ up to 8 qubits, output states for random product
  inputs from 9 to 20 qubits. Above 20 qubits the check is skipped and `equivalence_verified` is `None`.
- **Fail-safe.** If the check fails, the original circuit is returned with a warning; a wrong circuit is never returned.

---

## 6. Running it

```bash
# Demo script (add --live to also submit the optimized circuit as one Qniverse job; needs QNIVERSE_API_KEY)
.venv39/bin/python examples/c3_demo.py

# Tests
.venv39/bin/pytest -q tests/test_c3_optimizer.py tests/test_c3_fuzz.py
```

**Notebooks (JupyterLab / Qniverse):**
- `notebooks/c3_demo_standalone.ipynb`: single file with `qnvkit` embedded. Upload it alone and run all cells.
- `notebooks/c3_demo.ipynb`: same demo, expects the repository's `src/` next to it.
- The last cell runs the unoptimized and the optimized circuit for 1024 shots and compares the distributions. With
  `QNIVERSE_API_KEY` set both are submitted as Qniverse jobs; otherwise they are simulated locally. The output states
  where each ran.
- After changing `src/qnvkit` or a source notebook, rebuild the standalone files: `python tools/build_standalone_notebook.py`.

---

## 7. Adding a pass

A pass is a pure function `CircuitIR -> (new CircuitIR, gates_removed)`. For a pair rule, write the match
condition and reuse the helper, then register the pass:

```python
# src/qnvkit/optimize/passes.py
def cancel_cy(ir):
    """Cancels adjacent CY pairs with the same control and target."""
    def match(a, b):
        return a.name == "cy" and b.name == "cy" and a.qubits == b.qubits
    return _cancel_adjacent_pairs(ir, match)

PASS_REGISTRY["cancel_cy"] = cancel_cy
```

Adjacency, barriers, measurements and conditions are handled by the helper; the match function only decides
whether two already-adjacent gates cancel.

---

## 8. Known limitations

1. **No commutation rules.** Only strictly adjacent gates are rewritten. `Z q0; CX q0,q1; Z q0` is kept although
   the Z gates commute through the control of the CX.
2. **No resynthesis.** Different gate types are not combined (`H Z H` stays as is; `S S` is not turned into `Z`;
   `rz` and `p` are not merged with each other).
3. **Conditioned gates are never cancelled or merged**, to keep classical feed-forward behaviour unchanged.
4. **One-qubit barriers** cannot be represented by the QSDK and are dropped when the result is converted back to a
   `QniverseCircuit`; they still block rewrites during optimization.
