---
title: "Backend Systems"
category: "User Guide"
url: "https://qniverse.in/docs/backend-systems/"
breadcrumb: "Home > Docs > User Guide > Backend Systems"
---

# Backend Systems

> **Category:** User Guide | **Source:** [https://qniverse.in/docs/backend-systems/](https://qniverse.in/docs/backend-systems/)


This section displays the backend **Run** options for a user to run a circuit when submitted as a job on a CPU, GPU, FPGA, Vector, or QPU, along with High-Performance Computing (HPC) options and listed Backend options.

Click **Run****** in the upper right corner. Select an available system simulator or HPC system in the open model. Systems send the circuit to real quantum hardware when selected with the QPU option and simulators.

**Demonstrated here with a video tour of the options available at the backend to submit the job on CPU, GPU, FPGA, Vector Card, and QPU backend systems.**

[▶️ Video Demonstration: https://qniverse.in/wp-content/uploads/2025/04/backend-systems.mp4?_=1](https://qniverse.in/wp-content/uploads/2025/04/backend-systems.mp4?_=1)

## Select Processor

Gives a user the option to select from listed Processors, such as –

  * CPU
  * GPU
  * FPGA(Both FPGA simulator & FPGA_dm_simulator)
  * Vector
  * Quantum Processing Unit(QPU)

**Select HPC:** Gives a user an option to select from the listed HPCs, such as :

  * Param Utkarsh
  * QACC-Cluster

## Simulator Backend

The user has been presented with a range of options for the Simulator Backend, which they can select. Listed here are the CPU options available for the **QACC-Cluster and Param Utkarsh.**

## CPU

  * qasm_Simulator
  * aer_Simulator_density_matrix
  * aer_Simulator_statevector
  * aer_simulator_stabilizer New
  * aer_simulator_matrix_product_state
  * cirq_Simulator
  * cirq_clifford_simulator
  * nvidia_cudaq_stabilizer_simulator
  * quest_simulator
  * qsimcirq_simulator
  * qulacs_multicpu_simulator
  * cdac_photonics_simulator
  * qniverse_statevector_simulator

Listed here are the CPU options available for the **Param Utkarsh**

  * qasm_Simulator
  * aer_Simulator_density_matrix
  * aer_Simulator_statevector
  * aer_simulator_stabilizer New
  * aer_simulator_matrix_product_state
  * cirq_clifford_simulator
  * cirq_Simulator

## GPU

**Aer_StateVector_simulator_GPU:** Aer_StateVector_simulator_GPU is a feature within the Qiskit Aer framework that allows you to leverage the power of your GPU to perform state vector simulations of quantum circuits. State vector simulation involves calculating the complete quantum state of a system after a circuit is applied.

  * **Qiskit Aer:** Aer is a high-performance simulator for quantum circuits included in the Qiskit library. It provides various simulation methods, including state vector simulation.
  * **State vector Simulation:** This type of simulation calculates the entire state vector of a quantum circuit. The state vector holds the amplitudes (complex numbers representing probabilities) of finding the system in each possible basis state after applying the circuit.
  * **GPU Acceleration:** Aer_StateVector_simulator_GPU utilizes the NVIDIA cuStateVec library, which offers optimized kernels for state vector simulation on GPUs. This significantly speeds up simulations compared to CPU-based approaches, especially for larger circuits.
  * **Faster Simulations:** Running state vector simulations on GPUs can lead to significant speedups compared to CPU simulations, particularly for complex circuits with many qubits.
  * **Improved Scalability:** Leveraging GPUs allows you to handle larger quantum circuits that might be impractical to simulate on CPUs due to resource limitations.

**Nvidia_cudaq_statevector_simulator:**

The NVIDIA CUDA-Q Statevector Simulator is a high-performance tool that uses NVIDIA GPUs to accelerate simulations of quantum circuits. Its key features—such as GPU acceleration, scalability, precision, and seamless integration with the CUDA ecosystem—make it an invaluable resource for researchers and developers working on quantum computing applications.

**Key Features:**

**GPU Acceleration:** Leverages the parallel processing power of NVIDIA GPUs to significantly speed up quantum circuit simulations. This is crucial for handling larger circuits and more complex simulations that would be prohibitively slow on CPUs alone.  
**State Vector Representation:** Stores and manipulates the quantum state as a complex-valued vector. This allows for accurate simulation of quantum circuits and enables calculations of various properties of the quantum system.  
**Scalability:** Supports scaling simulations across multiple GPUs and even multiple nodes in a cluster. This enables researchers to tackle larger and more complex problems that exceed the memory capacity of a single GPU.  
**Precision:** Offers options for both single-precision (FP32) and double-precision (FP64) simulations. This allows users to choose the appropriate level of precision for their simulations, balancing accuracy with performance.  
**Integration with CUDA-Q:** Seamlessly integrates within the NVIDIA CUDA-Q framework. This allows users to leverage other CUDA-Q features like custom kernel definitions and integration with other CUDA libraries.  
**Efficient Memory Management:** Optimizes memory usage to minimize data transfer between CPU and GPU, further improving performance.

**qsimcirq_simulator_cuquantum_gpu_simulator:**

`qsimcirq` Can integrate with NVIDIA’s `cuQuantum` SDK to provide a GPU-accelerated simulator for quantum circuits.

Here’s a breakdown of what that means:

  * **`qsimcirq`** : This is a Python interface for `qsim`, Google Quantum AI’s high-performance quantum circuit simulator. It `qsim` is written in C++ and is optimized for classical hardware, leveraging techniques like gate fusion, vectorized instructions (AVX/FMA), and multithreading (OpenMP). It’s designed to be faster than the default Cirq simulator and can simulate a larger number of qubits (up to around 40 on powerful workstations).
  * **`cuQuantum`** : This is NVIDIA’s software development kit (SDK) designed to accelerate quantum circuit simulations on NVIDIA GPUs. It provides highly optimized GPU-accelerated libraries for quantum computing, including: 
    * **`cuStateVec`** For state-vector simulations.
    * **`cuTensorNet`** For tensor network-based simulations.

  * **Integration** : Google and NVIDIA have collaborated to integrate `qsim` with the `cuQuantum` SDK. This means that `qsimcirq` Users can leverage the power of NVIDIA GPUs to significantly speed up their quantum circuit simulations, especially for larger circuits.

**Aer_simulator_tensor_network_gpu**

**nvidia_cudaq_tensor_network_simulator**

**nvidia_cudaq_mps_simulator**

## FPGA Simulator and FPGA dm_simulator

The FPGA Simulator operates on an FPGA card, harnessing the parallel processing power of FPGAs to simulate quantum circuits. This simulator is designed for larger quantum circuits and provides hardware acceleration for faster quantum gate execution.

**FPGA dm_simulator**

The FPGA DM Simulator operates on an FPGA card and is specifically designed to simulate noisy quantum systems using a density matrix (DM) representation. This simulator models quantum noise and decoherence, making it ideal for simulating realistic quantum systems. Support till 12 qubits.

**Why Use Density Matrix?**

A density matrix is required when modeling:

  * Decoherence

  * Noise channels

  * Mixed states

  * Open quantum systems

  * Amplitude damping

  * Phase damping

  * Thermal noise

## Vector Card

The Vector Simulator runs on a vector card, which is optimized for high-throughput, parallel processing. It leverages vector-based computation to efficiently simulate quantum circuits by representing quantum states as vectors. This simulator is designed for classical simulation of quantum circuits, with a focus on speed for smaller-scale problems. Supports up to 27 qubits.

The csim_vector_simulator supports up to 32 Qubits.

## Select Quantum Hardware(QPU)

The user is presented with a range of options for the available Quantum Hardware, from which they can select. A user can only submit a job on QPU if he/she has an API key, which can be generated [here](https://quantum.ibm.com/ "api token") and then copied and pasted into the provided placeholder in the user’s profile section.

The following are the available QPU platforms:

  * QI Hardware
  * Rigetti Hardware
  * SuperStaq Hardware
  * IBM Hardware

**Superstaq Hardware**

The primary goal is to optimize the execution of quantum programs by tailoring them to the specific characteristics and native operations of various underlying quantum hardware platforms. This “device-physics-aware” compilation aims to extract maximum performance from current noisy intermediate-scale quantum (NISQ) devices.

Superstaq achieves this by:

  * **Deep optimization:** It compiles quantum programs to low levels of hardware control, going beyond typical abstract programming layers. This includes techniques like parametric (fractional) gates, dynamical decoupling, swap mirroring, and more.
  * **Hardware-agnostic approach:** While it optimizes for specific hardware, Superstaq is designed to be accessible from common quantum programming frameworks like **Qiskit (IBM)** and **Cirq (Google)**. This allows users to write programs in their preferred language and have Superstaq handle the hardware-specific optimizations.
  * Superstaq acts as an advanced compiler that bridges the gap between high-level quantum algorithms and the unique characteristics of different quantum computing hardware. By understanding the device physics and native gate sets, it can significantly improve the fidelity and performance of quantum programs running on various superconducting, trapped-ion, and neutral atom platforms
