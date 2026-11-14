# 07 — AI / LLM Usage Declaration (Required by Rules §2.5)

> Hackathon Rules §2.5 permit the use of AI tools for code generation, debugging, research, architecture design, and documentation, **provided their use is transparently declared and rigorously reviewed**.

| Module / Scope | Scope of AI Assistance | Tool & Model | Human Reviewer |
|---|---|---|---|
| `docs/` (planning docs, strategy, templates) | Problem selection analysis, deliverable scaffolding, rule compliance review | Claude Code (`claude-sonnet-5-5`) | Thirukumaran & Yatin |
| `docs/tutorial-sessions-documentation.md`, `docs/02-open-questions.md` | Video recording analysis (Sessions 1–3), OCR extraction of QSDK presentation slides, API documentation, SDK open questions resolution | Antigravity (`gemini-3.8-flash`) | Thirukumaran & Niharika J |
| `src/qnvkit/` (QSDK adapter, local stand-in, simulator matrices, decomposition rules, verification), `tests/test_c1_gate_basis_matrix.py`, `examples/c1_demo.py`, `notebooks/c1_demo.ipynb`, `docs/10-qsdk-probe.md`, `docs/c1-01-user-guide.md` | QC-C1-01 basis decomposition engine, Euler angle synthesis, unit tests, demo notebooks | Claude Code (`claude-fable-5-2`) | Thirukumaran |
| `src/qnvkit/transpile/`, `c2-03-qasm3-transpiler/`, `tests/test_c2_*.py`, `examples/c2_demo.py`, `notebooks/c2_demo*.ipynb` | QC-C2-03 OpenQASM 3.0 transpiler architecture, AST code generators (Qiskit 1.0+, Cirq 1.4+, CUDA-Q 0.8+, QSDK), cross-framework simulation tests | Claude Code (`claude-sonnet-5-5`) | Yatin & Yashwanth K |
| `src/qnvkit/optimize/`, `tests/test_c3_*.py`, `examples/c3_demo.py`, `notebooks/c3_demo*.ipynb`, `docs/c3-03-user-guide.md` | QC-C3-03 causal wire adjacency DAG, rewrite passes (`remove_identity`, `cancel_self_inverse`, `cancel_cx`, `merge_rotations`), barrier safety boundaries, hypothesis fuzzing | Claude Code (`claude-sonnet-5-5`) & Antigravity | Yashwanth K & Niharika J |
| `docs/03-technical-approach.md`, `docs/04-performance-report.md` | Technical approach documentation (Deliverable #2), performance benchmarking, theoretical complexity analysis (Deliverable #3) | Antigravity (`gemini-3.8-flash`) | Full Team (Thirukumaran, Yatin, Yashwanth K, Niharika J) |
