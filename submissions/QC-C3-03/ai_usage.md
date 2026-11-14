# QC-C3-03 — AI / LLM Usage Declaration (Required by Rules §2.5)

> Hackathon Rules §2.5 permit the use of AI tools for code generation, debugging, research, architecture design, and documentation, **provided their use is transparently declared and rigorously reviewed**.

| Module / Scope | Scope of AI Assistance | Tool & Model | Human Reviewer |
|---|---|---|---|
| `docs/` (planning docs, strategy, templates) | Problem selection analysis, deliverable scaffolding, rule compliance review | Claude Code (`claude-sonnet-5-5`) | Thirukumaran & Yatin R |
| `docs/10-qsdk-probe.md`, `docs/09-qniverse-integration.md` | Video recording analysis (Sessions 1–3), QSDK API specification extraction, SDK interface probing, platform integration | Antigravity (`gemini-3.8-flash`) | Thirukumaran & Niharika J |
| `src/qnvkit/optimize/`, `tests/test_c3_*.py`, `examples/c3_demo.py`, `notebooks/c3_demo*.ipynb`, `docs/c3-03-user-guide.md` | QC-C3-03 causal wire adjacency DAG, rewrite passes (`remove_identity`, `cancel_self_inverse`, `cancel_cx`, `merge_rotations`), barrier safety boundaries, hypothesis fuzzing | Claude Code (`claude-sonnet-5-5`) & Antigravity | Yashwanth K & Niharika J |
| `docs/03-technical-approach.md`, `docs/04-performance-report.md`, `README.md` | Technical approach documentation (Deliverable #2), performance benchmarking, theoretical complexity analysis (Deliverable #3) | Antigravity (`gemini-3.8-flash`) | Full Team (Thirukumaran, Yatin R, Yashwanth K, Niharika J) |

### Verification Protocol
All code and mathematical statements produced with AI assistance were verified by:
1. Automated pytest test suite (701 / 701 passing tests).
2. Direct matrix unitary equivalence checks (Tr(U1† U2) / 2^n ≡ 1.0).
3. End-to-end execution in C-DAC Qniverse cloud environment and local standalone notebooks.
