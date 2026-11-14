# 03 — Detailed Implementation Plan for QC-C3-03
**Problem Title:** QC-03-03 — Quantum Circuit Optimization Using QSDK  
**Class:** Class III (Final Checkpoint — 50% of class evaluation)  
**Status:** Ready for Implementation  

---

## 1. Problem Statement & Scope

### 1.1 Objective
Build an optimization module for the C-DAC QSDK that accepts a `QniverseCircuit` (or `CircuitIR`), applies a documented set of safe local rewrite rules, and returns a new, valid `QniverseCircuit`.

The module must:
1. Implement a reusable, modular set of circuit rewrite passes.
2. Calculate metrics (gate counts by type, total count, scheduled depth) consistently before and after optimization using the shared [`metrics.py`](../src/qnvkit/metrics.py) module.
3. Provide rigorous correctness tests for every implemented rewrite rule, including negative tests (barriers, measurements, and intervening operations must prevent cancellation).
4. Maintain a non-mutating guarantee: the input circuit object is never modified.
5. Provide evidence that all supported transformations preserve exact quantum circuit behavior (unitary equivalence up to global phase, statevector fidelity $\ge 1 - 10^{-6}$, and measurement distribution TVD $\approx 0$).

### 1.2 Evaluation Weight
Class III carries **50% of the class evaluation** (and 40% overall Product Delivery). The implementation must be robust, safe, mathematically provable, and fully compliant with C-DAC's documented QSDK API.

---

## 2. Theoretical Foundations & Rewrite Rules

### 2.1 The Wire-Adjacency Causal Model
A fundamental flaw in naive circuit optimizers is string or array replacement: scanning a flat list of gates and cancelling $G_1$ and $G_2$ without verifying if other gates executed on those wires in the meantime.

In `qnvkit.optimize`, we use a **Causal Wire Adjacency Graph**:
* For each qubit wire $q \in \{0, \dots, n-1\}$, we maintain an ordered sequence of events.
* Gate $A$ and Gate $B$ are **causally adjacent** if and only if:
  $$\forall q \in \text{wires}(A), \quad \text{next\_op}(q, A) = B$$
* If there is **any** intervening operation on wire $q$ between $A$ and $B$:
  - A `barrier` $\to$ **BLOCKS cancellation**.
  - A `measure` or `reset` $\to$ **BLOCKS cancellation**.
  - A non-commuting unitary gate $\to$ **BLOCKS cancellation**.
  - A classical condition (`if(c==k)`) $\to$ **BLOCKS cancellation**.
* This guarantees that two gates cancel if and only if they are physically and temporally adjacent on their respective qubits.

### 2.2 Mandatory Rewrite Passes (Independently Testable)
1. **`remove_identity`:**
   - Explicit `id` operations on any wire: $I \to \emptyset$.
   - Trivial rotation gates with angle $\theta \equiv 0 \pmod{2\pi}$:
     - $R_x(0) \to \emptyset$
     - $R_y(0) \to \emptyset$
     - $R_z(0) \to \emptyset$
     - $P(0), U_1(0) \to \emptyset$
     - $U_3(0, 0, 0) \to \emptyset$
2. **`cancel_self_inverse`:**
   - Consecutive identical self-inverse single-qubit gates on the same wire:
     - $X \cdot X = I \to \emptyset$
     - $Y \cdot Y = I \to \emptyset$
     - $Z \cdot Z = I \to \emptyset$
     - $H \cdot H = I \to \emptyset$
3. **`cancel_cx`:**
   - Consecutive identical CNOT gates with matching control and target wires:
     - $CX(c, t) \cdot CX(c, t) = I \to \emptyset$
     - *Note:* If control and target are reversed ($CX(c, t) \cdot CX(t, c)$), they do **not** cancel!

