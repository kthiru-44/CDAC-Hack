# 04 — Performance Evaluation Report (Deliverable #3)

> Template. Rules §6.3: time and memory needs, computational complexity, circuit depth and gate count where relevant.

## Setup
Machine / Qniverse JupyterLab, library versions, simulators used.

## C1-01 — Profiling and decomposition
| Circuit | Basis | Gates before → after | Depth before → after | Runtime |
|---|---|---|---|---|
| | | | | |

Complexity: profiling O(g); decomposition O(g · d_max) where d_max is the largest gate expansion.

## C2-03 — Transpiler
| Test circuit | Target | Status | Max distribution difference vs source | Transpile time |
|---|---|---|---|---|
| | | | | |

Complexity: parse O(L) for source length L; generation O(g).

## C3-03 — Optimiser
| Test circuit | Gates before → after | Depth before → after | Rules applied | Equivalence check |
|---|---|---|---|---|
| (one where both improve, one where nothing improves) | | | | |

Complexity: one sweep O(g), repeated until no change, at most O(g) sweeps.

## Limitations
_Fill in._
