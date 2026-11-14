---
title: "Simon’s Algorithm"
category: "Algorithms"
url: "https://qniverse.in/docs/simons-algorithms/"
breadcrumb: "Home > Docs > Algorithms > Simon’s Algorithm"
---

# Simon’s Algorithm

> **Category:** Algorithms | **Source:** [https://qniverse.in/docs/simons-algorithms/](https://qniverse.in/docs/simons-algorithms/)


## What is Simon’s algorithm?

Simon’s algorithm is a quantum algorithm that solves a problem related to finding periodicity in functions. It provides an exponential speedup over the best-known classical algorithms for the same problem and has applications in cryptography and computer science theory.

Simon’s algorithm works by implementing an unknown function, f, using quantum logic. This requires a unitary operator, Uf, that encodes the function’s action as a transformation on quantum states.

The algorithm’s quantum subroutine uses the Hadamard transform to execute two steps:

  1. quantum subroutine is typically run O(n) times to obtain a sufficient number of linearly independent equations to solve for the secret string to get a list of linearly independent bitstrings.
  2. Solve the system of equations produced by the bitstrings

The classical algorithm for Simon’s problem repeats queries until a collision is found. On average, a collision is more likely to be found after three tries, and there’s a greater than 50% chance of collisions for an input domain of eight numbers. Simon’s algorithm is a precursor to the Quantum Fourier Transform, which inspired Shor’s Algorithm.

The classical solution of Simon’s algorithm involves finding two inputs, x and y, where f(x) = f(y). This allows the user to determine **s = x⊕y** , where addition is done bitwise, mod 2. The user can also show that no two inputs produce the same output

To solve Simon’s problem classically, one needs to find two different inputs x and y for which f(x)=f(y), since one can then determine **s=x⊕y** (where addition is done bitwise, mod 2), or otherwise show that no two inputs produce the same output.

**Notation Consistency:** The secret string is referred to as both ‘k’ and ‘s’ throughout the explanation. It would be better to use a single, consistent notation (e.g., ‘s’) to avoid confusion.

**Below is a short video showing how the circuit looks for the 2-Qubit Selection with a “01” input for the secret message from the user. The corresponding QASM code is generated and can be modified and made to run on the available backend systems to obtain results, visualizations, and probabilities.**

`

[▶️ Video Demonstration: https://qniverse.in/wp-content/uploads/2025/04/simon-algo.mp4?_=1](https://qniverse.in/wp-content/uploads/2025/04/simon-algo.mp4?_=1)

## How does Simon’s Algorithm work?

Simon’s algorithm, unlike Grover’s algorithm, relies more heavily on mathematical expressions to describe its operations. Here’s a breakdown with key expressions:

**1\. Problem Setup:**

  * **Function (f):** Given a function `f` that maps `n`-bit strings (x) to `n`-bit strings (y). This function has a special property: **`f(x) = f(y)`** If and only if `**x ⊕ y = k**` for some fixed secret string **`k` **of length `n` (where **`⊕`** denotes bitwise XOR). The goal is to find the secret string `k`.

**2\. Oracle Function (Uf):**

In the quantum circuit, don’t have direct access to **`f`**. Instead, use an Oracle function **`Uf`** that implements the behavior of **`f`**. When applied to a superposition of states, it **`Uf`** acts on each basis state individually according to `f`.

**3\. Initial Superposition:**

Two qubits are initialized in a uniform superposition:
    
    
    ```python
    |ψ⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩) / 2  (normalized)
    ```

This creates a state where all four possible combinations (00, 01, 10, 11) are explored simultaneously.

**4\. Hadamard Transform (H):**

The first qubit is acted upon by the Hadamard transform (H):
    
    
    ```python
    H |ψ⟩ = (|0⟩ + |1⟩) ⊗ (|00⟩ + |01⟩ + |10⟩ + |11⟩) / √2
    ```

This creates a superposition across all four basis states for the first qubit, while the second qubit remains in its original superposition.

**5\. Applying the Oracle Function:**

The oracle function **`Uf`** is applied to the resulting state:
    
    
    ```python
    Uf * H |ψ⟩ = (Uf(|00⟩) + Uf(|01⟩) + Uf(|10⟩) + Uf(|11⟩)) ⊗ (|00⟩ + |01⟩ + |10⟩ + |11⟩) / √2
    ```

**6\. Interference:**

Due to the special property of **`f`** , if two input states differ only by the secret string `k`, their outputs from **`Uf`** will be identical. This creates constructive interference for those states, while others experience destructive interference.

**7\. Second Hadamard Transform:**

A second Hadamard transform is applied to the first qubit:
    
    
    ```python
    H * Uf * H |ψ⟩ = some complex state
    ```

This transformation amplifies the basis states that correspond to the secret string `k`.

**8\. Measurement:**

The two qubits are measured. The outcome reveals information about the secret string **`k`**. With a high probability, one of the bits will consistently be measured in the same state (either 0 or 1), providing a clue to the value in the corresponding position of **`k`**. The entire secret string can be determined efficiently by repeating the process (applying oracle and Hadamard transforms and measuring).**** This process is repeated approximately _n_ times to gather _n-1_ linearly independent equations.

## Explanation of Key Concepts

  * **Superposition** : Quantum states can exist in multiple states simultaneously, allowing Simon’s Algorithm to evaluate the function on various inputs simultaneously.
  * **Entanglement** : The input and output registers become entangled after the oracle query, meaning the state of one cannot be described independently of the state of the other.
  * **Interference** : The Hadamard transformations create interference patterns that amplify the correct solutions while canceling out the incorrect ones, making the hidden bit string **s** more apparent.
  * **Quantum Speedup** : Simon’s Algorithm runs in polynomial time on a quantum computer, specificallyO(n), whereas the best-known classical algorithm requires exponential time.

## Qubit Selection for Algorithm

After a user selects their preferred Qubit from the dropdown menu, a circuit is loaded in the main composer area after clicking on the “Load circuit” button for the selected Qubit.

Next, if a user selects 3-qubit, a corresponding 3-digit binary selection should be made, and similarly for other Qubit selections as well.

**Secret Message Selection:** Here, a secret message holds a hidden property (**the secret string s**) that the algorithm aims to discover about a function. Here, the input secret message always needs to be in binary format, i.e., in 0 and 1 format.

Imagine you have a black-box function that takes n bits as input and outputs another n bits. This function has a special property: it always outputs the same value if two input strings differ only by a specific “secret” n-bit string (let’s call it s). In other words, f(x) = f(y) only if x ⊕ s = y, where ⊕ represents bitwise XOR.

The goal of Simon’s algorithm is to find this secret string s, given only access to the black-box function (like an oracle) and the knowledge of the function’s property.

**Here is how the 2-Qubit selection works w.r.t Oracle arrangement:**

In Simon’s algorithm, the oracle plays a crucial role in revealing the function’s hidden period (secret string). Here’s how it works specifically for a 2-qubit selection:

**The Oracle’s Task:**

The oracle is a black-box function that takes two qubits as input **(`|x⟩|y⟩`)** and performs a specific operation based on Simon’s problem for a 2-qubit selection. Here’s the breakdown:

  1. **Input Qubits:**

     * The first qubit (`|x⟩`) represents the variable input to the function. It can be in a superposition state (`|0⟩ + |1⟩`), meaning it can be 0 or 1 simultaneously.
     * The second qubit (`|y⟩`) is typically initialized to the zero state (`|0⟩`). It acts as a scratchpad for the oracle’s operation.
  2. **Hidden Period:**

     * In a 2-qubit selection, the function has a hidden period of one bit (`s`). This means f(x) = f(x れません s) for any input value x. (⊕ denotes bitwise XOR).
  3. **Oracle’s Operation:**

     * The oracle manipulates the qubits based on the hidden period. Here’s the key step: 
       * If the first qubit’s value (x) differs from the hidden bit (s), the oracle flips the second qubit’s state (from |0⟩ to |1⟩ or vice versa).
       * If x and s are the same (x ⊕ s = 0), the oracle leaves the second qubit unchanged (remains |0⟩).

**Example:**

  * The hidden period (s) is 1 (s = |1⟩).
  * When the input is `|0⟩|0⟩` (x = 0), the oracle flips the second qubit (`|0⟩` to `|1⟩`) because 0 ⊕ 1 = 1.
  * When the input is `|1⟩|0⟩` (x = 1), The oracle leaves the second qubit as `|0⟩` since 1 ⊕ 1 = 0.

**How it Helps Find the Period:**

The algorithm can identify a pattern by querying the oracle with different superpositions of the first qubit and analyzing the second qubit’s state after the oracle’s operation. It can find two input states (differing only by the hidden bit) that both result in the same output from the oracle (the second qubit remains |0⟩). This reveals information about the hidden period, allowing the algorithm to determine the secret bit string (s).
