---
title: "Running Circuits"
category: "User Guide"
url: "https://qniverse.in/docs/running-circuits/"
breadcrumb: "Home > Docs > User Guide > Running Circuits"
---

# Running Circuits

> **Category:** User Guide | **Source:** [https://qniverse.in/docs/running-circuits/](https://qniverse.in/docs/running-circuits/)


**Running Quantum Circuits: A Guide**

[▶️ Video Demonstration: running-circuits.mp4](https://qniverse.in/wp-content/uploads/2025/04/running-circuits.mp4)

**1\. Platform Selection**

  * **CPU (Simulators):**

**Simulators:** Ideal for initial circuit design, testing, and debugging. They offer high fidelity and can simulate small- to medium-sized circuits efficiently.

    * **Advantages:** Fast execution, low cost, easily accessible.
    * **Disadvantages:** Limited to smaller circuits due to exponential resource growth with increasing qubit number.

**Examples:** Qiskit Aer and Cirq.

  * **GPU (Simulators):**

**Simulators:** Leverage the parallel processing power of GPUs to accelerate certain simulation tasks.

**Advantages:** Can simulate larger circuits than CPUs alone.

**Disadvantages:** Still limited by the exponential resource growth of quantum simulations.

**Examples:** TensorFlow Quantum, NVIDIA cuQuantum, GPU A100.

  * **QPUs (Quantum Processing Units – Real Quantum Hardware):**

  * Access to real quantum hardware for executing actual quantum circuits. 
    * **Advantages:** Execute true quantum algorithms and explore real-world quantum phenomena.
    * **Disadvantages:** Limited qubit count, high noise levels, longer execution times, and limited availability.

**2\. Job Submission and Result Viewing**

  *     * **Create an Account:** Register with the chosen platform
    * **Circuit Definition:**
      * Use a programming language (e.g., Python with Qiskit, Cirq) to define your quantum circuit.
      * Specify parameters like the number of qubits, gates, and measurements.
    * **Job Submission:**
      * Submit your circuit to the chosen platform (simulator, GPU, or QPU).
      * Configure job parameters (e.g., number of shots, backend selection).
    * **Job Monitoring:**
      * Track the progress of your job on the platform’s dashboard.
    * **Result Retrieval:**
      * Download the results of your circuit execution (e.g., measurement outcomes, execution time).

**3\. Saving and Exporting Work**

  * **Code:**
    * Save your circuit definition code (text format) for reproducibility and collaboration.
  * **Results:**
    * Export results (measurement data, execution times) in test format or analysis and visualization.
  * **Circuits:** Some platforms allow you to save and load circuit definitions for later use.

**Key Considerations:**

  * **Circuit Complexity:** For small circuits, simulators are generally sufficient. For larger circuits or when exploring real quantum phenomena, consider GPUs or QPUs.
  * **Noise and Errors:** Real quantum hardware is subject to noise.
