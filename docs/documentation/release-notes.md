---
title: "Qniverse Platform Release Notes"
category: "Platform"
url: "https://qniverse.in/release-notes/"
---

# Qniverse Platform Release Notes

> **Source:** [https://qniverse.in/release-notes/](https://qniverse.in/release-notes/)

# Release Notes

## 28-JULY-2026 – v1.6.0

We are excited to announce the latest Qniverse release, introducing major enhancements in simulation capabilities, New Quantum Algorithms, more clear documentation and overall platform usability.

**Platform Features**

  * **Added New CPU Simulators:**
    * Added **Aer Stabilizer Simulator** (`aer_simulator_stabilizer`) for efficient simulation of Clifford circuits.****
    * Added **Aer Matrix Product State (MPS) Simulator** (`aer_simulator_matrix_product_state`) for scalable simulation of low-entanglement quantum circuits.
    * Added **Cirq Clifford Simulator** (`cirq_clifford_simulator`) for fast simulation of Clifford-based quantum circuits.
    * Added **NVIDIA CUDA-Q Stabilizer Simulator** (`nvidia_cudaq_stabilizer_simulator`) for high-performance stabilizer circuit simulation.
  * **Added New GPU Simulators:**
    * Added **Aer Tensor Network GPU Simulator** (`aer_simulator_tensor_network_gpu`) for accelerated tensor network-based quantum circuit simulation on GPUs.
    * Added **NVIDIA CUDA-Q Tensor Network Simulator** (`nvidia_cudaq_tensor_network_simulator`) for efficient GPU-accelerated simulation of large quantum circuits.
    * Added **NVIDIA CUDA-Q Matrix Product State (MPS) Simulator** (`nvidia_cudaq_mps_simulator`) for scalable GPU-based simulation of low-entanglement quantum systems.
  * **Added New VECTOR Simulator:**
    * Added **CSIM Vector Simulator** (`csim_vector_simulator`) for optimized quantum circuit simulation on vector processing hardware.
  * **New Algorithms:**
    * Added **Max-Cut using the Quantum Approximate Optimization Algorithm (QAOA)** for solving combinatorial optimization problems.
    * Added **Quantum Digital Signature (QDS)** algorithm for demonstrating secure quantum communication and authentication protocols.
  * Added comprehensive documentation for the **Noise Model** , **Max-Cut (QAOA)** algorithm and **Quantum Digital Signature (QDS)** algorithm.

**Bug Fixes**

  * Added a Search option in the Compute Resources page for quick resource discovery.
  * Improved the **Superdense Coding** algorithm by swapping **Alice** and **Bob** qubits for a more intuitive and accurate representation.
  * Standardized quantum gate and operation names in the Gate Information modal for consistency across the platform.
  * Fixed the Export functionality on the Job Details page for all graph types.
  * Resolved the **Country** and **State** selection issue on the **Registration** page.
  * Fixed the **Undo/Redo** functionality in the **Circuit Builder** to ensure reliable circuit editing.

## 21-MAY-2026 – v1.5.0

We are excited to announce the latest Qniverse release, introducing major enhancements in simulation capabilities, Quantum SDK integration, Quantum Machine Learning improvements, premium feature segregation, and overall platform usability.

**Platform Features**

  * **Qniverse State Vector Simulator:** Introduced the new Qniverse State Vector Simulator backend for efficient and accurate quantum circuit simulation.
  * **Quantum SDK (QSDK):** Added the new QSDK feature to support enhanced quantum application development and workflow integration.
  * **QSDK Documentation:** Comprehensive QSDK documentation has been added to help users quickly get started with development, APIs, and integration workflows.
  * **Algorithm Tooltips:** Added informative tooltips for all algorithms to improve usability and provide better guidance to users during workflow creation.
  * **QSVM Algorithm Enhancements:** Updated the QSVM (Quantum Support Vector Machine) implementation with: 
    * Two new kernels: 
      * ZZ Feature Map
      * Pauli Feature Map
    * Optimized implementation for improved prediction accuracy and performance.
  * **Premium & Non-Premium Algorithm Segregation:** Introduced Premium and Non-Premium categorization for selected algorithms to provide differentiated access based on user subscription plans.
  * **Enhanced QML Data Upload Support:** Increased dataset upload capabilities for Quantum Machine Learning workflows: 
    * Non-Premium Users: 
      * Supports CSV uploads up to 25,000 records with up to 10 features
    * Premium Users: 
      * Supports CSV uploads up to 150,000 records with up to 16 features

**Bug Fixes**

  * Copy-Paste Gate Functionality 
    * Fixed issues related to copy-paste operations for quantum gates within the circuit editor.Uniform Colour Coding for Matrix Visualization
  * Photonic Circuit Export 
    * Resolved issues with the export functionality for photonic circuits from the Job Details page.
  * Noise Model Visibility 
    * Added a Noise Model indicator in the Job Details page to clearly specify whether a circuit execution was performed: 
      * With Noise
      * Without Noise

## 17-FEBRUARY-2025 – v1.4.0

**Platform Features**

  * **Portfolio Optimization using QAOA:** Upgraded the implementation for improved performance and reduced execution time, optimizing the hybrid quantum–classical workflow for faster QUBO formulation and QAOA-based portfolio optimization.
  * **N-Qubit Quantum Teleportation:** Implemented a generalized teleportation protocol enabling the transfer of an arbitrary (unknown or user-defined) _n_ -qubit quantum state between distant nodes using pre-shared entangled Bell pairs and classical communication channels.
  * **Grover Search for Multiple Targets:** Implemented Grover’s algorithm with support for multiple target elements, enabling quadratic speedup for searching unsorted databases.
  * **Vector Backend:** Added a new Simulation on Vector Card as a backend for enhanced statevector-based simulations.
  * **QPU Support:** Integrated the new Tuna-9 Quantum Processor and retired Spin-2+ and Starmon-7 Quantum processors from Quantum Inspire.
  * **IBM Quantum Integration:** Integrated connectivity to IBM Quantum Computers using the latest APIs.
  * **Noise Model:** Introduced a unified and configurable hybrid noise framework for superconducting qubit simulators, incorporating SPAM (state preparation and measurement), depolarizing noise, thermal relaxation (T1/T2 with gate-time awareness), and coherent gate over/under-rotation errors. Noise is applied post-transpilation to the Rx, Ry, Rz, CX basis, enabling realistic noisy simulation on Qiskit, Cirq, and CUDA-Q simulators.
  * **FPGA Backend:** Restored the fpga_simulator and also added a new fpga_dm_simulator backend with noise model support.
  * **Run Modal UI:** Upgraded the Run Model UI to support noise configuration with an improved and more user-friendly interface.
  * **JupyterHub UI Enhancement:** Updated the JupyterHub interface to align with the Qniverse layout, featuring a consistent design language and enhanced navigation for a more seamless and intuitive user experience.

**Bug Fixes**

  * Gate Colouring and Grouping Enhancement 
    * Updated gate classification and visual grouping into the following categories: 
      * Clifford Gates
      * Non-Clifford Gates
      * Parameterized Gates
      * Multi-Qubit Gates
      * Custom Gates
  * Uniform Colour Coding for Matrix Visualization 
    * Implemented Uniform color coding aligned with the state vector color scheme for matrix visualization of different gates across various basis.
  * Detail Report Output – Chart Colour Fix 
    * Resolved chart color inconsistencies in detailed reports, ensuring proper rendering and improved readability in both Dark Mode and Light Mode.

## 17-OCTOBER-2025 – v1.3.0

**Platform Features**

  * **FPGA Backend:** Simulate Quantum Algorithms on FPGA
  * **Algorithms:** Deterministic Quantum Search (DQS), Time-Evolution of Quantum System using Trotterization, QEC – Steane Seven-Qubit Code, Portfolio Optimization using QAOA
  * **Photonic Quantum Simulator:** Simulate Quantum Algorithms using Indigenous Quantum Photonic Simulator developed by C-DAC and realize the photonic component circuit.

**Bug Fixes**

  * For Quantum Machine Learning algorithms, the data-size support increased to 600
  * Compute Resources information updated for superstaq, quantum inspire, simulators
  * Creating custom gates with name in capital letters issue is solved.
  * Issue submitting job on superstaq solved.
  * Simon algorithm extended to support for decimal value 0
  * In QEC – Shor’s Nine-Qubit Code algorithm random error has been introducted along with bit-flip and phase-flip error.
  * CX-gate edit window the control and target qubit options are placed in order for better UI.
  * UI toggle button updated for dark & light theme.

## 04-AUGUST-2025 – v1.2.1

**Platform Updates & Fixes**

  * **Cirq Backend:** Resolved the issue where multiple measurement gates were incorrectly allowed on the same classical register. The interface now prompts users to assign separate classical registers for each measurement, enforcing this constraint at the client side itself!
  * **Compute Resources:** The “Credits” label has been renamed to “Balance Credits” for clearer resource tracking.

  * **Debugging & Probability Distribution:** Fixed the issue where the probability distribution was not displaying during the debug process. Resolved the issue where the “Ideal Probability Distribution” was not shown after clicking “Debug.”

  * **QPU Job Results:** Corrected the calculation, so the total probability of all states is now 100% instead of incorrectly summing.

  * **Grover’s Algorithm:** Added a measurement gate by default to Grover’s Algorithm circuits.

  * **QPU Simulations (Jobs Page):** Queue time and running time are now clearly displayed for simulations executed on QPU.

  * **IBM QPU Integration:** Due to a recent policy change, API key verification for IBM QPUs has been temporarily disabled until further notice.
  * **Superstaq Hardware:** Resolved the “Internal Server Error” that occurred during interactions with Superstaq hardware.

## 04-JULY-2025 – v1.2.0

**Features**

  * **Registration Page:** A user registration page has been created for seamless onboarding of the users.
  * **Credit System:** A new credit-based system has been implemented to manage simulation resource usage: 
    * **Welcome Bonus** : Users receive **150 free credits** upon successful registration.
    * **Credits Deduction per Simulation** : 
      * **CPU Simulation** : 5 credits
      * **GPU Simulation** : 10 credits
      * **QPU Simulation** : 2 credits
  * **Added new Simulators:**
    * **Qulacs** – A high-performance quantum circuit simulator optimized for large-scale quantum circuit simulations.
  * **Added new Algorithms:**
    * **QEC Algorithm** – Implements 3-bit repetition code for detecting and correcting single-qubit bit-flip and phase-flip errors.
    * **QEC Shor’s Nine-Qubit Code** – Encodes one logical qubit into nine physical qubits to correct arbitrary single-qubit errors using nested bit-flip and phase-flip codes.
    * **QHC Algorithm (Quantum Hierarchical Clustering)** – Utilizes quantum similarity measures like the swap test to perform hierarchical clustering with enhanced efficiency via quantum parallelism.
    * **QPCA Algorithm (Quantum Principal Component Analysis)** – Quantum-enhanced technique for dimensionality reduction using principles of quantum mechanics to speed up classical PCA.
    * **QPerceptron Algorithm** – Quantum-inspired version of the classical perceptron algorithm, leveraging quantum mechanics to tackle machine learning tasks more efficiently.
    * **QNN Algorithm (Quantum Neural Network)** – A hybrid framework combining quantum feature maps and variational quantum layers with classical neural networks for predictive tasks.

**Bug Fixes**

  * Fixed Issues in job submission to QPU hardware through Superstaq
  * Addressed a user query for installing seaborn library in Python 3 Kernel.
  * Updated the compute resources page showing all the QPUs.

## 06-MAY-2025 – v1.1.0

Features

  * **Shortcut Keys:** Added convenient shortcut keys for commonly used operations such as deleting gates, undoing and redoing actions. These shortcuts can be found listed under the ‘Help’ menu.
  * **Qubit Initialization:** Enhanced Qubit Initialization
  * **QuEst Simulator:** Added Quantum Exact Simulation Toolkit (QuEst). QuEst is a high performance simulator of quantum circuits, state-vectors and density matrices. QuEST uses multithreading, GPU acceleration and distribution to run lightning first on laptops, desktops and networked supercomputers.
  * **Added new Simulators:**
    * **Quest_simulator** – a high performance simulator of quantum circuits, state-vectors and density matrices.
    * **qsimcirq_simulator** – qsimcirq is a full wave function simulator written in C++. It uses gate fusion, AVX/FMA vectorized instructions and multi-threading using OpenMP to achieve state of the art simulations of quantum circuits. qsim is integrated with Cirq for CPU & GPU.
    * **qsimcirq_cuquantum_gpu_simulator** – GPU based Quantum Simulation using Qsim Cirq Simulator.
  * **Added new Algorithms:**
    * **Veto Algorithm** – The Veto Algorithm is a filtering technique that rejects events or data points based on predefined exclusion criteria to enhance the quality of the remaining dataset.
    * **QSVM Algorithm** – The QSVM (Quantum Support Vector Machine) algorithm leverages quantum computing to perform classification tasks by mapping data into a high-dimensional Hilbert space using quantum kernels for enhanced pattern recognition.
    * **QKMeans Algorithm** – The QKMeans (Quantum K-Means) algorithm is a quantum-enhanced clustering method that uses quantum distance estimation to group data into clusters more efficiently than classical K-Means.
    * **QPC for the socialist millionaire problem** – Quantum Private Comparison (QPC) for the Socialist Millionaire Problem enables two parties to compare whether their private inputs are equal—without revealing the actual values—using quantum properties like entanglement and superposition to ensure security and privacy.
    * **QKNN** – QKNN (Quantum k-Nearest Neighbors) is a quantum-enhanced classification algorithm that uses quantum parallelism and distance estimation to efficiently identify the k closest training samples to a query point for decision making.

**Bug Fixes**

  * Added horizontal auto scrolling of circuit composer while drag and drop the gates
  * Proper error messages are now implemented for all mandatory fields in the **Profile** section.
  * Proper error messages are now displayed for all required fields in the **Algorithm Input** section.
  * The issue where angles were not updating correctly while creating custom gates (RX, RY, RZ, P, U, and CP) has been resolved.
  * The issue with incorrect display of state angles (θ, λ, φ) during initialization has been fixed.

## 03-APR-2025 – v1.0.0

First Public Release

Features

  * **Powerful Circuit Builder:** The intuitive, drag-and-drop circuit builder enables users to visually design quantum circuits by selecting and placing quantum gates. 
  * **Rich Gate Palette:** Qniverse offers a Rich Gate Palette, enabling the construction of complex quantum circuits and custom gates by leveraging fundamental quantum gates.
  * **Realtime debug:** Qniverse facilitates real-time debugging of quantum circuits up to 6 qubits.
  * **Quantum Transpiler** : An integrated transpiler allows users to “**code once and execute on multiple platforms** “. It efficiently converts quantum circuits into formats supported by various simulation frameworks(Qiskit, CirQ, CudaQ etc.,) and transforms them into optimized instruction sequences compatible with different quantum hardware architectures(IBMs superconducting).
  * **Modular Libraries:** The in-built libraries enable users to work with pre-built components and easily integrate them into their workflows, enhancing development efficiency. Whether creating optimization algorithms, machine learning models, or cryptographic protocols, the modular libraries offer the flexibility needed to address a broad spectrum of quantum computing challenges.
  * **Ideal visualization:** Qniverse provides an intuitive visualization of probability distributions for quantum circuits up to 6 qubits, facilitating clear inference of quantum state outcomes.
  * **Algorithm Implementations** : Qniverse platform provides a powerful platform for implementing quantum algorithms. They don’t offer a one-stop shop for pre-built solutions, but rather equip you with the tools and knowledge to bridge the gap between theoretical and practical applications of quantum computing. This capability brings the power of quantum algorithms closer to real-world applications, advancing industries such as cryptography, materials science, and more.
  * **Connect to multiple Quantum Hardware:** Qniverse enables the execution of quantum circuits on multiple quantum hardware through seamless connectivity.
  * **Accelerated Quantum Computing:** Qniverse offers a diverse range of compute resources, including CPUs and classical accelerators like GPUs, FPGAs, and vector processors, to support quantum computing workflows.
  * **Persistent Quantum Circuit Access and SLURM Integration:** Qniverse integrates with HPC’s SLURM scheduler for efficient resource management and provides persistent access to previously executed quantum circuits.
  * **Documentation:** Qniverse offers comprehensive and user-friendly documentation, detailing its SDK, tools, and algorithms to facilitate seamless learning and implementation.
  * **Advanced Quantum Programming with JupyterLab:** Qniverse integrates JupyterLab, empowering advanced users to program, execute, and iterate on complex quantum circuits and algorithms within a familiar environment
