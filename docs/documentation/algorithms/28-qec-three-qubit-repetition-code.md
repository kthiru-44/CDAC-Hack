---
title: "QEC : Three-Qubit Repetition Code"
category: "Algorithms"
url: "https://qniverse.in/docs/qec-three-qubit-repetition-code/"
breadcrumb: "Home > Docs > Algorithms > QEC : Three-Qubit Repetition Code"
---

# QEC : Three-Qubit Repetition Code

> **Category:** Algorithms | **Source:** [https://qniverse.in/docs/qec-three-qubit-repetition-code/](https://qniverse.in/docs/qec-three-qubit-repetition-code/)


Quantum Error Correction (QEC) is a crucial field in quantum computing aimed at protecting quantum information from errors caused by various types of noise, such as bit-flips and phase-flips. Unlike classical computing, where information is stored as bits (0 or 1), quantum information is stored in quantum states that can be in superpositions of these states. This makes quantum information highly susceptible to errors, as even minor disturbances can significantly alter the state. QEC aims to encode quantum information in such a way that errors can be detected and corrected, ensuring that quantum computations remain reliable and fault-tolerant.

**Presenting here with a video tour of how the Quantum Error Correction Algorithm works:**

[▶️ Video Demonstration: https://qniverse.in/wp-content/uploads/2025/06/QEC-Algo.mp4?_=1](https://qniverse.in/wp-content/uploads/2025/06/QEC-Algo.mp4?_=1)

**Bit-Flip Error**

Bit-flip error is one of the most common types of errors in quantum computing. A bit-flip error occurs when the state of a qubit changes from ∣0⟩ to ∣1⟩ or from ∣1⟩ to ∣0⟩, which is analogous to flipping a classical bit. For example, a qubit that is originally in the state ∣0⟩ could be flipped to ∣1⟩, leading to a loss of the original information. Bit-flip errors are typically caused by environmental interactions, such as noise or imperfect operations on the qubits.

**Phase-Flip Error**

A phase-flip error, on the other hand, does not change the qubit from 0 to 1 or vice versa. Instead, it changes the internal phase of the qubit’s state. Specifically, the state 0 remains unchanged, but the state 1 gains a negative sign in its contribution to the qubit’s overall behaviour. This doesn’t affect the measurement outcome if the qubit is purely in state 0 or 1, but it has a significant effect when the qubit is in a superposition. Phase-flip errors are typically caused by factors like fluctuations in the system’s energy levels or interactions with the environment.

Quantum error correction codes are designed to detect and correct errors, enabling quantum systems to perform reliable computations despite imperfections.

## Why Use 3 Qubits in the Repetition Code?

In quantum error correction, the 3-qubit repetition code strikes a balance between simplicity, efficiency, and fault tolerance. It is designed to detect and correct a single bit-flip /phase-flip error, offering the minimal number of qubits required to ensure both functionality and protection.

**_2-Qubit Code: No detection, No correction_**

The repetition code cannot be properly implemented using only 2 qubits. The core principle of the repetition code is to introduce redundancy by encoding a single logical qubit into multiple physical qubits, so that if an error occurs on one of them, the original logical state can still be recovered using majority voting.

With only 2 qubits, majority logic is not possible. If the two qubits differ (e.g., one is in state 0 and the other in state 1), the system cannot determine which one is correct, as there is no third qubit to detect the error using the majority method. This makes it fundamentally unsuitable for a true repetition code, which requires both detection and correction of errors through redundancy.

The minimum number of qubits required to implement a valid repetition code is three. This allows for a single error to be identified and corrected based on the value that appears in the majority of the qubits. Using fewer than three qubits undermines the purpose of the repetition code and prevents reliable correction.

**_3-Qubit Code: Detection and Correction (Single Error)_**

The 3-qubit repetition code addresses this limitation by enabling both error detection and correction. With three qubits encoding a logical state, the majority voting mechanism allows the system to determine which qubit has flipped in case of an error. For example, if two qubits remain the same and one qubit flips, the majority can be used to identify the correct state, and the flipped qubit can be corrected accordingly. However, this code can only correct a single bit-flip error. If more than one qubit flips simultaneously, the system will not be able to recover the original logical state, as there is no majority to determine the correct value.

**_4-Qubit Code: Detection and Correction, but Inefficient_**

While a 4-qubit repetition code can detect and correct single-bit flip errors, it offers no advantage over the 3-qubit code. The extra qubit adds redundancy but doesn’t improve error correction, as the code still fails if two qubits flip. This makes it an inefficient use of resources.

So, the 3-bit repetition code protects against a single error of a specific type, either a bit-flip (X) or a phase-flip (Z) and is not capable of handling multiple errors or combined (Y) errors. If correction is needed for more than one qubit or both X and Z errors, more advanced codes are required. **[Shor’s 9-bit code](https://qniverse.in/docs/qec-shors-nine-qubit-code/) **extends this idea by combining repetition strategies to protect against both bit-flip and phase-flip errors across all 9 qubits, enabling correction of any single-qubit error.

## Flow/Working of 3-bit repetition code

#### _Encoding_

In quantum error correction, encoding is the process of transforming a single logical qubit into a larger entangled state across multiple physical qubits, in order to protect the information against errors. The goal is to add redundancy without losing the quantum nature of the state, particularly its superposition and coherence.

  * Transforms one logical qubit into three physical qubits to protect against bit-flip
  * Starts with the logical qubit in any arbitrary state.
  * Two additional qubits are initialised to |0⟩.
  * Apply CNOT from the logical qubit to each of the other two physical qubits.
  * This entangles the qubits and distributes the quantum information.
  * Enables error detection and correction using majority voting.

**For phase-flip encoding:**

To extend the 3-qubit repetition code for phase-flip error correction, the encoding is performed in the Hadamard basis**.** This is achieved by applying a Hadamard gate to all three physical qubits before the error simulation process.

#### _Simulating Errors_

After encoding the logical qubit into three physical qubits, we simulate the presence of an error to model the effects of noise in a quantum system. Depending on the type of error bit-flip or phase-flip, the required Pauli operator is applied to one of the qubits. This simulation is essential for testing the ability of the code to detect and correct errors.

****

#### Bit-Flip Error Simulation

  * Simulates the effect of noise by introducing a controlled error after encoding.
  * A bit-flip is modelled using the Pauli-X gate, which flips ∣0⟩ to ∣1⟩ and vice versa.
  * The error is applied to only one qubit at a time since the 3-qubit code can correct a single bit-flip.
  * For example, applying an X gate on qubit 0 alters the logical state to simulate a bit-flip on the first qubit

#### Phase-Flip Error Simulation

  * Simulates phase noise by introducing a phase-flip error after encoding.
  * A phase flip is modelled using the Pauli-Z gate, which flips the sign of the ∣1⟩ component of a qubit’s state.
  * The error is applied to only one qubit at a time, as the basic 3-qubit code handles only bit-flips—this is mainly for analysis purposes.
  * For example, applying a Z gate on qubit 0 changes the phase of the state, without altering its measured bit value

After introducing Z error, apply Hadamard gate to all three physical qubits to bring it back to computational basis (∣0⟩, ∣1⟩) from Hadamard basis.

#### _Error detection (Syndrome measurement)_

After an error is introduced in the encoded quantum state, the next step is to detect and identify which qubit, if any, has been affected. This is done through a process called syndrome measurement, which uses additional qubits called ancilla qubits to extract error information without disturbing the actual data qubits. This allows the error to be located without collapsing the encoded quantum state.

These measurements output (called the syndrome) indicate whether the pairs match:

  * A result of **0** (from the ancilla) means the qubits are the same (no disagreement).
  * A result of **1** means the qubits are different (one likely flipped).

00 | No error  
---|---  
10 | Error in qubit 0  
11 | Error in qubit 1  
01 | Error in qubit 2  
  
#### _Error Correction_

After detecting and locating an error using syndrome measurements, a correction gate is applied to the affected qubit.

Pauli operators are self-inverse, so applying the same gate (e.g., X or Z) again reverses the error.

**Bit-flip correction** :

  * If the error is on qubit 0, apply an X gate to qubit 0 to restore the original logical state.
  * Example: α|100⟩ + β|011⟩ → α|000⟩ + β|111⟩ (after correction)

**Phase-flip correction** :

  * If the error is on qubit 2, apply a Z gate to qubit 2.
  * Apply Hadamard gates if needed to work in the |+⟩, |–⟩
  * Example: α|+ – +⟩ + β|- + -⟩ → α|+ + +⟩ + β|- – -⟩ (after correction).

This correction uses ancilla qubits to extract error syndromes without collapsing the quantum state, as it reveals only the error location, not the encoded logical information.
