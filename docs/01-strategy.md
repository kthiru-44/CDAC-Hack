# 01 — Strategy: rules digest and how we maximise the score

Source: `hackathon_rules.pdf`. If the announcements on the day differ, they win.

## Hard rules (fail any one and we're out)
- **Working proof of concept required.** A slides-only concept is rejected.
- Must be **quantum** and must **use Qniverse platform or Qniverse SDK**.
- Log in to Qniverse **only with the registered email ID** (that account holds the credits).
- Open-source libraries are allowed (install locally or in Qniverse JupyterLab) but must be **shown working with the Qniverse SDK**.
- AI/LLM tools are allowed but **must be declared**: where they were used and which models → `07-ai-usage.md`.
- Submit **all** source code and docs. C-DAC holds the rights to the submitted documentation.

## Scoring
**By problem class (checkpoints)**
| Class | When | Weight |
|---|---|---|
| 1 | Checkpoint 1 (~3 h in) | 20% |
| 2 | Checkpoint 2 (mid-event) | 30% |
| 3 (medium–hard) | Final submission | 50% |

**Evaluation criteria**
| Criterion | Weight | How we win it |
|---|---|---|
| Product and application delivery | 40% | Working optimiser on Qniverse with measured before/after results |
| Judges' common scoring sheet | 35% | Clear novelty: verification, noise-aware cost, benchmark vs Qiskit O3 |
| Presentation | 15% | Visual before/after (circuit diagrams, histograms, benchmark table) |
| Viva voce | 10% | Every team member can explain pass complexity and the equivalence proof |

**Open-innovation bonus:** up to **+20%** under product delivery if we propose our own challenge.
Pitch it at the start, Checkpoint 1 or Checkpoint 2. The judges then place it in Class 1, 2 or 3.

## Our plan
1. **Pitch QOpt (verified compiler: optimise, convert, verify on many simulators) as open innovation at the start** (`06-proposal.md`) and aim for Class 3.
2. **Fallback:** if a published Class 3 problem is in domain 2 or 3, map QOpt onto it.
3. **Don't skip Classes 1 and 2.** One or two members solve published Class 1 and 2 problems for the early 50%.
4. **Early feedback:** use Checkpoints 1 and 2 to show QOpt progress to the judges and adjust course.

## How we differ from other domain-2 teams
Most teams will run `transpile(optimization_level=3)` and report "depth went down". We add:
1. **Verified:** every optimised circuit comes with an equivalence certificate.
2. **Benchmarked:** compared against Qiskit O3, pytket and PyZX on a standard suite.
3. **Noise-aware:** we optimise *estimated fidelity*, not just depth, using Qniverse's own noise parameters.
4. **Measured on Qniverse:** before/after runs on Qniverse noisy simulators show real success-probability gains.
5. **Cross-simulator verified conversion:** round-trip framework conversion checked by differential testing on many simulators (domain 3).
6. **Integrated:** QASM 2.0 in and out, so it slots into Qniverse's composer and its 7-framework converter.

## Internship angle (C-DAC)
- Ship it as a **pip-installable package** with a README and tests, so C-DAC could merge it.
- Talk to the C-DAC representatives early and ask what Qniverse users struggle with.
- At the end, get the judges' names and contacts and follow up within a week with the repo link.
