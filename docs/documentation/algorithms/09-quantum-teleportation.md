---
title: "Quantum Teleportation"
category: "Algorithms"
url: "https://qniverse.in/docs/quantum-teleportation/"
breadcrumb: "Home > Docs > Algorithms > Quantum Teleportation"
---

# Quantum Teleportation

> **Category:** Algorithms | **Source:** [https://qniverse.in/docs/quantum-teleportation/](https://qniverse.in/docs/quantum-teleportation/)


## What is the Quantum Teleportation Algorithm?

Quantum teleportation is a protocol that enables the transfer of the _precise quantum state_ (the quantum information) of a particle from one location (sender, traditionally named Alice) to another (receiver, traditionally named Bob), even if they are physically separated, without physically moving the particle itself. This algorithm is crucial for quantum communication and quantum networking protocols. This algorithm is crucial for quantum communication and quantum networking protocols. It uses pre-shared entangled states as a key resource. While entanglement correlations are instantaneous, the complete transfer of the _specific_ state requires an additional step of classical communication, preventing faster-than-light information transfer. ~~which allow for the instantaneous transfer of information to transport quantum information.

**Below is a short video showing how the circuit looks for the 3-Qubit Selection with the option to set the parameters α and β with the condition****α + β = 1 to be satisfied.**

[▶️ Video Demonstration: https://qniverse.in/wp-content/uploads/2025/03/quantum-teleportation.mp4?_=1](https://qniverse.in/wp-content/uploads/2025/03/quantum-teleportation.mp4?_=1)

## Process of Teleportation?

In quantum teleportation, entanglement in the Bell state (EPR pair) transfers an arbitrary quantum state between two distant observers, often called Alice and Bob. Quantum teleportation does not involve physically transferring information; instead, it involves transferring the state of the information. This concept is crucial in quantum networking and provides a means of transporting information that is otherwise very difficult to transport between two extremely distant locations, whether on Earth or across the universe.

The process of quantum teleportation starts with an entangled pair of particles shared between two parties, usually called Alice and Bob. Alice aims to teleport the state of a qubit to Bob. She performs specific measurements on her particles and sends the results to Bob through classical communication. Bob can then use this information to apply certain operations to his entangled particle, recreating the exact state that Alice intended to teleport.

The simplest quantum teleportation circuit requires only three qubits. Alice puts her qubit into a quantum superposition using what is known as a Hadamard gate, and then she entangles her qubit with Bob’s qubit using what is called a controlled-NOT gate. Alice then takes a third qubit, which has the quantum state to be teleported, and she entangles that qubit with her qubit. She then measures her two qubits in two different bases, which destroys her quantum information but gives her the classical information she needs to provide to Bob. Upon receipt, Bob uses the classical information to perform operations on his qubit that then allows him to use the teleported quantum state for whatever purposes. Because Bob had to wait for the classical information to arrive, no physics laws were violated.

Quantum teleportation allows transferring the unknown quantum state of a qubit (sender, Alice) to another qubit (receiver, Bob) at a distant location. While it doesn’t involve physically transmitting the qubit itself, it leverages the power of entanglement and classical communication to achieve this feat.

**1\. Initial State:**

Alice possesses a qubit in an unknown quantum state

`|ψ⟩_A = α |0⟩_A + β |1⟩_A`

where α and β are complex coefficients determining the state’s superposition.

Alice and Bob share an entangled pair of qubits, typically in a Bell state.

**|Φ⟩_AB = (|00⟩_AB + |11⟩_AB) / √2**

This Bell state represents the entanglement between Alice’s qubit (A) and Bob’s qubit (B).

**2\. Bell State Measurement (BSM):**

Alice performs a Bell state measurement on her qubit (the one to be teleported) and her half of the entangled pair. This measurement projects the two qubits onto one of the four Bell states:

`P(Φ+) = |Φ+⟩_AB ⟨Φ+|`

P(Φ-) = |Φ-⟩_AB ⟨Φ-|

P(Ψ+) = |Ψ+⟩_AB ⟨Ψ+|

P(Ψ-) = |Ψ-⟩_AB ⟨Ψ-|

The outcome of this measurement is classical information.

**3\. Classical Communication:**

Alice transmits the outcome of the BSM (which Bell states was measured) to Bob via classical communication (e.g., a phone call). This communication doesn’t transmit any quantum information itself, but Bob must perform the correct operation on his qubit.

**4\. Bob’s Operation (Pauli Corrections):**

Based on the classical information received from Alice, Bob applies one of the Pauli X (σ_x), Y (σ_y), or Z (σ_z) operators to his qubit to recover the original state:

  * If Alice measured |Φ+⟩, Bob does nothing (identity operation).
  * If Alice measured |Φ-⟩, Bob applies the Z-gate (σ_z).
  * If Alice measured |Ψ+⟩, Bob applies the X-gate (σ_x).
  * If Alice measured |Ψ-⟩, Bob applies both X (σ_x) and Z (σ_z) gates sequentially.

These Pauli corrections manipulate Bob’s qubit to match the original state Alice was trying to teleport.

**5\. Final State:**

After Bob applies the correction based on the BSM outcome, the final state ideally becomes:

**`|ψ⟩_B = α |0⟩_B + β |1⟩_B`**

**``**

This represents successful teleportation, where the unknown state of Alice’s qubit has been transferred to Bob’s qubit at a distance.

## Potential Usage/Applications of Quantum Teleportation:

Although quantum teleportation may seem far-fetched, it has been experimentally demonstrated and holds potential for various practical applications. Several potential uses of quantum teleportation include:

**QUANTUM INTERNET:**

Quantum teleportation is a fundamental building block for a future quantum internet. This network would enable the secure and efficient transfer of quantum information across vast distances. By teleporting qubits, we can establish long-range quantum communication channels that are inherently secure due to the principles of quantum mechanics. This could lead to applications like globally distributed quantum computing, enhanced secure communication for sensitive data, and novel forms of quantum cryptography that are impervious to eavesdropping. Furthermore, a quantum internet could connect quantum sensors and telescopes, enabling unprecedented levels of precision in scientific measurements.

**QUANTUM SENSING & METROLOGY:**

  * Improved: Quantum teleportation can significantly enhance the capabilities of quantum sensors and metrology devices. By teleporting the quantum state of a system being measured to a more accessible or less noisy location, we can improve the precision and sensitivity of measurements. For example, in gravimetry, magnetometry, and atomic clocks, teleportation could allow for more accurate readings by isolating the fragile quantum states from environmental noise. This could lead to breakthroughs in fields like navigation, fundamental physics research, and medical imaging

**QUANTUM COMMUNICATION:**

  * Improved: Quantum teleportation provides a mechanism for highly secure quantum communication. While it doesn’t directly transmit the qubit faster than light (due to the necessary classical communication), it is essential for tasks like quantum key distribution (QKD). QKD protocols leverage quantum mechanics to generate and distribute cryptographic keys that are provably secure against eavesdropping. Teleportation can be used within more complex QKD schemes to ensure the integrity of the quantum states carrying the key information over long distances, making it a crucial component for establishing secure communication networks for governments, financial institutions, and other entities requiring the highest level of security. It can also be used for tasks like blind quantum computation, where a user can have a quantum computation performed remotely without revealing their input or the computation itself.
