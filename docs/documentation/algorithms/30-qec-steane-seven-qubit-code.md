---
title: "QEC: Steane Seven-Qubit Code"
category: "Algorithms"
url: "https://qniverse.in/docs/qec-steane-seven-qubit-code/"
breadcrumb: "Home > Docs > Algorithms > QEC: Steane Seven-Qubit Code"
---

# QEC: Steane Seven-Qubit Code

> **Category:** Algorithms | **Source:** [https://qniverse.in/docs/qec-steane-seven-qubit-code/](https://qniverse.in/docs/qec-steane-seven-qubit-code/)


## What is the Steane Code?

The Steane code is a foundational quantum error-correcting code that encodes one logical qubit into seven physical qubits. It is built using the structure of the classical [7,4] Hamming code and is an example of a CSS (Calderbank–Shor–Steane) code, a family of codes that leverage two classical linear codes to correct both bit-flip and phase-flip errors in quantum systems.

In this construction, the Steane code inherits the parity-check matrix (H) from the [7,4] Hamming code, which allows it to identify error locations through syndrome extraction. The same Hamming code structure is applied in both the computational basis (for bit errors) and the phase basis (for phase errors). This symmetry makes the Steane code one of the simplest and most elegant examples of a quantum error-correcting code that treats different types of errors on equal footing.

The Steane code is important because it combines theoretical clarity with practical relevance. Its relatively small size makes it suitable for analysis, simulation, and early experimental demonstrations, while its CSS structure supports efficient fault-tolerant operations. As such, it is widely studied as an introductory model in quantum error correction, serving both as a teaching example and as a building block for more advanced fault-tolerant quantum computing schemes.

**Presenting here with a short video tour of the implementation of Steane Seven Qubit Code in Qniverse**

[▶️ Video Demonstration: Steane-7-qubit-algo-2.mp4](https://qniverse.in/wp-content/uploads/2025/09/Steane-7-qubit-algo-2.mp4)

## How is encoding done in Steane Code?

**Encoding:**

The Steane code encodes a single logical qubit into seven physical qubits by distributing the information of the input state across multiple entangled qubits. The encoding is based on the [7,4] Hamming code, which provides the mathematical structure for generating valid codewords.

_**Input State:** _

An arbitrary qubit state to be protected is:

∣ψ⟩ = α∣0⟩ + β∣1⟩

The goal of the encoding is to map this single-qubit state into a seven-qubit encoded state:

∣ψL​⟩ = α∣0L​⟩ + β∣1L​⟩

where ∣0L⟩ and ∣1L⟩ are the logical codewords of the Steane code.

_**Codeword Construction:** _

The Steane codewords are derived from the [7,4] Hamming code:

  * ∣0L⟩ is formed as an equal superposition of the even-weight Hamming codewords.
  * ∣1L⟩ is formed as an equal superposition of the odd-weight Hamming codewords.

This ensures that the logical 0 state and logical 1 state are embedded into a 7-qubit space defined by the Hamming code, where the arrangement of data and parity bits determines the encoded superpositions.

_**Encoding Procedure:** _

  * Start with an arbitrary input qubit ∣ψ⟩ = α∣0⟩ + β∣1⟩ and six ancilla qubits initialized to ∣0⟩.
  * Apply Hadamard and CNOT gates so that the final seven qubits reproduce the structure of the [7,4] Hamming code, with four qubits corresponding to data positions and three qubits corresponding to parity positions. In this mapping, parity qubits occupy positions 1, 2, and 4, while data qubits occupy positions 3, 5, 6, and 7. Each parity qubit is connected by CNOT gates to a specific subset of data qubits: parity qubit 1 checks qubits (3, 5, 7), parity qubit 2 checks qubits (3, 6, 7), and parity qubit 4 checks qubits (5, 6, 7). These controlled operations ensure that the logical information is consistently spread across the entire seven-qubit encoded block.
  * The output is the encoded state ∣ψL⟩, expressed as a seven-qubit configuration where the logical qubit’s information is distributed across all qubits in alignment with Hamming code rules.

**Simulating Errors:**

To model noise in the Steane code, errors can be simulated by applying Pauli-X, Pauli-Z, or both (Pauli-Y) to any one of the seven physical qubits after encoding. Errors may be introduced on different qubits, but only one qubit should be affected at a time, since the Steane code is designed to detect and correct any arbitrary single-qubit error, including bit-flip, phase-flip, or combined errors. This simulation validates the code’s fault-tolerance against common quantum noise models.

## What is Syndrome Measurement in Steane Code?

**Syndrome Measurement:**

Syndrome measurement in the Steane code is based on its stabilizer generators. The Steane code has six stabilizers: three of them are of X-type and three are of Z-type, each one corresponding to a parity check from the classical [7,4] Hamming code. These stabilizers are:

**Z-type stabilizers:**

  * SZ1​= Z4 Z5 Z6​ Z7
  * SZ2​= Z1 ​​Z3 Z5 Z7​
  * SZ3​= Z2​ Z3​ ​Z6​ Z7​

**X-type stabilizers:**

  * SX1​= ​X4 ​X5 ​X6 ​X7
  * SX2​= X1​ X3​ X5​ X7
  * SX3​= X2​ X3​ ​X6​ X7

To measure these stabilizers, the code requires six ancilla qubits in total, three dedicated to Z stabilizers and three dedicated to X stabilizers.

The Z-type stabilizers are used to detect bit-flip (X) errors. For example, to measure the stabilizer Z1Z3Z5Z7​ ​, an ancilla qubit initialized in ∣0⟩ is used as the target, and CNOT gates are applied with qubits 1, 3, 5, and 7 as controls. The same method is repeated for Z4 Z5 Z6​ Z7​ and Z2​ Z3​ ​Z6​ Z7​, with their respective data qubits. After measurement of the ancillas, the results give syndrome bits that indicate the presence and possible location of X errors.

The X-type stabilizers are used to detect phase-flip (Z) errors. For example, to measure the stabilizer X1​ X3​ X5​ X7​, the ancilla qubit is first prepared in the ∣+⟩ state using a Hadamard gate. CNOT gates are then applied with the ancilla as control and qubits 1, 3, 5, and 7 as targets. A Hadamard gate is applied again before measurement to return the ancilla to the computational basis. This same procedure is repeated for the stabilizers X2​X3​​X6​X7 ​ and ​X4X5X6X7​. The measurement outcomes from these ancillas give syndrome bits that reveal the positions of Z errors.

**Error on qubit** | **Z-type syndromes (detect X errors)** | **X-type syndromes (detect Z errors)**  
---|---|---  
**No error** | **000** | **000**  
**Qubit 1** | **100** | **100**  
**Qubit 2** | **010** | **010**  
**Qubit 3** | **110** | **110**  
**Qubit 4** | **001** | **001**  
**Qubit 5** | **101** | **101**  
**Qubit 6** | **011** | **011**  
**Qubit 7** | **111** | **111**  
  
These six syndrome bits, written in the order of the stabilizer generators following the convention of Preskill (Chapter 7), together uniquely identify both the location and the Pauli type of any single-qubit error, thereby enabling the Steane code to correct all single-qubit errors.

**Error Correction in Syndrome Measurement**

After an error is detected using syndrome measurement, correction is applied by performing the appropriate Pauli operation on the identified qubit. If the syndrome indicates a bit-flip error, a Pauli-X gate is applied to the affected qubit. If the syndrome indicates a phase-flip error, a Pauli-Z gate is applied. If both errors are present, a Pauli-Y correction can be applied, which is equivalent to applying both X and Z. Since the Steane code corrects any arbitrary single-qubit error, the correction is always localized to the specific qubit indicated by the syndrome without disturbing the logical information.

**Decoding:**

Decoding begins by reversing the encoding process so that the logical qubit is disentangled from the redundant qubits. The ancilla qubits and parity information, which were added during encoding, are disentangled using CNOT and Hadamard gates in the reverse order of the encoding circuit. Once disentanglement is complete, the original logical qubit state is recovered on a single qubit, while the other qubits return to fixed states (|0⟩). The measured syndrome results are discarded at this stage, since only the corrected logical qubit needs to be retained. This ensures that the protected logical information can be safely extracted after error correction has been applied.
