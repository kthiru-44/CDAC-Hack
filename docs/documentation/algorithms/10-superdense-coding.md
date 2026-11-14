---
title: "Superdense Coding"
category: "Algorithms"
url: "https://qniverse.in/docs/super-dense-coding/"
breadcrumb: "Home > Docs > Algorithms > Superdense Coding"
---

# Superdense Coding

> **Category:** Algorithms | **Source:** [https://qniverse.in/docs/super-dense-coding/](https://qniverse.in/docs/super-dense-coding/)


## What is a Superdense Coding algorithm?

Superdense coding is a quantum communication protocol that enables two parties to communicate classical information using a single qubit and a shared entangled pair of qubits. This protocol takes advantage of the properties of quantum entanglement and the principles of quantum mechanics to achieve efficient communication.

Superdense coding allows for transmitting two classical bits of information using only one qubit. It leverages the concept of entanglement and requires a pre-shared entangled resource between the sender (Alice) and receiver (Bob).

**Below is a short video showing how the circuit looks for the 2-Qubit Selection with an “11” input for the secret message.**

[▶️ Video Demonstration: Superdense-coding.mp4](https://qniverse.in/wp-content/uploads/2024/05/Superdense-coding.mp4)

## How is Superdense Coding achieved?

**1\. Bell State:**

The protocol starts with creating a Bell state, which is a maximally entangled state of two qubits. This state can be represented as:
    
    
    ```python
    |Ψ⟩ = (|00⟩ + |11⟩) / √2   (where ⊗ denotes the tensor product)
    ```

Here, the first qubit belongs to Alice and the second belongs to Bob. The state is entangled, meaning the qubits are correlated, and their fates are linked.

**2\. Alice’s Operations (Encoding):**

Alice wants to send two classical bits (00, 01, 10, or 11) using this shared state. She performs different operations on her qubit depending on the message:

  * **No operation (00):** If Alice wants to send 00, she leaves her qubit unchanged (remains in the |0⟩ state).
  * **X-gate (01):** If Alice wants to send 01, she applies an X-gate (NOT gate) to her qubit, flipping it to the |1⟩ state. This operation can be expressed by the X-gate matrix:

**`X = [[0, 1], [1, 0]]`**

  * **Z-gate (10):** If Alice wants to send 10, she applies a Z-gate (phase flip gate) to her qubit. This operation can be represented by the Z-gate matrix:

**`Z = [[1, 0], [0, -1]]`**

  * **iY-gate (11):** If Alice wants to send 11, she applies an iY gate (equivalently XZ) to her qubit. This operation combines a bit flip and a phase flip, transforming the shared Bell state into a different orthogonal Bell state. After Alice sends her qubit, Bob can identify this Bell state through Bell-basis measurement and recover the message 11**.**

**3\. Sending the Qubit:**

After performing the chosen operation, Alice sends her qubit to Bob.

**4\. Bob’s Operations (Decoding):**

Bob now has both qubits (the entangled pair and the one sent by Alice). To decode the message, he performs a combination of controlled operations based on the information he already possesses (the entangled state):

  * **CNOT (controlled-NOT) followed by Hadamard Gate:** These operations manipulate the entangled state based on the state of Alice’s qubit. The specific details of the operation depend on the chosen encoding scheme (e.g., which gate corresponds to which message bit).

**5\. Measurement:**

Finally, Bob measures both qubits in the computational basis (usually the Z-basis). The outcome of these measurements reveals the message sent by Alice.

**Overall, the expressions involved in superdense coding lie in the manipulation of quantum states using gates like X, Z, and iY. The specific combination of gates used by Alice for encoding and the controlled operations used by Bob for decoding depends on the chosen implementation.**

**Additional Notes:**

  * Superdense coding showcases the power of entanglement for transmitting information more efficiently than classical communication.
  * The concept of Bell states and their properties play a crucial role in this protocol.
  * While seemingly transmitting two bits with one qubit, it’s important to remember that the entangled state was a shared resource created beforehand.

## How does Superdense Coding work in Quantum Computing?

  * **Entangled Qubits** : Initially, two parties, usually named Alice and Bob, share a pair of entangled qubits. Entanglement means the quantum states of the qubits are correlated in such a way that the state of one qubit depends on the state of the other, regardless of the distance between them.
  * **Encoding** : Alice wants to send classical information to Bob. She takes her half of the entangled pair and performs a quantum operation known as a quantum gate on it. By applying a specific quantum gate to her qubit, Alice can encode two classical bits of information onto her qubit.
  * **Transmission** : Alice sends her qubit to Bob through a quantum communication channel. Since the qubits are entangled, the state of Bob’s qubit becomes correlated with the state of Alice’s qubit as soon as she sends it, regardless of the physical distance between them.
  * **Decoding** : Upon receiving Alice’s qubit, Bob performs a specific quantum operation, the inverse of the one Alice applied, on his qubit. This operation allows Bob to extract the classical information encoded by Alice, effectively decoding the message.
  * **Classical Communication** : Finally, Bob communicates with Alice classically to confirm that he has received the message correctly.
