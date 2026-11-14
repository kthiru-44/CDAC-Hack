---
title: "Deutsch-Jozsa Algorithm"
category: "Algorithms"
url: "https://qniverse.in/docs/deutsch-jozsa-algorithm/"
breadcrumb: "Home > Docs > Algorithms > Deutsch-Jozsa Algorithm"
---

# Deutsch-Jozsa Algorithm

> **Category:** Algorithms | **Source:** [https://qniverse.in/docs/deutsch-jozsa-algorithm/](https://qniverse.in/docs/deutsch-jozsa-algorithm/)


## What is Deutsch-Jozsa Algorithm?

The Deutsch-Jozsa algorithm is one of the earliest quantum algorithms discovered, and it demonstrates a quantum speedup over classical algorithms for a specific problem. The problem it solves is called the Deutsch-Jozsa problem, which is a black-box problem.

This algorithm can determine if a function has a specific property, such as being balanced. It achieves this by requiring that the function, or a derivation of it, only be called once with a quantum algorithm instead of twice with a classical algorithm. This is especially advantageous when the function is computationally expensive, since computing it once instead of twice can save a significant amount of resources

By using the Deutsch-Jozsa approach, it is possible to determine whether a given Boolean function is constant or balanced. A function takes input values of 0 and 1 and outputs values of 0 or 1. The function is considered constant if all outputs are 0 or 1. When exactly half of the inputs are zero and exactly half are ones, refer to the function as balanced.

## How does the Deutsch-Jozsa work?

**Starting here with a video that shows how the Deutsch-Jozsa algorithm is loaded with the given parameters, with a 2-qubit selection**

[▶️ Video Demonstration: https://qniverse.in/wp-content/uploads/2024/12/DJ-Algorithm-2.mp4?_=1](https://qniverse.in/wp-content/uploads/2024/12/DJ-Algorithm-2.mp4?_=1)

**The Deutsch-Jozsa algorithm has a 5-step process.**

  * First, quantum registers and input states are prepared.
  * In the second step, the qubits are organized into the Hadamard Basis, giving each qubit a 50% chance of being 0 or 1.
  * The third step is the oracle, which encodes the function that determines if the outputs are constant or balanced using quantum entanglement.
  * The fourth step returns the qubits to the measurement basis to find the answer.
  * Finally, in the fifth, the qubits are measured to obtain the solution.

The main difference between implementation approaches is in the oracle. One common implementation uses a CX gate to initialize a second quantum register with an ancilla qubit, also known as a “work qubit.” The ancilla qubit is set to 1 instead of the normal initialization of 0. The oracle then uses phase kickback to determine if the function is constant or balanced. If the function is balanced, phase kickback will add a negative phase to half of the quantum states.

## Analysis of the Algorithm

**1\. Function Definition (f):**

The DJ algorithm deals with a black-box function `f` That takes one bit (`x`) as input and outputs one bit (`y`). This function can be either:

  * **Constant :** **`f(x)`** always outputs the same value (either 0 or 1) for all possible input bits `x`.
  * **Balanced :** **`f(x)`** outputs 0 for exactly half of the possible input bits and 1 for the other half.

**2\. Quantum Circuit:**

The DJ algorithm utilizes a quantum circuit with two qubits:

  * **First Qubit (|x⟩) :** This qubit is initialized in a superposition state: **`|x⟩ = (|0⟩ + |1⟩) / √2`**

  * **Second Qubit (|y⟩) :** This qubit is initialized in the |0⟩ state: **`|y⟩ = |0⟩`**

**3\. Hadamard Gate (H):**

A Hadamard gate (H) is applied to the first qubit, creating a superposition of both possible input values simultaneously.

**4\. Oracle Function (f):**

A unitary operator representing the black-box function **`f`** is applied as a controlled operation. This operation depends on the state of the first qubit **(****`|x⟩`****)** and modifies the second qubit**(****`|y⟩`****)** based on the function’s output **`f(x)`**.

**5\. Inverse Hadamard Gate :**

The inverse Hadamard gate is applied to the first qubit, transforming the superposition back into a basis state (either |0⟩ or |1⟩).

**Expressions for State Transformations:**

These expressions represent the state transformations in the DJ algorithm:

  * Initial state: **`|ψ⟩ = |x⟩ ⊗ |y⟩ = (|0⟩ + |1⟩) / √2 ⊗ |0⟩`**
  * After Hadamard: **`|ψ⟩ = (|0⟩ + |1⟩) / √2 ⊗ (|0⟩ + |1⟩) / √2`**
  * After Oracle: This depends on the specific function **`f`** and its effect on the second qubit.
  * After Inverse Hadamard: **`|ψ⟩ = α |0⟩ ⊗ |f(0)⟩ + β |1⟩ ⊗ |f(1)⟩`** (where α and β are complex coefficients)

**Measurement and Outcome:**

  * Measuring the first qubit reveals either |0⟩ or |1⟩.
  * If the function **`f`** is constant, the outcome will always be the same (either all 0s or all 1s).
  * If the function **`f`** is balanced, the outcome will be different with a 50% chance of being 0 or 1.

## How does the Deutsch-Jozsa Algorithm compare?

The Deutsch-Jozsa algorithm determines if the Boolean function is constant or balanced. For today’s error-prone quantum computers, this circuit must be run several times to determine whether the function is likely constant or likely balanced. However, future quantum computers can make this judgment with 100% accuracy on the first attempt.

In contrast, the corresponding classical technique requires a minimum of two attempts. It requires several attempts equal to 1 + N, where N is the number of inputs. A minimum of two attempts is required to see a zero and a one and, thus, determine if the function is balanced.

For a larger number of inputs, if half of the inputs are zeros, for instance, there is still a chance that the other half are all ones, and the function might still be balanced. However, if half plus one of the inputs are zeroes, and a balanced function must contain exactly half zeros and half ones, then it can be determined that the function is constant.

The distinction between quantum and conventional techniques may look inconsequential since textbook examples always demonstrate extremely minor issues. Imagine, however, a problem with one million inputs.

The ideal classical approach would need to examine 500,001 inputs in the worst-case scenario. In contrast, the Deutsch-Jozsa algorithm would simultaneously examine all inputs and produce an accurate answer after a single attempt.

## What is the Practicality of the Deutsch-Jozsa Algorithm?

The Deutsch-Jozsa algorithm was not initially designed for practical applications but rather to showcase the potential for quantum computers to solve specific problems more efficiently than classical computers. Although the algorithm itself does not have any known practical uses, it laid the groundwork for the discovery of Grover’s algorithm, which demonstrated that quantum computers can provide significant speedups for certain tasks. However, it also underscored the considerable technical challenges associated with building quantum oracles for more than a few qubits.
