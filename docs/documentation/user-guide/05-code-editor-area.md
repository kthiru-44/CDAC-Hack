---
title: "Code Editor Area"
category: "User Guide"
url: "https://qniverse.in/docs/code-editor-area/"
breadcrumb: "Home > Docs > User Guide > Code Editor Area"
---

# Code Editor Area

> **Category:** User Guide | **Source:** [https://qniverse.in/docs/code-editor-area/](https://qniverse.in/docs/code-editor-area/)


As a unified platform, you can build your circuit or code once and execute it across multiple quantum frameworks such as QASM, Qiskit, CirQ, CudaQ. To support this, the platform offers three different language formats, making it easy to create quantum circuits and generate code in a variety of quantum programming languages. Any changes made to the circuit’s code are instantly reflected in the composer area. Additionally, you can create or modify circuits and custom gates directly in the composer by typing or editing code.

**Here is a quick video tour demonstrating how the code editor area interacts with the gates to construct a circuit from code.**

[▶️ Video Demonstration: code-editor-area-2-1.mp4](https://qniverse.in/wp-content/uploads/2024/12/code-editor-area-2-1.mp4)

## Features of the Code Editor

  * **Drag-and-Drop Interface:** Users can visually design quantum circuits by dragging and dropping elements onto the circuit composer area.
  * **Real-Time Code Generation:** The users design their circuits, and the editor automatically generates the corresponding code in QASM, Cirq, Qiskit, CudaQ, Qulacs, QuEst, and Editable Qiskit.
  * **Syntax Highlighting and Code Formatting:** The Editor provides advanced syntax highlighting for QASM, Cirq, and Qiskit, making the generated code easy to read and understand. The editor also supports code formatting, ensuring that the generated code is clean and well-structured.
  * **Error Detection and Debugging:** Built-in error detection helps users identify and correct mistakes in their circuit designs. The editor highlights errors and provides helpful messages, guiding users toward the correct implementation.
  * **Run Code:** Code can be run on various platforms (CPU, GPU, and QPU) available from the listed options in the Run Options settings, based on a user’s preference.
  * **Customization Options:** You can modify the generated code in the code editor, and the changes will be reflected in the circuit. **This feature is specifically offered by the QASM editor** , not by the other two Qiskit and Cirq editors.
  * **Qubit Initialization:** A user can initialize a qubit for State:∣ψ⟩ = α∣ 0⟩ + β ∣1⟩, by setting up with parameters for α and β**.**

## QASM

QASM, short for Quantum Assembly Language, is a low-level programming language designed to describe quantum circuits at a hardware-agnostic level. It is used primarily to define quantum operations and circuits in a format that quantum processors can understand and execute.

**Features**

  * **Hardware-Agnostic:** QASM provides a standard way to represent quantum circuits, making it compatible with different quantum hardware.
  * **Gate-Level Operations:** It focuses on the specification of quantum gates and their operations, similar to how assembly language operates at a low level for classical computers.
  * **Simple Syntax:** QASM’s syntax is straightforward, making it easy to understand and use for representing quantum circuits.

**Use Cases**

  * **Quantum Hardware Programming:** Used to program and control quantum processors.
  * **Intermediate Representation:** Acts as an intermediary between high-level quantum programming languages and hardware.

## Qiskit(Read-Only)

Qiskit is an open-source quantum computing software development framework created by IBM. It provides tools for creating and manipulating quantum programs and running them on quantum simulators and real quantum devices.

**Features**

  * **Comprehensive Library:** It offers a wide range of functions for quantum computing, including algorithms, circuits, and noise models.
  * **Modular Design:** Composed of several modules such as Terra (circuit creation), Aer (simulators), Ignis (error correction), and Aqua (algorithms).
  * **Integration with IBM Quantum Experience:** Allows users to run quantum circuits on IBM’s quantum computers and simulators.

**Use Cases**

  * **Quantum Algorithm Development:** Used for designing and implementing quantum algorithms.

## Cirq(Read-Only)

Cirq is an open-source quantum computing framework developed by Google. It is designed to facilitate the creation, simulation, and execution of quantum circuits, with a particular focus on Noisy Intermediate-Scale Quantum (NISQ) devices.

**Features**

  * **NISQ Device Focus:** Optimized for developing and running experiments on NISQ-era quantum devices.
  * **Flexible and Extensible:** It provides a flexible interface for creating and manipulating quantum circuits, making it easy to extend and customize.
  * **Integration with Google’s Quantum Processors:** Enables execution of quantum circuits on Google’s quantum hardware.

**Use Cases**

  * **Quantum Research:** Used extensively in academic and industrial research to develop and test new quantum algorithms.
  * **Algorithm Prototyping:** Ideal for prototyping and experimenting with quantum algorithms on simulators before deploying on actual hardware.
  * **Error Mitigation Research:** Facilitates research into error correction and mitigation techniques crucial for NISQ devices.

## CudaQ**(Read-Only)**
NVIDIA CUDA-Q is a platform designed to accelerate quantum computing by integrating it with classical computing resources, particularly GPUs. Here’s a concise overview:

  * **Hybrid Computing:**
    * CUDA-Q facilitates the development of hybrid quantum-classical applications, allowing seamless interaction between quantum processors (QPUs), GPUs, and CPUs.
  * **QPU Agnostic:**
    * It’s designed to be “qubit-agnostic,” meaning it can work with various QPU technologies and qubit types.
  * **GPU Acceleration:**
    * It leverages NVIDIA GPUs to significantly speed up quantum circuit simulations and classical portions of quantum algorithms.
  * **Software Development:**
    * Provides tools and libraries to streamline quantum software development, including compilers and runtime environments.
  * **Scalability:**
    * Aims to enable the development of scalable quantum applications that can utilize future quantum supercomputers.
  * **Ecosystem Integration:**
    * It is designed to be interoperable with existing AI and HPC workflows.
  * **Research advancement:**
    * It is used to advance the research of quantum computing across many scientific fields.

## QuEST (Quantum Exact Simulation Toolkit)

QuEst is an open-source high-performance quantum circuit simulator (not a full quantum programming language). It’s implemented as a C library that lets you build and execute simulations of quantum circuits (state-vectors, density matrices, noise, etc.) across CPUs, GPUs, and distributed systems.

**Language Support in QuEST**

**1\. Primary Interface: C (and C++)**

  * The main API is exposed in standard C.

  * You can link and call QuEST from C or C++ projects.

  * This is the only language directly supported at the API level.

**2\. Integration With Other Languages**

  * QuEST itself does not define a new quantum programming language (like Q# or OpenQASM).

  * To program with QuEST, you write classical host code in C/C++ that uses the QuEST API to set up qubits, gates, and simulations.

  * There’s no native Python, Rust, or higher-level language binding included by default (though users sometimes write wrappers themselves)

## Editable Qiskit

Editable Qiskit refers to the capability within the Qiskit framework to modify and customize quantum circuits and algorithms dynamically. This allows users to create, edit, and experiment with quantum circuits interactively.
