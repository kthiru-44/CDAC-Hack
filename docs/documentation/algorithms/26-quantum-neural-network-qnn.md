---
title: "QNN Algorithm"
category: "Algorithms"
url: "https://qniverse.in/docs/qnn-algorithm/"
breadcrumb: "Home > Docs > Algorithms > QNN Algorithm"
---

# QNN Algorithm

> **Category:** Algorithms | **Source:** [https://qniverse.in/docs/qnn-algorithm/](https://qniverse.in/docs/qnn-algorithm/)


## Introduction to Quantum Neural Network

Quantum Neural Network (QNN) is a hybrid learning framework that integrates quantum circuit-based feature maps and variational layers with classical neural network components. At its core, QNN leverages parameterized quantum circuits to extract nonlinear transformations of input data, which are then processed by a classical head for prediction. The primary goal of QNN is to combine quantum-enhanced feature representations with proven classical optimization techniques to tackle both classification and regression tasks.

Presenting here with a video tour of how the Quantum Neural Networks(QNN) work in Qniverse:

[▶️ Video Demonstration: QPCA-Algo.mp4](https://qniverse.in/wp-content/uploads/2025/07/QPCA-Algo.mp4)

## How Quantum Neural Networks Differ from Classical Neural Networks

Classical neural networks rely exclusively on stacked layers of linear transformations and nonlinear activations to learn representations from data. In contrast, QNN introduces quantum subroutines—specifically, state preparation and variational circuits—that embed data into a high-dimensional Hilbert space and apply parameterized rotations and entangling gates. This quantum feature mapping can capture complex correlations with fewer trainable parameters, while the classical head ensures compatibility with existing loss functions, optimizers, and evaluation metrics.

## How Quantum Neural Networks Can Be Implemented

  1. Data Encoding and Preprocessing 
     1. Normalize each feature to [0, 2π] (or another suitable range) to match rotation-gate requirements.
     2. Split the dataset into training, validation, and test subsets.
     3. Choose an encoding scheme (e.g., angle encoding, amplitude encoding) based on qubit resources and data dimensionality.
  2. Quantum Circuit Architecture and Ansatz Selection 
     1. Decide on the number of qubits: one per feature or use embedding techniques to pack multiple features per qubit.
     2. Define the ansatz layers: typically alternating rotation gates (RX, RY) and entangling gates (CNOTs) arranged in a repeating block.
     3. Parameterize each gate with trainable weights θ.
  3. Forward Pass: State Preparation and Measurement 
     1. For each input sample, initialize the qubits to |0…0⟩ and apply the encoding circuit to map classical data into quantum amplitudes.
     2. Execute the ansatz circuit with current parameters θ.
     3. Measure one or more qubits in the Z-basis to obtain expectation values ⟨Z⟩, which serve as the network output.
  4. Loss Function Evaluation and Parameter Update Loop 
     1. Compute the loss (e.g., mean squared error for regression, cross-entropy for classification) between measured outputs and labels.
     2. Use a classical optimizer (e.g., gradient descent, Adam) to update θ. 
        1. Gradients can be estimated via the parameter-shift rule or finite differences.
     3. Optimization Loop Integration with Classical Optimizer 
        1. Integrate quantum circuit execution into a training loop: 
           1. Encode a batch of samples
           2. Run circuits in parallel (if backend supports batching)

  * Aggregate measurements and compute loss/gradients

  1. Update parameters θ
  2. Check for convergence or maximum epochs

  6. Iterative Training and Convergence Check 
     1. Track loss and accuracy on the validation set for each epoch.
     2. Implement early stopping or learning-rate scheduling to prevent overfitting.
     3. Once converged, freeze θ and evaluate on the test set for final performance metrics.

## Advantages and Disadvantages Compared to the Classical Counterpart

#### Advantages

  * Quantum Feature Mapping: Embeds data into a rich Hilbert space using parameterized rotations and entanglement, capturing nonlinear correlations that may be costly to approximate classically.
  * Hybrid Efficiency: Offloads complex feature extraction to shallow quantum circuits while retaining mature classical optimization and regularization techniques (dropout, schedulers, early stopping).
  * Parameter Savings: Quantum subroutines can achieve expressive transformations with fewer trainable parameters compared to deep classical architectures.
  * Hardware Acceleration: Supports GPU-accelerated quantum simulators (lightning.gpu), paving the way for future real-device execution.

#### Disadvantages

  * Hardware Constraints: Noisy and limited-qubit NISQ devices constrain practical scaling; many runs rely on simulators with classical overhead.
  * Circuit Overhead: State preparation and repeated QNode executions (shots) introduce latency compared to pure classical inference.
  * Debugging Complexity: Hybrid quantum-classical stacks require expertise in both domains, complicating error diagnosis and performance tuning.
  * Scalability Limits: Circuit depth and qubit count grow with feature dimensionality, potentially offsetting quantum advantages on large datasets.

## Real-World Applications

  * Small-Scale Classification: Binary or low-class multiclass tasks (e.g., medical diagnosis, financial fraud detection) on datasets where quantum feature maps add discriminative power.
  * Anomaly Detection: Identify subtle deviations by mapping inputs to entangled quantum states before thresholding via a classical head.
  * Quantum Chemistry Regression: Predict molecular properties (energies, dipoles) from quantum-inspired feature embeddings.
  * Time-Series Forecasting: Encode temporal windows into quantum circuits for enhanced pattern extraction in financial or sensor data.
  * Image Patch Classification: Classify small image regions (e.g., in microscopy) using amplitude-style feature encodings.

## Overview

The QuantumNeuralNetwork implementation is a modular hybrid framework combining PennyLane quantum circuits with a PyTorch classical head. It handles data preprocessing, quantum device selection, circuit construction, variational parameter management, training with early stopping, and full end-to-end evaluation. Users interact via fit(), predict(), evaluate(), and train(), with access to a rich training history.

#### Key Components and Features

  * QNNConfig: Dataclass to configure qubit count, layers, task type, device preferences, seeding, dropout, gradient clipping, early stopping, validation split, scaler choice, shots, and batch observations.
  * Device Selection: Automatically picks the best available quantum simulator device.
  * Improved Data Encoding: Normalizes features, applies multi-gate rotations, and entangles qubits for expressive encoding.
  * Variational Layers: Circular entanglement plus layered parameterized rotations (RY, RZ, RX) for deep feature transforms.
  * Hybrid Model: Dynamic classical head construction based on measured outputs; supports both classification (sigmoid) and regression (identity).
  * Training Utilities: Optimizers (AdamW), schedulers, loss functions, gradient clipping, early stopping, and comprehensive metric computation.
  * Evaluation Suite: Accuracy, precision, recall, F1, classification report, confusion matrix for classification; MSE, RMSE, MAE, R², explained variance for regression.
  * History Tracking: Per-epoch losses and metrics stored in training_history for visualization or further analysis.

## End-to-End Workflow

Initialization:  
Instantiate with optional QNNConfig or keyword overrides:

from QNN_Qniverse import QuantumNeuralNetwork, QNNConfig

config = QNNConfig(n_qubits=4, n_layers=2, task_type=’classification’)

qnn = QuantumNeuralNetwork(config)

Data Preprocessing:  
Call fit() or train() on your data source; the framework will split, scale, encode, and prepare tensors automatically.

Quantum Neural Network Process:

  * _select_device() → _setup_quantum_device()
  * _setup_quantum_circuit() to compile the QNode
  * _setup_model() to initialize quantum parameters and classical head

Training Routine:  
Inside fit(), the model is trained over epochs with optimizer, scheduler, loss, metric logging, and early stopping. The best model state is retained.

Evaluation and Output:

  * predict() returns class labels or continuous values.
  * evaluate() prints reports and returns metric dictionaries.
  * train() prints summaries, per-epoch tables, test-set reports, and returns a structured summary dict.

## Getting Started in Qniverse

Usage with Iris Dataset:

from QNN_Qniverse import QuantumNeuralNetwork

# Initialize QNN (auto infers qubits/layers)

qnn = QuantumNeuralNetwork()

# Train pipeline on Iris CSV

results = qnn.train(

data=’iris.csv’,

target_column=’species’,

test_size=0.2,

epochs=30,

learning_rate=0.01,

verbose=True

)

# Inspect returned summary

print(results)

**Understanding the Parameters**

  * n_qubits: Number of qubits in the quantum circuit (defaults to the number of features).
  * n_layers: Number of variational layers (default 3 if unspecified).
  * task_type: “classification” or “regression” (auto-inferred).
  * device_name: Quantum device identifier (“auto”, “lightning.gpu”, etc.).
  * random_seed: Seed for reproducibility.
  * dropout_rate: Dropout probability in the classical head.
  * gradient_clipping: Maximum norm for gradient clipping.
  * early_stopping_patience: Epochs to wait before early stop.
  * validation_split: Fraction of data for validation in fit().
  * use_robust_scaler: Whether to use RobustScaler vs. StandardScaler.
  * shots: Number of circuit executions for expectation estimation.
  * batch_obs: Enable batched measurements for speed.

**Hyperparameter Tuning**

  * n_layers & n_qubits: Balance expressivity vs. trainability; fewer layers/qubits often yield more stable convergence on NISQ devices.
  * learning_rate: Typical range 1e-3 to 1e-1; monitored via scheduler.
  * dropout_rate & gradient_clipping: Control overfitting and training stability.
  * early_stopping_patience & validation_split: Adjust to prevent over- or under-training.

**Evaluation Metrics and Plot History**

  * Classification: accuracy, precision, recall, F1-score, classification report, confusion matrix.
  * Regression: MSE, RMSE, MAE, R² score, explained variance.
  * Training History: Accessible via qnn.training_history and summarized with get_training_summary().

**Conclusion**

Quantum Neural Network provides a user-friendly interface for hybrid quantum-classical learning, encapsulating complex circuit design, parameter management, and training workflows behind simple method calls. By following this documentation, users can seamlessly integrate QNN into their machine learning pipelines, experiment with quantum feature mappings, and leverage classical optimization best practices for both classification and regression tasks.
