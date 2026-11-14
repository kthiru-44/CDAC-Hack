---
title: "Quantum Phase Estimation (QPE)"
category: "Algorithms"
url: "https://qniverse.in/docs/quantum-phase-estimation-qpe/"
breadcrumb: "Home > Docs > Algorithms > Quantum Phase Estimation (QPE)"
---

# Quantum Phase Estimation (QPE)

> **Category:** Algorithms | **Source:** [https://qniverse.in/docs/quantum-phase-estimation-qpe/](https://qniverse.in/docs/quantum-phase-estimation-qpe/)


## What is Quantum Phase Estimation?

QPE estimates the phase associated with the eigenvalue corresponding to a given eigenvector. Here’s a clearer version of this text:

Quantum mechanics involves the use of unitary operators to transform quantum states while preserving their norm and inner product structure. Eigenvectors are special states that remain unchanged except for a phase factor when a unitary operator acts on a quantum state.

The eigenvalues of unitary operators are complex numbers of the form e^2πiθ, where θ is the phase. QPE estimates this phase θ. The goal of Quantum Phase Estimation (QPE) is to estimate the eigenphase, which is the phase associated with the eigenvalue of a given unitary operator.

  * QPE requires the construction of a quantum circuit comprising a set of controlled unitary operations and a Quantum Fourier Transform (QFT). The precision of the estimation determines the number of qubits required in the circuit.  Controlled operations entangle the estimation register with the eigenvector, encoding the eigenphase into the amplitudes of the quantum state.

  * The QFT is a quantum equivalent of the classical discrete Fourier transform. It spreads information about the phase across multiple qubits. After applying the QFT, measurement is performed on the qubits. The resulting measurement outcomes are then used to estimate the phase.

  * Post-processing involves using the measurement outcomes of the quantum circuit to estimate the phase. This typically involves converting the binary representation of the measurement outcomes into a decimal fraction, which represents the estimated phase.

  * The accuracy of the estimated phase depends on the number of qubits used and the precision of the QFT. As the number of qubits increases, so does the precision of the estimation, but this also increases the complexity of the quantum circuit.

**Starting with a short video tour of how the circuit looks for the 2-Qubit Selection and the results obtained on submitting the circuit with parameters set for the Unitary operator as Phase operator and Theta(θ) as pi/2.**

[▶️ Video Demonstration: https://qniverse.in/wp-content/uploads/2024/05/QPE.mp4?_=1](https://qniverse.in/wp-content/uploads/2024/05/QPE.mp4?_=1)

## Why is QPE Important?

  * **Unlocks Eigenvalues:** Eigenvalues are crucial properties of unitary operators, and QPE provides a way to extract these hidden values. Eigenvalues hold valuable information about the system being studied.
  * **Foundation for Other Algorithms:** QPE serves as a building block for several groundbreaking quantum algorithms, including Shor’s factoring algorithm (for breaking encryption) and the Harrow-Hassidim-Lloyd (HHL) algorithm (for solving certain linear systems of equations).

## How Does QPE Work?

QPE leverages the superposition and entanglement principles of quantum mechanics. Here’s a simplified breakdown:

**1\. Preparation:**

  * An initial quantum state, denoted as |ψ⟩, (where |ψ⟩ is the Eigenvector of the Unitary operator) is prepared.
  * A set of qubits (quantum bits) is initialized in the |0⟩ state, acting as an estimation register.
  * The estimation register is bought in uniform superposition using the Hadamard operator.

**2\. Controlled Unitary Transformation:**

  * A sequence of controlled unitary operations (controlled by estimation register is applied on |ψ⟩.
  * The specific unitary operation depends on the problem at hand.
  * This step entangles the initial state |ψ⟩ with the estimation register, encoding the phase information into the register.

**3\. Quantum Fourier Transform (QFT):**

  * An inverse quantum Fourier transform (iQFT) is applied to the estimation register. This operation extracts the phase information from the entangled state.

**4\. Measurement:**

  * The estimation register qubits are measured.The output gives a binary approximation of the phase θ corresponding to the eigenvalue.

## How Does QPE Work(Expression Format)?

**Eigenvalue and Eigenvector:**

**1\. U |ψ⟩ = e^(2πiθ) |ψ⟩:** This equation represents the eigenvalue equation, where:

  * U is the unitary operator.
  * |ψ⟩ is the eigenvector of U.
  * e^(2πiθ) is the eigenvalue of U with phase θ (0 ≤ θ < 1).

**2\. Quantum Fourier Transform (QFT):**

  * **QFT |θ⟩ = (1/√2^t) * Σ^(2^t-1)_k=0 e^(2πiθk/2^t) |k⟩:** This expression defines the QFT, where:
  * t is the number of qubits in the estimation register.
  * |θ⟩ is the computational basis state representing the unknown phase θ.
  * |k⟩ is the computational basis state of the estimation register (k = 0, 1, …, 2^t-1).
  * The summation creates a superposition of basis states with weights determined by the phase θ.

**3\. Final State after QFT:**

  * **|ψ⟩⊗QFT |θ⟩:** This represents the entangled state after applying the QFT to the estimation register, where ⊗ denotes the tensor product.

**4\. Measurement Outcome:**

  * **|m⟩:** This represents the outcome state after measuring the estimation register qubits, where |m⟩ is a specific computational basis state (m = 0, 1, …, 2^t-1).

**5\. Estimated Phase:**

  * **θ_est ≈ m/2^t:** This approximates the unknown phase θ based on the measured outcome |m⟩. The accuracy improves with more qubits (larger t).
