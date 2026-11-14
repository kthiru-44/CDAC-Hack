---
title: "Building Circuits"
category: "User Guide"
url: "https://qniverse.in/docs/building-circuits/"
breadcrumb: "Home > Docs > User Guide > Building Circuits"
---

# Building Circuits

> **Category:** User Guide | **Source:** [https://qniverse.in/docs/building-circuits/](https://qniverse.in/docs/building-circuits/)


**Step 1: Select a Gate**

  1. Identify the quantum gate you want to use from the “Gates Palette” on the top side of the interface.
  2. Click and hold the desired gate.

**Step 2: Place the Gate on the Circuit**

  1. Drag the selected gate to the desired position on the circuit diagram.
  2. Release the mouse button to drop the gate on the qubit line(s) where you want it to act.

**Step 3: Connect Gates (if needed)**

  1. Some gates require connections between qubits, mainly multi qubits, for adding a control and target, which a user can do by clicking a gate and choosing the option of Edit.

**Step 4: Add Measurement**

  1. Locate the “Measurement” gate in the gate pallet.
  2. Drag and drop the measurement gate onto the qubit line(s) you want to measure.

**Step 5: Arrange and Adjust**

  1. If necessary, adjust the positions of the gates on the circuit diagram to improve readability and organization
  2. You can drag and drop gates to different positions on the qubit lines.

**Step 6: Run the Circuit**

  1. Once you have designed your circuit, you can run it on a simulator from the many provided(CPU), GPU, or on a real quantum device(QPU)
  2. The interface will provide options for selecting the backend (simulator or device) running the simulation and obtaining the visualization or simulation output results.

**Additional Tips**

  * **Undo/Redo:** Use the “Undo” and “Redo” buttons to revert or reapply changes to your circuit.
  * **Manage:** To manage Quantum registers[(q)ubits] and Quantum registers(c) number as per user’s preference.
  * **Clear:** The “Clear” button allows you to start with a fresh circuit diagram.
  * **OpenQASM 2.0:** The code editor displays the OpenQASM 2.0 code representation of your circuit. You can modify the code directly if you are familiar with the language; is also available in Qiskit, Cirq, and CudaQ.

## Creating Custom Gates

**Here is a short video demonstrating how users can create a custom gate and perform related operations.**

[▶️ Video Demonstration: custom-gates.mp4](https://qniverse.in/wp-content/uploads/2025/04/custom-gates.mp4)

  1. **Design a Custom Gate:** Combine a sequence of existing gates to create a new, more complex gate. This can help modularize your circuit design or represent frequently used subroutines.

  1. **Name and Describe the Gate:** Give the custom gate a descriptive name(only 3 letters) and an optional description to help you and others understand its purpose, which a user can see by clicking the **(i)** option

  1. **Save the Custom Gate:** The interface provides a mechanism to save your custom gate for future use by clicking the save option.

**Using Custom Gates**

  1. Once you have created a custom gate, it will appear in the gate palette along with the pre-defined gates.
  2. You can then drag and drop your custom gate onto the circuit diagram like any other gate.
  3. The interface will automatically break down the custom gate into its basic gates when you run the circuit or view the detailed circuit representation when clicking gate expand.**[G]**.

**Additional Features:**

  * **Gate Expansion:** Clicking on a custom gate in the circuit diagram should expand it to show the underlying sequence of gates.

  * **Gate Information:** Clicking on a gate (custom or pre-defined) should display information about the gate, such as its representation and its effect on the qubit state.

  * **Gate Editing:** The ability to edit or modify existing custom gates.

  * **Gate Deletion:** The option to delete custom gates if they are no longer needed.