### 2.3 Opt-in Extra Passes (High-Value Standout Features)
4. **`cancel_extended_self_inverse`:**
   - Consecutive identical multi-qubit self-inverse gates:
     - $CZ(c, t) \cdot CZ(c, t) = I \to \emptyset$
     - $SWAP(a, b) \cdot SWAP(a, b) = I \to \emptyset$
     - $CH(c, t) \cdot CH(c, t) = I \to \emptyset$
     - $CCX(c_1, c_2, t) \cdot CCX(c_1, c_2, t) = I \to \emptyset$
     - $CSWAP(c, t_1, t_2) \cdot CSWAP(c, t_1, t_2) = I \to \emptyset$
5. **`cancel_inverse_pairs`:**
   - Consecutive adjoint pairs:
     - $S \cdot S^\dagger = I$, $S^\dagger \cdot S = I \to \emptyset$
     - $T \cdot T^\dagger = I$, $T^\dagger \cdot T = I \to \emptyset$
     - $CS \cdot CS^\dagger = I$, $CS^\dagger \cdot CS = I \to \emptyset$
     - $CT \cdot CT^\dagger = I$, $CT^\dagger \cdot CT = I \to \emptyset$
6. **`merge_rotations`:**
   - Consecutive rotations along the same axis on the same wire:
     - $R_z(\alpha) \cdot R_z(\beta) = R_z(\alpha + \beta)$
     - $R_x(\alpha) \cdot R_x(\beta) = R_x(\alpha + \beta)$
     - $R_y(\alpha) \cdot R_y(\beta) = R_y(\alpha + \beta)$
     - $P(\alpha) \cdot P(\beta) = P(\alpha + \beta)$
     - If $(\alpha + \beta) \equiv 0 \pmod{2\pi}$, the merged gate is eliminated completely!
     - Also merges matching controlled rotations: $CR_z(\alpha) \cdot CR_z(\beta) = CR_z(\alpha + \beta)$.
7. **`run_to_fixed_point`:**
   - Iteratively executes the selected pass pipeline until no further gate reductions occur (or max 10 iterations reached).

---

## 3. Package Architecture & File Layout

```
src/qnvkit/optimize/
├── __init__.py           # Exports optimize(), OptimizationPass, PASS_REGISTRY
├── causal_dag.py         # Wire-adjacency event graph & barrier collision checker
├── passes.py             # Pure, modular implementation of each rewrite pass
└── optimizer.py          # Master orchestrator, configuration parser, and reporting
```

### 3.1 Public Interface Contract
```python
def optimize(
    circuit: Union[QniverseCircuit, CircuitIR],
    passes: Optional[List[str]] = None,
    fixed_point: bool = False
) -> OptimizeResult:
    """
    Optimizes a QniverseCircuit or CircuitIR using documented safe rewrite passes.
    
    Parameters:
      circuit: Input quantum circuit (strictly non-mutated).
      passes: Optional list of pass names. Default:
              ["remove_identity", "cancel_self_inverse", "cancel_cx"]
      fixed_point: If True, loops passes until no further reduction.
      
    Returns:
      OptimizeResult with:
        - circuit: New optimized QniverseCircuit
        - ir: Optimized CircuitIR
        - before: ProfileReport before optimization
        - after: ProfileReport after optimization
        - passes_applied: Tuple of applied pass names
        - reduction_percentage: Gate count reduction %
        - warnings: List of warning strings
    """
```

---

## 4. Phase-by-Phase Implementation Steps

### Phase 1: Causal DAG & Wire Adjacency Engine (`causal_dag.py`)
1. Ingest `CircuitIR`.
2. Build per-wire event chains: `wire_ops[q] = [op_index_1, op_index_2, ...]`.
3. Provide helper: `find_adjacent_pair(ir, op_predicate)`:
   - Finds two operations $op_A$ at index $i$ and $op_B$ at index $j$ ($i < j$).
   - Verifies that $\forall q \in \text{qubits}(op_A)$, there are **no intervening operations** on wire $q$ between index $i$ and $j$.
   - If any wire has a `barrier`, `measure`, `reset`, or other gate in between, rejection is instant.

