---
title: "Portfolio Optimization using QAOA"
category: "Algorithms"
url: "https://qniverse.in/docs/portfolio-optimization-using-qaoa/"
breadcrumb: "Home > Docs > Algorithms > Portfolio Optimization using QAOA"
---

# Portfolio Optimization using QAOA

> **Category:** Algorithms | **Source:** [https://qniverse.in/docs/portfolio-optimization-using-qaoa/](https://qniverse.in/docs/portfolio-optimization-using-qaoa/)


QAOA Portfolio Optimization is a hybrid quantum–classical asset selection and weighting toolkit that formulates the portfolio construction problem as a QUBO (Quadratic Unconstrained Binary Optimization) and solves it via the Quantum Approximate Optimization Algorithm (QAOA). Given a universe of assets, it balances expected return and risk, then decodes the best measured bitstring into portfolio weights (equal- or unequal-weighted), and reports performance and explainability artifacts (Sharpe ratios, risk contributions, probability of top bitstrings, and more). Implemented with Qiskit v1.4.3 primitives and AerSimulator.

**Presenting here with a short video tour of the implementation of QAOA Portfolio optimization in Qniverse**

[▶️ Video Demonstration: https://qniverse.in/wp-content/uploads/2025/10/QAOA-algo.mp4?_=1](https://qniverse.in/wp-content/uploads/2025/10/QAOA-algo.mp4?_=1)

## How QAOA Portfolio Optimization Differs from Classical Mean–Variance?

Classical mean–variance optimization solves a continuous quadratic program under constraints (e.g., weights sum to 1, non-negativity). In contrast, this approach discretizes choices into binary variables (one bit per asset for equal weights, or “one-hot” multi-bit per asset for weight levels), constructs a QUBO capturing return, risk, budget, and one-hot constraints, maps it to an Ising Hamiltonian, and uses QAOA to approximate the ground state. The measured bitstring encodes the selected assets and (optionally) their weight level.

## How QAOA Portfolio Optimization Can Be Implemented?

  1. **Data Normalization and Preparation**  
Load prices (CSV, DataFrame, or ndarray), robustly parse dates, sanitize numerics, pivot to a “time × tickers” price table, and compute returns by method: pct_change, log_return, or diff. Handle infinities and NaNs with forward/backward fills and drops.
  2. **Return & Covariance Estimation**  
Compute mean returns and the sample covariance matrix from the cleaned returns table; ensure positive semi-definiteness by nudging eigenvalues if needed.
  3. **QUBO Formulation**  
For equal weights: build an n×n QUBO combining risk (covariance) and return (diagonal reward). For unequal weights: expand to (#assets × bits_per_asset) with one-hot blocks, cross-asset covariance interactions scaled by risk tolerance, selection bonuses, and a budget penalty enforcing total-weight ≈ target.
  4. **QUBO → Ising Mapping**  
Vectorize conversion to a SparsePauliOp (linear Z terms and ZZ couplings) and compute the constant offset.
  5. **QAOA Setup**  
Instantiate QAOA (Qiskit v1.x) with a Sampler (shots, seed) and an optimizer (COBYLA or SPSA). Choose depth (reps) per accuracy–runtime tradeoff.
  6. **Solve & Decode**  
Run QAOA to obtain eigenstate bitstring probabilities; pick the most probable bitstring; decode to selected assets and weights. Rescale to meet the total-weight constraint if required. Fallback: if nothing is selected, assign equal weights to top-return assets.
  7. **Metrics & Artifacts**  
Compute expected return, volatility, Sharpe, and annualized Sharpe; optionally evaluate on a held-out test set. Prepare plot-ready structures: weights bars, risk–return scatter, risk-contribution pie, and top-10 bitstring probability bars.

## Advantages and Disadvantages Compared to the Classical Counterpart

**Advantages**

  * Discrete, interpretable choices: Naturally enforces cardinality and coarse weight levels via binary variables (equal weights or one-hot levels).
  * Flexible constraints: Clean composition of risk, return, budget, and one-hot constraints into a single QUBO.
  * Quantum-ready: Uses QAOA with modern Qiskit primitives, enabling experimentation on simulators today and hardware later.

**Disadvantages**

  * Discretization error: Coarse weight levels approximate continuous solutions; more levels mean more qubits.
  * Resource growth: Unequal-weight models scale with (#assets × levels), increasing Hamiltonian size and circuit depth.
  * NISQ limitations: Practical performance depends on shots, noise, and optimizer settings; simulators may dominate runtime.

## Real-World Applications

  * Long-only screening with cardinality limits (e.g., pick K from N) under budget and sector rules (through QUBO design).
  * Coarse-grained allocation where a few weight buckets suffice (0%, 10%, 20%, …).
  * Rapid what-if exploration of return–risk tradeoffs by sweeping risk_tolerance, penalty strengths, and reps.

## Overview

The QAOAPortfolioOptimizer class provides an end-to-end pipeline: ingest prices, compute returns/covariance, build QUBO (equal or unequal weights), convert to Ising, run QAOA, decode weights, compute in-sample metrics, optionally evaluate out-of-sample, and return a portfolio summary and plot-ready data. It includes robust date/number parsing, adaptive weight-level construction, budget constraints, and vectorized Hamiltonian assembly for efficiency.

## Key Components and Features

  * **Data Handling**  
Robust datetime parsing, numeric sanitization, pivoting to prices, multiple return methods, and NA/∞ cleanup.
  * **Statistics**  
Mean returns and covariance with PSD safeguard via eigenvalue shift.
  * **Weighting Modes**  
Equal weights (1 bit/asset) or unequal weights (one-hot levels per asset); adaptive weight-level suggestions based on asset count and target budget.
  * **QUBO Builder**  
Returns reward, risk penalty, one-hot per asset, cross-asset covariance, and budget penalty are composed into Q.
  * **Ising Conversion**  
Vectorized mapping to SparsePauliOp with linear and quadratic Z terms plus global offset.
  * **QAOA Solver**  
Qiskit Sampler with shots/seed, QAOA depth reps, and optimizer choice (COBYLA/SPSA). Outputs eigenvalue and bitstring probabilities.
  * **Evaluation & Reporting**  
In-sample and out-of-sample return, risk, Sharpe, annualized Sharpe; portfolio summary with weights and risk contributions; plot-data dict for four standard visualizations.

## End-to-End Workflow

  1. **Initialization:** Configure num_assets, risk_tolerance, reps, optimizer, shots, penalty_strength, weight strategy, and budget.
  2. **Data Preprocessing:** Load CSV/DataFrame, parse dates, compute returns, and clean.
  3. **QUBO & Ising:** Build Q, add constraints, map to Ising Hamiltonian.
  4. **QAOA Run & Decode:** Execute QAOA, read top bitstring, decode weights (rescale if needed).
  5. **Evaluation & Output:** Compute metrics, generate portfolio summary, and produce plot data (weights bar, risk–return scatter, risk contribution pie, top-10 bitstrings).

## Getting Started in Qniverse

**Usage with Market Data (CSV)**

from qniverse.algorithms import QAOAPortfolioOptimizer

**Initialize optimizer**

selector = QAOAPortfolioOptimizer(  
num_assets=20,  
risk_tolerance=0.3,  
reps=40,  
optimizer=’COBYLA’,  
max_iter=250,  
shots=2048,  
)

**Train using the integrated pipeline**

summary, performance = selector.train(  
csv_path=”data.csv”,  
ticker_col=”Company”,  
target_col=”Open”,  
date_col=”Date”,  
return_method=”log_return”,  
test_size=0.25  
)

print(summary)  
print(performance)

The train routine loads data, runs QAOA, prints a final report, returns a portfolio summary DataFrame and a metrics dict (including Sharpe ratios).

## Understanding the Parameters

**Optimization Settings**

  * num_assets: Number of assets to consider (auto-capped to available). If None, uses all available.
  * risk_tolerance: Tradeoff in [0, 1]; higher emphasizes risk (covariance), lower emphasizes return.
  * reps: QAOA depth (p). Larger values may improve quality at extra runtime.
  * optimizer: ‘COBYLA’ or ‘SPSA’ with max_iter controlling classical step budget.
  * shots: Number of circuit executions in the Sampler; higher reduces sampling noise.
  * seed: Random seed for reproducibility.

**Data Handling Settings**

  * return_method: One of ‘pct_change’, ‘log_return’, or ‘diff’.
  * csv_path / DataFrame / ndarray inputs: Ticker/price/date columns for CSV/DataFrame; ndarray uses numeric columns directly.
  * ticker_col / target_col / date_col: Column names for pivot and return computation; robust parsing included.

**Hyperparameter Tuning**

  * reps: Increase until solution quality stabilizes.
  * optimizer & max_iter: COBYLA for smooth local search; SPSA for stochastic landscapes.
  * penalty_strength: Sweep to ensure one-hot and budget constraints hold without drowning the objective.
  * weight_levels: Adjust granularity vs. qubit count; start coarse (e.g., 0, 10%, 20%, …).
  * shots: Balance sampling error vs. runtime; raise if bitstring probabilities look too flat.

**Evaluation Metrics and Plot History**

  * In-sample: expected_return, expected_risk, sharpe_ratio, annualised_sharpe, eigenvalue, optimization_time, selections.
  * Out-of-sample (if test split provided): return, risk, and Sharpe computed on aligned tickers.
  * Plot data dict:  
• weights_bar (selected tickers & weights)  
• risk_return_scatter (individual assets + portfolio point)  
• risk_contribution_pie (contribution shares)  
• probability_bars (top-10 bitstrings by probability)

## Conclusion

QAOA Portfolio Optimization offers a discrete, constraint-friendly path to portfolio construction using hybrid quantum methods. With robust data preparation, flexible weighting modes, vectorized QUBO/Ising assembly, and Qiskit-native QAOA, it enables practical experiments today and a migration path to future quantum hardware. Use the provided pipeline to load data, run QAOA, review performance, and export plot-ready artifacts for reporting.
