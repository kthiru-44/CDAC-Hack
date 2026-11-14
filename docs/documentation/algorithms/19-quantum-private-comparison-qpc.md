---
title: "Quantum Private Comparison(QPC) Algorithm"
category: "Algorithms"
url: "https://qniverse.in/docs/quantum-private-comparisonqpc-algorithm/"
breadcrumb: "Home > Docs > Algorithms > Quantum Private Comparison(QPC) Algorithm"
---

# Quantum Private Comparison(QPC) Algorithm

> **Category:** Algorithms | **Source:** [https://qniverse.in/docs/quantum-private-comparisonqpc-algorithm/](https://qniverse.in/docs/quantum-private-comparisonqpc-algorithm/)


## Introduction

A quantum algorithm has been implemented to address the Socialist Millionaire problem. The primary objective of this algorithm is to enable two parties, Alice and Bob, to securely determine the equality of their private information, such as numerical data, without revealing this information to each other or an assisting third party.

This implementation is based on the methodology outlined in the research paper** _“Quantum private comparison for the socialist millionaire problem” by Hou, Sun, and Zhang (2024)._** The implementation focuses on realizing and validating the paper’s core concepts.

Key aspects of this approach, which the implementation aims to put into practice and check, are:

  * **Enhanced Security:** The algorithm employs a specific quantum operation, namely a rotation operation. This is done to maintain the security of the comparison process within the quantum domain, rather than relying on conventional comparison methods like bitwise XOR, which can produce potentially vulnerable classical data.
  * **Practicality:** The algorithm utilizes quantum resources that are relatively accessible and manageable with current technology. Specifically, it uses Bell state pairs of entangled qubits, and simple quantum operations, such as single-qubit rotations and Bell measurements. This design choice enhances the potential real-world applicability of the method.

The implementation successfully realizes the core comparison logic of the protocol.

**Presenting here with a short video tour of how the QPC Algorithm is implemented and runs in Qniverse**

[▶️ Video Demonstration: QPC-algo.mp4](https://qniverse.in/wp-content/uploads/2025/04/QPC-algo.mp4)

## Algorithm Description

The algorithm helps compare two pieces of information, X and Y, each represented by n bits, with assistance from a third party (TP), Charlie, who is trusted to follow the rules but might try to learn secrets if possible (semi-honest). Alice and Bob also need a shared secret key, KAB​ (also n bits long), which they must establish securely beforehand (using a method like Quantum Key Distribution).

The central quantum action used is a specific type of **rotation operation**. Imagine the state of a qubit represented on a sphere (the Bloch sphere); this operation rotates the state around the vertical (Y) axis by a certain angle. The angle of rotation depends on the information being encoded.

Here are the steps of the protocol implemented:

  1. **Step 1: Preparation (Charlie)**

  * Charlie creates n pairs of specially linked (entangled) qubits. These pairs are in one of four specific configurations known as **Bell states** , chosen randomly for each pair. Let’s call the j-th pair Gj.
  * He separates the qubits into two groups, S1​ and S2. S1​ gets the first qubit from each pair Gj, and S2​ gets the second qubit.

  1. **Step 2: Distribution (Charlie - > Alice/Bob)**

  * Charlie sends the sequence S1​ directly to Alice and S2​ directly to Bob.
  * **Note:** The original protocol includes inserting “decoy” qubits and performing a security check here to detect eavesdropping. This decoy state mechanism was skipped in our implementation.

  1. **Step 3: Encoding & Operation (Alice, Bob)**

  * For each qubit j in her sequence S1, Alice performs two rotation operations, one after the other. The rotation angle depends on her corresponding input bit (xj​) and the shared key bit (kj​). If a bit is 1, she performs a 180-degree rotation; if it’s 0, she does nothing (a 0-degree rotation). The sequence after her operations is called SA.
  * Bob does the same for each qubit j in his sequence S2, using his input bit (yj​) and the key bit 
  * (kj​) to determine the rotations. His resulting sequence is SB.

  1. **Step 4: Return (Alice/Bob - > Charlie)**

  * Alice sends her modified sequence SA​ back to Charlie, and Bob sends his modified sequence SB​ back to Charlie.
  * **Note:** Similar to Step 2, the original protocol includes another decoy state insertion and security check during this transmission. This step was also skipped in our implementation.

  1. **Step 5: Measurement & Comparison (Charlie)**

  * Charlie takes the j-th qubit from Alice’s final sequence (SA​) and the j-th qubit from Bob’s final sequence (SB​). Remember, these two qubits started as an entangled Bell pair, Gj. He performs a **Bell-basis measurement** on this pair, which checks which of the four Bell states the pair is currently in.
  * He does this for all n pairs.
  * Charlie compares the measurement result for each pair with the original Bell state (Gj​) he created for that pair back in Step 1.

  1. **Step 6: Result Announcement (Charlie)**

  * If _every single one_ of the n measurement results matches the original Bell state Charlie started with for that pair, he concludes that Alice’s and Bob’s inputs were identical (X=Y).
  * If _even one_ measurement result is different from the original state, he concludes their inputs were different (X=Y).
  * Charlie then tells Alice and Bob the simple result: “equal” or “not equal”.

The reason this works is that the combined effect of Alice’s and Bob’s rotations on a pair of qubits cancels out completely (leaving the pair in its original Bell state, apart from an undetectable overall change) only when their input bits (xj​ and yj​) for that position were the same.

## Protocol Objectives

• Equality Comparison: Determine if X = Y for Alice’s and Bob’s private inputs.  
• Privacy: Ensure X and Y remain undisclosed to each other and the third party.  
• Security: Protect against external and insider attacks.  
• Practicality: Use simple quantum technologies (Bell states, rotation operations, Bell-basis measurements for ease of implementation

## Security Analysis

**1\. External Attacks**

The protocol resists external eavesdroppers (e.g., Eve) attempting attacks like intercept measure-resend:  
• Rotation Operations: Inputs are encoded as rotation angles. Without knowing the angles or KAB, Eve cannot infer initial Bell states or private inputs by measuring intercepted qubits.  
• Quantum Channel Security: The quantum states transmitted are Bell states modified by rotations, indistinguishable without knowledge of the initial states and rotations.

**2 Insider Attacks**

• Attack by Charlie: Charlie prepares Bell states and performs measurements but cannot infer X or Y. Identical outcomes arise from different rotation pairs,e.g.,**Ry(π), Ry(π) vs. Ry(0), Ry(0)** , making inputs indistinguishable.  
• Attack by Alice or Bob: Alice cannot access Bob’s inputs (encoded in):  
Ry(πY ) without intercepting S2 or SB. Since there is no direct communication between Alice and Bob, and Charlie’s measurements only reveal equality, such attacks fail.

## Simulation Experiments

Two simulation cases verify the protocol:  
• Case 1 (X =Y =5): Binary X =Y =101, key KAB =110, initial Bell states:

**{|Ψ+⟩,|Ψ+⟩,|Φ+⟩}**

Alice and Bob apply identical rotations, e.g.:  
**{Ry(π),Ry(0),Ry(π)} and {Ry(π),Ry(π),Ry(0)}**  
Measurements match initial states, confirming X = Y.

• Case 2 (X =5,Y =4): Binary X = 101, Y = 100, same key and states. Different rotations lead to mismatched measurements, confirming X Y

## Performance Evaluation

An evaluation of the implementation’s performance was conducted using the standards defined in the original paper:

  * **Correctness:** The implementation was tested with a variety of inputs for Alice (X) and Bob (Y), along with different shared keys (KAB). The system consistently produced correct results for the core comparison logic. Specifically, it reported “equal” when X and Y were identical, and “not equal” when they differed. This is held under ideal conditions, i.e., in the absence of transmission errors or eavesdropping. This confirms the expected behavior of the comparison logic, based on the effects of the rotation operations on the Bell states.
  * **Security:** This implementation does not incorporate the decoy state method for detecting eavesdropping. Consequently, it lacks the protection against external attacks, such as man-in-the-middle attacks, during the quantum communication phases (Steps 2 and 4) that is present in the original protocol. The security against insider attacks, where Charlie does not learn X or Y, and Alice and Bob do not learn each other’s inputs directly, relies solely on the quantum properties of the core comparison mechanism and the assumption of secure channels.
  * **Qubit Efficiency:** The implementation, mirroring the protocol’s design, uses _n_ pairs of entangled qubits (a total of 2 _n_ qubits) to compare _n_ bits of classical information. This results in a theoretical qubit efficiency of 50%, with one bit compared for every two qubits used.
  * **Resource Usage:** The primary quantum operations involved in the implementation are single-qubit rotations and Bell measurements. These operations are considered relatively standard within the capabilities of current quantum platforms.

In summary, when compared to the theoretical framework presented in the paper, the implementation successfully replicates the protocol’s core comparison logic. It achieves the expected correctness, under ideal conditions, and maintains the intended 50% qubit efficiency. However, it does not implement the security features designed to protect against eavesdropping.

## Conclusions

  1. The project successfully implemented the core quantum private comparison logic using rotation operations, as suggested by Hou, Sun, and Zhang. Testing confirmed that the implementation functions correctly on the platform for determining the equality of two private inputs, assuming secure communication channels.Key takeaways from this implementation include:
     * Validation that using rotation operations presents a practical alternative to XOR-based comparison methods for the core logic.
     * Confirmation of the protocol’s core design, achieving 50% qubit efficiency.

Limitations of this implementation and the protocol include:

  1. It needs a third party (TP) who is trusted to follow the protocol (semi-honest).
  2. It only tells if the inputs are equal or not; it doesn’t determine which is larger if they are different.

Future steps could include:

  1. Improving the implementation to better handle noise on real quantum hardware.
  2. Trying to extend the protocol to compare magnitudes (greater than/less than).
  3. Looking into ways to implement similar comparisons with less reliance on, or without, a third party.
  4. Testing the implementation with larger inputs (increasing n).