### Phase 2: Modular Rewrite Passes (`passes.py`)
1. Implement `remove_identity(ir: CircuitIR) -> Tuple[CircuitIR, int]`.
2. Implement `cancel_self_inverse(ir: CircuitIR) -> Tuple[CircuitIR, int]`.
3. Implement `cancel_cx(ir: CircuitIR) -> Tuple[CircuitIR, int]`.
4. Implement `cancel_extended_self_inverse(ir: CircuitIR) -> Tuple[CircuitIR, int]`.
5. Implement `cancel_inverse_pairs(ir: CircuitIR) -> Tuple[CircuitIR, int]`.
6. Implement `merge_rotations(ir: CircuitIR) -> Tuple[CircuitIR, int]`.
7. Each pass returns a new `CircuitIR` and the count of eliminated gates.

### Phase 3: Master Optimizer Pipeline (`optimizer.py`)
1. Validate pass names against `PASS_REGISTRY`. Reject unknown pass names with an informative message.
2. Take snapshot of input circuit fingerprint (`initial_fingerprint = ir.fingerprint()`).
3. Compute `profile_before = profile(ir)`.
4. Run configured passes (single-pass or loop to fixed point).
5. Assert `ir.fingerprint() == initial_fingerprint` (guarantee non-mutation).
6. Compute `profile_after = profile(optimized_ir)`.
7. Verify mathematical equivalence via `sim.py` ($|Tr(U_{\text{orig}}^\dagger U_{\text{opt}})| / 2^n \equiv 1.0$).
8. Reconstruct fresh `QniverseCircuit` via `to_qniverse(optimized_ir)`.
9. Return `OptimizeResult`.

### Phase 4: Test Suite (`tests/test_c3_optimizer.py`)
1. **Unit tests for every pass:**
   - Identity removal: `id`, `rx(0)`, `rz(2*pi)`.
   - Self-inverse pairs: $X-X$, $H-H$, $Z-Z$, $Y-Y$.
   - CX-CX pairs: $CX(0,1) \cdot CX(0,1)$.
   - Extended: $CZ-CZ$, $SWAP-SWAP$, $CCX-CCX$.
   - Inverse pairs: $S \cdot S^\dagger$, $T \cdot T^\dagger$.
   - Rotation merging: $R_z(0.3) \cdot R_z(0.5) \to R_z(0.8)$; $R_z(\pi/2) \cdot R_z(-\pi/2) \to \emptyset$.
2. **Negative Tests (Safety Guardrail Verification):**
   - Intervening gate blocks cancellation ($X(0) \to Z(0) \to X(0) \ne Z(0)$).
   - Intervening gate on one wire of $CX$ blocks cancellation ($CX(0,1) \to X(0) \to CX(0,1)$).
   - Intervening barrier blocks cancellation ($X(0) \to \text{barrier} \to X(0)$).
   - Intervening measurement blocks cancellation ($X(0) \to \text{measure} \to X(0)$).
   - Intervening reset blocks cancellation ($X(0) \to \text{reset} \to X(0)$).
   - Conditional gate blocks cancellation (`if(c==1) X(0) ...`).
3. **No-Improvement & Immutability:**
   - Optimal circuit with no redundancies passes through with 0 gates added and status `NO_OPTIMIZATION_POSSIBLE`.
   - Input circuit QASM is identical before and after.
4. **Fuzzing Equivalence:**
   - 1,000 randomized quantum circuits generated with redundancies; assert 100% unitary equivalence after optimization.

### Phase 5: Demonstration & Deliverables
1. [`examples/c3_demo.py`](../examples/c3_demo.py): Standalone script displaying before/after circuit profiles, reduction percentage, and barrier negative test.
2. [`notebooks/c3_demo.ipynb`](../notebooks/c3_demo.ipynb) and [`notebooks/c3_demo_standalone.ipynb`](../notebooks/c3_demo_standalone.ipynb): Interactive Jupyter notebooks for Qniverse JupyterLab.
3. User documentation and limitations note in `docs/c3-03-user-guide.md`.

---

## 5. Verification Commands

```bash
# 1. Run C3 optimizer unit tests
.venv39/bin/pytest -q --tb=short tests/test_c3_optimizer.py

# 2. Run full test suite across all 3 problems
.venv39/bin/pytest -q --tb=short

# 3. Run standalone C3 demo
.venv39/bin/python examples/c3_demo.py
```
