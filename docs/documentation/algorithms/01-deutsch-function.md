---
title: "Deutsch Function"
category: "Algorithms"
url: "https://qniverse.in/docs/deutsch-function/"
breadcrumb: "Home > Docs > Algorithms > Deutsch Function"
---

# Deutsch Function

> **Category:** Algorithms | **Source:** [https://qniverse.in/docs/deutsch-function/](https://qniverse.in/docs/deutsch-function/)


The Deutsch function is a fundamental concept in quantum computing that serves as a building block for more complex quantum algorithms. It is a two-qubit function that takes two input qubits (x and y) and returns a single output qubit (z). The function is defined as follows:

**Deutsch(x, y) = x XOR y,** where XOR is the exclusive OR operation.

The Deutsch function can be implemented using a quantum circuit consisting of a Hadamard gate, a controlled-NOT gate, and another Hadamard gate.

The circuit works as follows:

  1. **Hadamard gates:** The input qubits x and y are initialized to the state |0>. Hadamard gates are applied to both qubits to put them into a superposition of |0> and |1>.
  2. **Controlled NOT gate:** The controlled-NOT gate is applied with qubit x as the control qubit and qubit y as the target qubit. This gate flips the target qubit (y) if the control qubit (x) is |1>.
  3. **Hadamard gates:** Hadamard gates are applied again to both qubits.

After the circuit completes, the output qubit z will be in the state |1> if the Deutsch function is evaluated to 1, and |0> if it is evaluated to 0.

The Deutsch function is a simple example of a quantum algorithm that can be used to demonstrate the power of quantum computing. It shows how quantum superposition and entanglement can be used to perform calculations that would be difficult or impossible on a classical computer.
