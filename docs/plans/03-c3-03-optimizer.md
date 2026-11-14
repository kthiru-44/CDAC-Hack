# Plan for QC-C3-03

Shared context, constraints, package layout and setup are in `00-overview-and-foundation.md` (read it first: Python 3.9 target, documented QSDK surface only, `src/qnvkit/` layout, interfaces).

## Problem 3 — QC-C3-03 (final)
- **API:** `optimize(qc, passes=None) -> OptimizeResult(circuit, report)`; default = mandatory set; unknown pass name → rejected with the valid list.
- **Mandatory passes (independent, individually testable):** `remove_identity`; `cancel_self_inverse` (x, y, z, h pairs); `cancel_cx` (same control and target).
- **Opt-in extras:** other self-inverse gates (`cz`, `swap`, `ccx`, …), inverse pairs (`s·sdg`, `t·tdg`), rotation merging (`rz/rx/ry/p/u1`, with correct periods for controlled rotations), run to fixed point.
- **Adjacency rule:** two gates cancel only if, on every wire they touch, they are consecutive, with identical operands in identical roles, and no barrier, measurement, reset, conditional or other gate between. Conditional gates are never rewritten. Barriers, measurements, resets, registers preserved; order of survivors stable; no gate ever added.
- **Report:** counts by type, total, depth before/after (shared `metrics.py`), rewrites per pass, warnings; "no improvement" is valid.
- **Evidence:** positive and negative test per rule (barrier/intervening gate blocks), 1,000 random-circuit equivalence fuzz, immutability test, one improving and one non-improving example, optional comparison with Qiskit's transpiler.

