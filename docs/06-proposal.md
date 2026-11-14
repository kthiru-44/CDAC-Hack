# 06 — Open-Innovation Proposal (one page, for the judges)

**Title:** QOpt: A Verified Compiler for Qniverse (optimise, convert, and prove it on many simulators)
**Domains:** 2 (circuit optimisation and compilation) + 3 (transpilation and framework interoperability), with 1 (profiling) as a by-product
**Requested class:** Class 3

## Problem
Qniverse lets users build a circuit once and generate code for 7 frameworks, and it offers about 25 simulators.
But the generated code is one-way (Qiskit, Cirq and CudaQ views are read-only), nothing checks that the
frameworks and simulators agree on the result, and the circuit is run as written, redundant gates included.
Silent mismatches (bit-order, global phase, gate-definition differences) and avoidable two-qubit gates
cost users correctness and success probability, and nothing tells them.

## What we will build
1. **Converter:** OpenQASM 2.0 as the common format, with round-trip conversion to and from Qiskit, Cirq and CUDA-Q
   (the reverse direction Qniverse lacks).
2. **Multi-simulator verifier (differential testing):** run the original, the converted and the optimised circuit on
   many Qniverse simulators and compare them: statevector or unitary up to global phase for small n,
   statistical tests (TVD / chi-square) for sampled results, stabilizer checks for Clifford circuits, PyZX for symbolic equivalence.
   Any disagreement is reported as a **discrepancy** with a likely cause (for example endianness).
3. **Optimiser:** peephole, commutation, resynthesis and ZX passes chosen by a **noise-aware cost** using
   Qniverse's own noise parameters (p, T1, T2, Tg). Every pass is followed by an equivalence check.
4. **Certificate:** one report per circuit: before/after depth and gate counts, estimated success probability,
   and pass/fail on every simulator.

## How we will show it works
- Benchmark table against **Qiskit O3, pytket and PyZX** on Grover, QFT, adders, QAOA and QASMBench circuits.
- Conversion matrix: every framework pair x every simulator, with pass/fail and the bugs found.
- Measured success probability before and after on Qniverse noisy simulators.
- Complexity and scaling analysis for every component.

## Value to C-DAC
A pip-installable layer that complements the existing converter: it makes conversions verifiable,
surfaces cross-simulator inconsistencies on the platform, and optimises circuits before they run.
