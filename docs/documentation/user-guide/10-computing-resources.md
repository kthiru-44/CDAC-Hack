---
title: "Compute Resources"
category: "User Guide"
url: "https://qniverse.in/docs/computing-resources/"
breadcrumb: "Home > Docs > User Guide > Compute Resources"
---

# Compute Resources

> **Category:** User Guide | **Source:** [https://qniverse.in/docs/computing-resources/](https://qniverse.in/docs/computing-resources/)


Compute resources encompass various types of hardware that perform computational tasks, including CPUs, GPUs, vector processors/cards, and QPUs. Each resource has unique characteristics and is suited to different types of computations and calculations.

**Also presented here is a brief video tour showing how to access a detailed section for resources being used in the Qniverse application for job simulations and results.**

[▶️ Video Demonstration: https://qniverse.in/wp-content/uploads/2025/04/compute-resources_new-.mp4?_=1](https://qniverse.in/wp-content/uploads/2025/04/compute-resources_new-.mp4?_=1)

## Central Processing Unit****
**Function** : The primary processor in a computer is responsible for executing general-purpose instructions and managing system operations.

**Architecture** : Composed of a few cores optimized for single-threaded performance and executing a wide range of instructions.

**Use Cases** : General computing tasks, including running operating systems and applications, and managing input/output operations.

**Performance** : Typically measured in GHz, number of cores, and instructions per clock (IPC).

## Graphics Processing Unit

**Function** : Specialized processor designed to accelerate graphics rendering and parallel processing tasks.

**Architecture** : Contains thousands of smaller, efficient cores optimized for handling multiple tasks simultaneously.

**Use Cases** : Graphics rendering, video processing, machine learning, scientific simulations, and other parallelizable tasks.

**Performance** : Measured in teraflops (TFLOPS) for floating-point operations and the number of CUDA cores (for NVIDIA GPUs) or stream processors (for AMD GPUs).

The Aer_cuStateVector is a state vector simulator backend provided by IBM’s Qiskit Aer library. It is optimized to run on NVIDIA GPUs using cuStateVec, part of NVIDIA’s cuQuantum library. This backend harnesses the massive parallelism and computational power of GPUs to simulate quantum circuits much faster than traditional CPU-based simulators.

**Advantages:**

Speed: Dramatically faster simulation times for large quantum circuits due to the parallel processing capabilities of GPUs.

Scalability: It can handle larger quantum circuits and higher qubit counts that are infeasible with CPU-only simulators.

Efficiency: Optimized use of GPU resources ensures efficient computation and resource utilization.

**Key Features:**

**GPU Acceleration:** Leverages the parallel processing power of NVIDIA GPUs to significantly speed up quantum circuit simulations. This is crucial for handling larger circuits and more complex simulations that would be prohibitively slow on CPUs alone.  
**State Vector Representation:** Stores and manipulates the quantum state as a complex-valued vector. This allows for accurate simulation of quantum circuits and enables calculations of various properties of the quantum system.  
**Scalability:** Supports scaling simulations across multiple GPUs and even multiple nodes in a cluster. This enables researchers to tackle larger and more complex problems that exceed the memory capacity of a single GPU.  
**Precision:** Offers options for both single-precision (FP32) and double-precision (FP64) simulations. This allows users to choose the appropriate level of precision for their simulations, balancing accuracy with performance.  
**Integration with CUDA-Q:** Seamlessly integrates within the NVIDIA CUDA-Q framework. This allows users to leverage other CUDA-Q features like custom kernel definitions and integration with other CUDA libraries.  
**Efficient Memory Management:** Optimizes memory usage to minimize data transfer between CPU and GPU, further improving performance.

**Benefits:**

**Faster Simulations:** Enables significantly faster simulation of quantum circuits compared to CPU-based implementations.  
**Scalability:** Enables simulations of larger and more complex quantum systems.  
**Improved Accuracy:** Supports double-precision simulations for applications requiring greater accuracy.  
**Integration with****the CUDA Ecosystem:** Enables seamless integration with other CUDA libraries and tools, enabling the development of more sophisticated quantum-classical hybrid applications.

## Vector Processors/Cards

**Function** : Processors designed to perform the same operation on multiple data points simultaneously, known as Single Instruction, Multiple Data (SIMD).

**Architecture** : Features vector registers and functional units that can perform operations on entire vectors in one instruction cycle.

**Use Cases** : High-performance computing (HPC) tasks, scientific computations, data analysis, and real-time signal processing.

**Performance** : Evaluated based on the width of vector units (e.g., 128-bit, 256-bit, 512-bit) and the ability to handle large vectors efficiently.

## Quantum Processing Unit

**Function** : Specialized processor that performs computations based on the principles of quantum mechanics.

**Architecture** : Utilizes qubits instead of bits, leveraging superposition, entanglement, and quantum gates to perform calculations.

**Use Cases** : Solving complex optimization problems, cryptography, drug discovery, material science, and other problems that benefit from quantum parallelism.

**Performance** : Measured in terms of the number of qubits, coherence time, gate fidelity, and quantum volume.

## Comparative Overview

**CPUs** : Versatile and good for general-purpose computing, but limited in parallel processing capabilities compared to GPUs.

**GPUs** : Excel at parallel processing, making them ideal for tasks that can be divided into smaller, concurrent operations.

**Vector Processors** : Optimize specific computations by processing multiple data points simultaneously, bridging the gap between general-purpose CPUs and highly parallel GPUs.

**QPUs** : Still in the experimental stage for most practical applications, but offer the potential for exponential speedups in specific computational problems.

## Integration in Computing

Modern computing systems often integrate multiple types of computing resources to leverage their respective strengths:

**Hybrid Systems** : Combining CPUs and GPUs in a single system for tasks like machine learning, where the CPU handles general control and logic while the GPU accelerates data processing.

**High-Performance Computing (HPC)** : Utilizing vector processors and GPUs in supercomputers to achieve massive parallelism for scientific simulations and data analysis.

**Quantum-Classical Hybrid Computing** : Using QPUs in conjunction with classical CPUs/GPUs to solve parts of a problem more efficiently than either could alone, particularly in research and experimental setups.

## Available Backend systems on Qniverse

**Simulators on CPUs on both QACC-cluster and Param Utkarsh HPCs :**

**QACC-Cluster:**

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

**Param Utkarsh**

  * qasm_Simulator
  * aer_Simulator_density_matrix
  * aer_Simulator_statevector
  * aer_simulator_stabilizer New
  * aer_simulator_matrix_product_state
  * cirq_clifford_simulator
  * cirq_Simulator

**Simulators on GPUs on both QACC_cluster and Param Utkarsh HPCs :**

  * aer_simulator_statevector_gpu
  * nvidia_cudaq_statevector
  * qsimcirq_cuquantum_gpu_simulator
  * Aer_simulator_tensor_network_gpu
  * nvidia_cudaq_tensor_network_simulator
  * nvidia_cudaq_mps_simulator

**FPGA Processors/Cards:**

  * fpga_simulator
  * fpga_dm_simulator

**Vector Cards:**

  * vector_simulator
  * csim_vector_simulator

**QPUs:**

  * Quantum Inspire(QI) Hardware
  * Superstaq Hardware
  * Rigetti Hardware
  * IBM Hardware

**HPC(High Performance Computers):**

Param Utkarsh

QACC Cluster

``
