# QC-C1-01 — AI / LLM Usage Declaration (Required by Rules §2.5)

> Hackathon Rules §2.5 permit the use of AI tools for code generation, debugging, research, architecture design, and documentation, **provided their use is transparently declared and rigorously reviewed**.

| Module / Scope | Scope of AI Assistance | Tool & Model | Human Reviewer |
|---|---|---|---|
| `docs/` (planning docs, strategy, templates) | Problem selection analysis, deliverable scaffolding, rule compliance review | Claude Code (`claude-sonnet-5-5`) | Thirukumaran & Yatin R |
| `docs/10-qsdk-probe.md`, `docs/09-qniverse-integration.md` | Video recording analysis (Sessions 1–3), QSDK API specification extraction, SDK interface probing, platform integration | Antigravity (`gemini-3.8-flash`) | Thirukumaran & Niharika J |
| `src/qnvkit/` (QSDK adapter, local stand-in, simulator matrices, decomposition rules, verification), `tests/test_c1_gate_basis_matrix.py`, `examples/c1_demo.py`, `notebooks/c1_demo.ipynb`, `docs/10-qsdk-probe.md`, `docs/c1-01-user-guide.md` | QC-C1-01 basis decomposition engine, Euler angle synthesis, unit tests, demo notebooks | Claude Code (`claude-fable-5-2`) | Thirukumaran |
| `docs/03-technical-approach.md`, `docs/04-performance-report.md`, `README.md` | Technical approach documentation (Deliverable #2), performance benchmarking, theoretical complexity analysis (Deliverable #3) | Antigravity (`gemini-3.8-flash`) | Full Team (Thirukumaran, Yatin R, Yashwanth K, Niharika J) |

### Verification Protocol
All code and mathematical statements produced with AI assistance were verified by:
1. Automated pytest test suite (701 / 701 passing tests).
2. Direct matrix unitary equivalence checks (Tr(U1† U2) / 2^n ≡ 1.0).
3. End-to-end execution in C-DAC Qniverse cloud environment and local standalone notebooks.
