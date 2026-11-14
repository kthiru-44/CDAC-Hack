---
title: "Bernstein-Vazirani Algorithm"
category: "Algorithms"
url: "https://qniverse.in/docs/bernstein-vazirani-algorithm/"
breadcrumb: "Home > Docs > Algorithms > Bernstein-Vazirani Algorithm"
---

# Bernstein-Vazirani Algorithm

> **Category:** Algorithms | **Source:** [https://qniverse.in/docs/bernstein-vazirani-algorithm/](https://qniverse.in/docs/bernstein-vazirani-algorithm/)


## What is the Bernstein-Vazirani algorithm?

The Bernstein-Vazirani algorithm is a quantum algorithm that solves a similar problem to the classical problem addressed by the classical Bernstein-Vazirani algorithm. It’s a simple quantum algorithm, but it demonstrates the power of quantum parallelism. It is used to solve a specific type of problem known as the Bernstein-Vazirani problem. The Bernstein-Vazirani problem deals with a function _f_ that takes an _n_ -bit input _x_ and returns a single bit, defined as _f(x) = s ⋅ x mod 2_ , where _s_ is a secret _n_ -bit string and _⋅_ denotes the bitwise dot product (sum of the products of corresponding bits) modulo 2. The goal is to find this secret string  _s_

The algorithm works by using a set of qubits in superposition, an auxiliary qubit, and a quantum oracle that represents the secret key. The qubits are then measured, and the resulting measurement provides information about the hidden binary string.

The key to this algorithm’s efficiency is the use of quantum parallelism, which allows us to explore all possible inputs simultaneously. This is achieved through the superposition of states in the quantum register. Thus, the algorithm only requires one query to find the hidden string, in contrast to the classical algorithm, which requires O(n) queries.

[▶️ Video Demonstration: https://qniverse.in/wp-content/uploads/2025/04/bernstein-algo.mp4?_=1](https://qniverse.in/wp-content/uploads/2025/04/bernstein-algo.mp4?_=1)

## How does the Bernstein-Vazirani algorithm work?

The Bernstein-Vazirani algorithm uses quantum gates to perform operations on qubits. The two most commonly used quantum gates in the algorithm are the Hadamard gate and the CNOT gate. The Hadamard gate is used to create superposition, while the CNOT gate is used to create entanglement between two qubits.

Superposition is a fundamental concept in quantum mechanics, which allows a qubit to be in two states at the same time. In the Bernstein-Vazirani algorithm, the Hadamard gate is used to create superposition. By applying the Hadamard gate to each qubit in a register, the algorithm can create a superposition of all possible states of the qubits.

In the Bernstein-Vazirani algorithm, the CNOT gate is used to create entanglement between two qubits. By applying the CNOT gate to two qubits, the algorithm can create entanglement between them, which allows the state of one qubit to be determined by the state of the other qubit.

BV algorithm with expressions:

**1\. Oracle Function (f):**

The oracle in the Bernstein-Vazirani algorithm implements the function _f(x) = s ⋅ x mod 2_. It acts on the quantum state by encoding the result of this function into the phase of an auxiliary qubit.

**2\. Quantum Circuit:**

The BV algorithm utilizes a quantum circuit with two qubits:

  * **First Qubit (|x⟩):** This qubit is initialized in a superposition state: `|x⟩ = (|0⟩ + |1⟩ ) / √2`

  * **Second Qubit (|y⟩):** This qubit is initialized in the |0⟩ state: `|y⟩ = |0⟩`

**3\. Hadamard Gate (H):**

A Hadamard gate (H) is applied to the first qubit, creating a superposition of both possible input values simultaneously.

**4\. Oracle Function (f):**

A unitary operator representing the black-box function `f` is applied as a controlled operation. This operation depends on the state of the first qubit and modifies the second qubit based on the function’s output `f(x)`The oracle’s action is typically represented as: |x⟩|y⟩ → |x⟩|y ⊕ (s ⋅ x mod 2)⟩, where _x_ is the _n_ -bit input and _y_ is the auxiliary qubit.

**5\. Inverse Hadamard Gate :**

The inverse Hadamard gate (H^†) is applied to the first qubit, transforming the superposition back into a basis state (either |0⟩ or |1⟩).

**Expressions for State Transformations:**

These expressions represent the state transformations in the BV algorithm:

  * Initial state: `|ψ⟩ = |x⟩ ⊗ |y⟩ = (|0⟩ + |1⟩) / √2 ⊗ |0⟩`
  * After Hadamard: `|ψ⟩ = (|0⟩ + |1⟩) / √2 ⊗ (|0⟩ + |1⟩) / √2`
  * After Oracle: This depends on the specific function `f` and its effect on the second qubit.
  * After Inverse Hadamard: `|ψ⟩ = α |0⟩ ⊗ |f(0)⟩ + β |1⟩ ⊗ |f(1)⟩` (where α and β are complex coefficients)

**Measurement and Outcome:**

  * Measuring the first qubit reveals either |0⟩ or |1⟩.
  * If the function `f` is balanced, the outcome will be different with a 50% chance of being 0 or 1. This allows us to determine that the function is balanced with a single query to the oracle (unlike classical algorithms that might require multiple queries).
  * If the function `f` is constant, the outcome will always be the same (either all 0s or all 1s). However, the BV algorithm doesn’t differentiate between these two cases (both constant 0 and constant 1 are unbalanced functions).

## What are the applications of the Bernstein-Vazirani algorithm?

  * The Bernstein-Vazirani algorithm has numerous real-world applications, especially in cryptography. It is a powerful algorithm that can rapidly identify the hidden string in a function, making it valuable in various scenarios where the function’s input is unknown.
  * It serves as a building block for understanding more complex quantum algorithms. While it might have theoretical connections to cryptography in the sense of breaking specific types of hidden linear functions, it’s not a practical tool for breaking real-world cryptographic systems like symmetric-key cryptography in the way described. 

## Comparative Analysis: Bernstein-Vazirani Algorithm vs. Other Quantum Algorithms

### Quantum Fourier Transform

The quantum Fourier transform is a key quantum algorithm used in various other quantum algorithms, including Shor’s algorithm. It is employed to convert a quantum state from the time domain to the frequency domain. Although the Bernstein-Vazirani algorithm does not utilize the quantum Fourier transform, it is an essential component of many other quantum algorithms.
