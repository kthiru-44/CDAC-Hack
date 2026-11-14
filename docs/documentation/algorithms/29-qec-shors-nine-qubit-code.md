---
title: "QEC : Shor’s Nine-Qubit Code"
category: "Algorithms"
url: "https://qniverse.in/docs/qec-shors-nine-qubit-code/"
breadcrumb: "Home > Docs > Algorithms > QEC : Shor’s Nine-Qubit Code"
---

# QEC : Shor’s Nine-Qubit Code

> **Category:** Algorithms | **Source:** [https://qniverse.in/docs/qec-shors-nine-qubit-code/](https://qniverse.in/docs/qec-shors-nine-qubit-code/)


## What is Shor’s Nine-Qubit code?

The Shor 9-qubit code, introduced by Peter Shor in 1995, is one of the earliest and most foundational quantum error correction (QEC) codes. It was the first to demonstrate that quantum information can be protected against arbitrary single-qubit errors, including bit-flip (X), phase-flip (Z), and their combination (Y). Drawing inspiration from classical repetition codes, Shor extended the concept to the quantum domain by addressing not only bit errors, which resemble classical bit flips, but also phase errors, which are unique to quantum mechanics and affect the relative phase of a qubit’s superposition state.

**Presenting here with a video tour of how the Shor’s Nine-Qubit Code is implemented****in Qniverse:**

[▶️ Video Demonstration: https://qniverse.in/wp-content/uploads/2025/07/QEC9-bit.mp4?_=1](https://qniverse.in/wp-content/uploads/2025/07/QEC9-bit.mp4?_=1)

## How Shor’s nine-Qubit Code works?

This code protects a single logical qubit by encoding it into nine physical qubits. The strategy involves layering two types of repetition codes: an inner code that protects against bit-flip errors and an outer code that handles phase-flip errors. Specifically, the logical qubit is first encoded into a three-qubit phase-protected block, and each of those three qubits is further encoded using a three-qubit bit-protected block, leading to a 3 × 3 structure that spans nine qubits in total. This construction is the minimum required to independently and simultaneously detect and correct both types of quantum errors for a single qubit. Any fewer qubits would compromise the code’s ability to correct arbitrary Pauli errors.

While the data is stored in these nine physical qubits, error detection and correction rely on ancilla qubits, which are not part of the logical encoding but are used to extract error syndromes through quantum measurements. So, the full implementation of the Shor code typically involves around seventeen qubits in total: nine for storing the logical qubit and eight for error diagnosis.

The 3-qubit repetition code, which can correct only one type of error (either bit-flip or phase-flip), is structurally embedded within the Shor code as a building block. Through this hierarchical design, the Shor 9-qubit code establishes a complete error-correcting framework capable of preserving quantum information against any single-qubit error without collapsing the state, thus forming a foundational example of how quantum error correction can be achieved.

As the Shor 9-bit code is capable of correcting single-qubit error, which includes bit-flip (X), phase-flip (Z), or both (Y), across its 9 physical qubits. It achieves this by combining two layers of repetition coding, one for bit-flip and one for phase-flip protection. However, in scenarios where quantum resources are limited or only one specific type of error is dominant, simpler codes like the **[3-bit repetition code](https://qniverse.in/docs/qec-three-qubit-repetition-code/) **can be used as a lightweight alternative. The repetition code offers a resource-efficient way to correct a single error of either X or Z type, but not both simultaneously, making it suitable for basic error models or testing environments.

## How does Encoding work in Shor’s nine-qubit code?

**_Encoding_**

The encoding process in the Shor 9-qubit code happens in two main stages, which protect the quantum information from both bit-flip and phase-flip errors.

#### Phase-Flip Encoding (Outer Code)

The first step in the encoding process targets phase-flip (Z) errors. The logical qubit is encoded into a superposition of three-qubit blocks using Hadamard and entangling operations. This creates a state of the form:

∣ψL⟩ = α∣+ + +⟩ + β∣− − −⟩

where ∣+⟩ = (∣0⟩+∣1⟩) and ∣−⟩ = (∣0⟩−∣1⟩).  
This encoding distributes the phase information across three qubits, so that a single-phase error on any one of them does not compromise the logical state. It enables phase-flip errors to be detected by comparing the relative phases between the three blocks in further steps.

#### Bit-Flip Encoding (Inner Code)

Each of the three qubits resulting from the phase-flip encoding is then further encoded using a 3-qubit repetition code to protect against bit-flip (X) errors. This is done by distributing the quantum information across three qubits using entanglement, creating a form of redundancy analogous to the classical three-bit repetition code. Each of these three qubits holds the same logical information, enabling error correction through majority voting.

This results in the full 9-qubit logical state:

∣ψL⟩ = α (∣+ + +⟩) ⊗3 \+ β (∣− − −⟩) ⊗3

or, equivalently, in the computational basis:

∣0L⟩ = (∣000⟩ + ∣111⟩) ⊗3, ∣1L⟩ = (∣000⟩ − ∣111⟩) ⊗3

This repetition code ensures that any single X-type error can be detected and corrected within each 3-qubit block.

**Block-Based Structure**

The final encoded state consists of nine physical qubits arranged into three blocks of three. Each block handles bit-flip correction through repetition, while the comparison between blocks allows for detection and correction of phase-flip errors. The full encoded logical states become:

∣0L⟩ = (∣000⟩ + ∣111⟩) ⊗3, ∣1L⟩ = (∣000⟩ − ∣111⟩) ⊗3

This structure ensures that the code can detect and correct single-qubit errors, whether it’s a bit-flip, phase-flip, or both.

## Simulating Errors

To model noise in a quantum system, errors can be simulated by applying Pauli-X, Z, or both to any one of the nine physical qubits after encoding. Errors can be introduced in any order, but only one qubit should be affected at a time, as the Shor code is designed to detect and correct any arbitrary single-qubit error. This simulation helps validate the code’s fault tolerance under typical quantum noise models.

## _Bit flip and Phase flip error detection, and Correction_

After encoding the logical qubit into the 9-qubit Shor code structure, bit-flip (X-type) errors can be detected by performing syndrome measurements on each of the three 3-qubit blocks, which use additional qubits called ancilla qubits to extract error information without disturbing the actual data qubits. This allows the error to be located without collapsing the encoded quantum state.

These measurements output (called the syndrome) indicate whether the pairs match:

  * A result of 0 (from the ancilla) means the qubits are the same (no disagreement).
  * A result of 1 means the qubits are different (one likely flipped).

00 | No error  
---|---  
10 | Error in qubits 0  
11 | Error in qubits 1  
01 | Error in qubits 2  
  
This entire detection process is performed independently for each of the three blocks. In total, the bit-flip error detection mechanism is applied three times**,** once for each 3-qubit block of the encoded state:

  * **Block 1:** Qubits 0, 1, 2
  * **Block 2:** Qubits 3, 4, 5
  * **Block 3:** Qubits 6, 7, 8

Each block has its own pair of ancilla qubits and CNOT measurement setup, ensuring localized error detection and correction.

After detecting and locating an error using syndrome measurements, a correction gate is applied to the affected qubit. Pauli operators are self-inverse, so applying the same gate (e.g., X or Z) again reverses the error.

To detect and correct phase-flip (Z-type) errors, the Shor 9-bit code uses a strategy that mirrors the approach used for bit-flip detection, but applied at the block level. Phase errors are more subtle because they don’t alter the measured values in the computational basis directly; they change the relative phase of the quantum state. To make these errors detectable using standard parity checks, a Hadamard transformation is employed.

  * Hadamard gates are applied to all 9 data qubits.
  * After this, CNOT gates are used to entangle the data qubits with ancilla qubits in a block-wise manner. Each ancilla interacts with qubits from corresponding positions in the three 3-qubit blocks.
  * The ancilla qubits are then measured, and their outputs serve as the syndrome values indicating which block has experienced a phase-flip error.

00 | No error  
---|---  
10 | Error in block 0  
11 | Error in block 1  
01 | Error in block 2  
  
  * Once the syndrome information is extracted, Hadamard gates are applied again to all 9 data qubits to return them to their original basis.

This detection process is performed once across the entire 9-qubit register, comparing the three blocks collectively.

Based on the syndrome outcomes, we determine which block contains the phase error. A single Z-gate is applied to any one qubit in the affected block.

This is sufficient because all three qubits in a block are expected to be in the same state (either |000⟩ or |111⟩). Applying Z to one of them effectively flips the phase of the entire logical component without disturbing bit-level encoding.

## How does Decoding work in Shor’s nine-qubit code?

**_Decoding:_**

After error detection and correction, the final step in the Shor 9-qubit code is to decode the logical qubit from its 9-qubit encoded form and extract the final result via measurement. CNOT gates are applied within each block to undo bit-flip encoding. Hadamard gates are applied to the first qubit of each block to reverse the phase-flip encoding. All 9 qubits are then measured, and the logical outcome is extracted.
