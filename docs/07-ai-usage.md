# 07 — AI / LLM Usage Declaration (required by rules §2.5)

The rules allow AI tools for coding, debugging, research, documentation and review, **provided their use is declared**.

| Where | What it was used for | Tool / model | Reviewed by |
|---|---|---|---|
| `docs/` (planning docs, templates) | Problem selection, planning docs, documentation scaffolding | Claude Code (Claude Sonnet 5.5, `claude-sonnet-5-5`) | |
| `docs/tutorial-sessions-documentation.md`, `docs/02-open-questions.md` | Video recordings analysis (Sessions 1-3), OCR extraction of QSDK slides, complete API documentation, SDK open questions resolution | Antigravity (Gemini 3.8 Flash) | |
| `src/qnvkit/` (QSDK adapter, local stand-in, simulator matrices, decomposition rules, verification), `tests/test_c1_gate_basis_matrix.py`, `examples/c1_demo.py`, `notebooks/c1_demo.ipynb`, `docs/10-qsdk-probe.md`, `docs/c1-01-user-guide.md` | Review of C1-01, bug fixes, tests, demo and documentation | Claude Code (Claude Fable 5.2, `claude-fable-5-2`) | |
| `docs/plans/` | Implementation plans | Claude Code (Claude Sonnet 5.5 and Claude Fable 5.2) | |
| | | | |

Add a row whenever AI helps with code or text. Note which files or functions it touched.
