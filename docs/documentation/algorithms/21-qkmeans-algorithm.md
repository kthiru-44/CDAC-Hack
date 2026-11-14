---
title: "QKMeans Algorithm"
category: "Algorithms"
url: "https://qniverse.in/docs/qkmeans-algorithm/"
breadcrumb: "Home > Docs > Algorithms > QKMeans Algorithm"
---

# QKMeans Algorithm

> **Category:** Algorithms | **Source:** [https://qniverse.in/docs/qkmeans-algorithm/](https://qniverse.in/docs/qkmeans-algorithm/)


## Introduction to QKMeans

Quantum KMeans (QKMeans) is a hybrid clustering algorithm that leverages quantum computing concepts alongside traditional clustering methods. At its core, QKMeans utilizes quantum circuits to compute similarity measures between data points and centroids, which serves as an alternative means for distance evaluation compared to classical Euclidean metrics. The primary goal of QKMeans is to exploit potential quantum speed-ups and enhanced feature mapping through quantum state representations while still incorporating well-known classical techniques for cluster updating, convergence checking, and evaluation.

**Presenting here with a short video tour of how the QKMean Algorithm is implemented and runs in Qniverse**

[▶️ Video Demonstration: https://qniverse.in/wp-content/uploads/2025/05/QkMean-algo-2.mp4?_=1](https://qniverse.in/wp-content/uploads/2025/05/QkMean-algo-2.mp4?_=1)

## How Quantum KMeans Differs from Classical KMeans

While the classical KMeans algorithm calculates Euclidean distances directly between data points and centroids, QKMeans uses a quantum subroutine known as the swap test to estimate the inner product between quantum states derived from data vectors. This quantum-enabled distance is then merged with classical formulas to form the effective distance metric. The algorithm further implements mechanisms such as parallel processing and caching to increase efficiency.

## How Quantum KMeans Can Be Implemented?

Quantum KMeans is a hybrid clustering algorithm that incorporates quantum computing principles into the classic KMeans framework to enhance similarity measurement. Implementing Quantum KMeans involves several key stages, combining classical preprocessing, quantum circuit design, and iterative optimization.

  1. **Data Normalization and Preparation**

The first step is to prepare the input data. Each data point, typically represented as a real-valued vector, must be **normalized** so it can be encoded into a valid quantum state. Normalization ensures that the vector lies on the unit sphere, which is a requirement for proper quantum state preparation.

  2. **Quantum State Encoding**

Once the data is normalized, each vector is encoded into a quantum state. One of the most common approaches is angle encoding or amplitude encoding, where the features of a data vector are translated into rotation angles of quantum gates (such as Rot or RY gates). Each feature is applied to a separate qubit or register of qubits, resulting in a quantum state that represents the data.

  3. **Distance Computation Using the Swap Test**

To compare how similar two quantum states are (e.g., a data point and a cluster centroid), a quantum subroutine called the **swap test** is used. This circuit estimates the squared inner product between two quantum states.

  * The circuit uses an ancilla qubit and two registers containing the encoded states.
  * A Hadamard gate is applied to the ancilla, followed by controlled-SWAP (CSWAP) gates between the corresponding qubits of the two states.
  * Another Hadamard gate is applied to the ancilla, which is then measured.
  * The probability of measuring the ancilla in the |0⟩ state gives an estimate of the inner product between the two vectors.

The **quantum-enhanced distance** between the two vectors can then be computed using this inner product along with their classical norms, typically by applying the cosine law:

This replaces the traditional Euclidean distance in the KMeans algorithm.

  4. **Cluster Assignment**

For each data point, calculate its quantum-enhanced distance to all current cluster centroids using the above method. Assign the point to the cluster with the minimum distance.

This step can be parallelized, especially for large datasets, since distance computations between data points and centroids are independent of one another.

  5. **Centroid Update**

After all data points are assigned to their nearest clusters, update the cluster centroids. This can be done using the classical mean of all vectors in each cluster. If you’re using mini-batch KMeans, you update centroids incrementally using a learning rate.

This update does not need to be quantum, and is performed purely in the classical domain.

  6. **Iteration and Convergence**

Repeat the assignment and update steps iteratively until:

  * The centroids do not change significantly between iterations (within a tolerance), or
  * A maximum number of iterations is reached.

During each iteration, you may also record clustering history for visualization (e.g., cluster composition and centroid movement).

  7. **Evaluation**

Once convergence is achieved, evaluate the clustering performance using internal clustering metrics such as:

  * **Silhouette Score**
  * **Davies–Bouldin Index**
  * **Calinski–Harabasz Index**

If ground truth labels are available, compute external metrics like:

  * **Adjusted Rand Index (ARI)**
  * **Normalized Mutual Information (NMI)**

  8. **Hyperparameter Tuning (Optional)**

To find the best number of clusters k, Quantum KMeans can be extended with:

  * **Cross-validation** : Run multiple trials with different k values and select the one that maximizes average Silhouette Score.
  * **Elbow Method** : Plot cluster inertia (sum of squared distances) vs. k and find the point where improvement plateaus (the “elbow”).

## Advantages and Disadvantages Compared to the Classical Counterpart

**Advantages**

  1. **Quantum State Mapping:**
     * The use of quantum state preparation—via techniques such as amplitude embedding and angle embedding—enables the encoding of classical data into a high-dimensional Hilbert space. This mapping can capture more complex feature representations and subtle data correlations that might be overlooked by classical methods. (See: _q‑means: A Quantum Algorithm for Unsupervised Machine Learning_ , by Iordanis Kerenidis, Jonas Landman, Alessandro Luongo, and Anupam Prakash, arXiv:1812.03584, December 10, 2018.; also _Do you know what q‑means?_ , by João F. Doriguello, Alessandro Luongo, and Ewin Tang, arXiv:2308.09701, August 18, 2023.).

  1. **Hybrid Approach:**
     * Quantum k‑means algorithms combine quantum subroutines (for similarity and distance evaluation using methods such as the swap test) with robust classical updating and convergence techniques. This hybrid framework leverages quantum parallelism to expedite the computationally intensive parts (notably distance estimation) while preserving the reliability of classical iterative updates. This approach is demonstrated in recent hybrid quantum clustering studies. (See: _Quantum Clustering with k‑Means: a Hybrid Approach_ , by Alessandro Poggiali, Alessandro Berti, Anna Bernasconi, Gianna M. Del Corso, and Riccardo Guidotti, arXiv:2212.06691, December 13, 2022.).

  1. **Parallelism and Efficiency:**
     * By exploiting quantum parallelism, quantum algorithms can evaluate multiple distances simultaneously. Theoretical analyses show that some quantum variants achieve a running time with only polylogarithmic dependence on the number of data points NN (in contrast to the O(kdN)O(kdN) per-iteration complexity of classical k‑means). These efficiency gains are especially significant for very large datasets. (See: _q‑means: A Quantum Algorithm for Unsupervised Machine Learning_ and related follow-up work by Ragesh Jaiswal, _A Quantum Approximation Scheme for k‑Means_ , arXiv:2308.08167, August 16, 2023.).

  1. **Potential for Quantum Advantage:**
     * As quantum hardware improves—with increased qubit counts and lower noise—the quantum components of these clustering algorithms could yield significant speedups for very high-dimensional or large-scale datasets. The potential for exponential or super-polynomial improvements, particularly in distance computations, is very promising. (See: the full complexity analysis provided in _q‑means: A Quantum Algorithm for Unsupervised Machine Learning_ and _Do you know what q‑means?_).

**Disadvantages**

  1. **Hardware Limitations:**
     * Currently available quantum devices (as well as simulators) are limited by a small number of qubits and high error rates within the NISQ (Noisy Intermediate-Scale Quantum) regime. In many instances, the algorithms run in simulation rather than on real hardware, which can negate or reduce the practical quantum advantage. (This point is underlined in _q‑means: A Quantum Algorithm for Unsupervised Machine Learning_).
  2. **Overhead from Quantum Routines:**
     * Quantum circuit execution entails significant overhead—stemming from state preparation, gate operations, and the requirement for multiple circuit repetitions (shots) to collect statistically significant measurements. Although quantum techniques (like swap-test distance estimation) promise asymptotic speedups, their current overhead may slow down the algorithm on moderately sized or well-structured datasets. (Discussed in _Quantum Clustering with k‑Means: a Hybrid Approach_
  3. **Complexity and Debugging:**
     * The hybrid nature of quantum-classical algorithms adds additional layers of complexity to debugging and performance tuning. The interaction between probabilistic quantum subroutines (which are sensitive to noise) and the deterministic classical optimization process introduces further challenges in both development and error handling. (This challenge is detailed in multiple studies, including _q‑means: A Quantum Algorithm for Unsupervised Machine Learning_).
  4. **Scalability Concerns:**
     * Although theoretical models suggest that quantum k‑means scales polylogarithmically with the number of data points NN, the resource requirements (such as circuit depth and qubit overhead) increase with the dimensionality of data. Present quantum hardware may struggle with very high-dimensional data, potentially limiting the practical benefits of quantum clustering approaches in the near term. (Explained in _A Quantum Approximation Scheme for k‑Means_ , by Ragesh Jaiswal, arXiv:2308.08167, August 16, 2023).

## Real-World Applications

Quantum KMeans, while still an area of active research, holds promise in several application domains where classical clustering might benefit from the unique properties of quantum computation:

  1. **High-Dimensional Data Analysis** : 
     * In fields such as genomics, image recognition, and finance, data sets can be extremely high-dimensional. QKMeans may offer new ways to capture intrinsic structure through quantum state mapping.
  2. **Anomaly Detection** : 
     * Clustering techniques are often used for anomaly detection in cybersecurity or fraud detection. The enhanced similarity evaluation of QKMeans might yield improved performance in spotting subtle anomalies.
  3. **Quantum Machine Learning Integration** : 
     * As part of broader hybrid quantum-classical machine learning systems, QKMeans can serve as a pre-processing or feature extraction method feeding into other quantum or classical learning algorithms.
  4. **Optimization Problems** : 
     * Clustering is a key step in many optimization tasks, such as supply chain segmentation or customer segmentation in marketing. The potential for quantum acceleration could be particularly beneficial in time-critical applications.
  5. **Scientific Data Clustering** : 
     * Research fields that handle complex and multi-dimensional experimental data (e.g., particle physics, astronomy) could leverage QKMeans to detect patterns not easily identified by classical methods.

## Overview

The QuantumKMeans implementation is a hybrid clustering algorithm that integrates quantum computing techniques with classical clustering methods. Its primary aim is to enhance the standard k-means algorithm by employing a quantum swap test to calculate the distance between data points and centroids. This quantum approach is used to determine an “overlap” measure between the quantum state representations of classical data vectors, which is then incorporated into the distance metric.

## Key Components and Features

  * **Quantum-Enhanced Distance Calculation:**
    * Implements a **swap test** quantum circuit to estimate the similarity (inner product squared) between the quantum states representing a data point and a centroid.
    * Uses the measured overlap along with the Euclidean norms of the vectors to compute a quantum-inspired distance.
  * **Quantum State Preparation:**
    * Converts classical feature vectors into normalized quantum states.
    * Applies rotation gates on quantum registers to encode the feature values.
  * **Centroid Initialization and Updates:**
    * Randomly initializes centroids from the input dataset.
    * Iteratively assigns data points to the closest centroids based on the quantum-enhanced distance.
    * Updates centroids by computing the mean of points in each cluster, with support for both full-batch and mini-batch processing.
  * **Parallel Processing:**
    * The algorithm leverages multi-threading via Python’s ThreadPoolExecutor to concurrently assign data points to clusters, thereby improving computation speed on larger datasets.
  * **GPU Support:**
    * Optionally uses GPU acceleration through PennyLane’s lightning.gpu device to speed up quantum circuit simulations.
    * Includes a verification step to ensure that GPU support is available, otherwise falls back to a CPU-based backend.
  * **Hyperparameter Tuning:**
    * Provides two methods for selecting the best number of clusters (k): 
      * **Cross-Validation:** Evaluates a range of k values by maximizing the silhouette score.
      * **Elbow Method:** Uses inertia (sum of squared distances) to determine the optimal k by detecting an “elbow” point in the reduction of inertia.
  * **Evaluation and Visualization:**
    * Computes various internal evaluation metrics, such as the Silhouette Score, Davies–Bouldin Index, and Calinski–Harabasz Index.
    * If target labels are provided, external evaluation metrics (Adjusted Rand Index and Normalized Mutual Information) are also computed.
    * Maintains a plot history that captures the clustering process at each iteration, optionally reducing the data to two dimensions using PCA for visualization purposes.
  * **Data Handling and Integration:**
    * Includes functionality to load data from CSV files, allowing for easy integration with common datasets.
    * Features parameters for selecting which columns represent features and target labels, ensuring versatility when working with different datasets.

## End-to-End Workflow

  1. **Initialization:**  
The QuantumKMeans class is instantiated, where it configures the quantum simulator (GPU or CPU) and initializes essential variables and caches.
  2. **Data Preprocessing:**  
The input data is loaded and preprocessed. This involves normalizing the feature vectors and, if needed, separating the target labels.
  3. **Quantum Clustering Process:**
     * **State Preparation:** Converts classical vectors to quantum states.
     * **Swap Test:** Evaluates the similarity between data points and centroids using the quantum swap test.
     * **Cluster Assignment:** Data points are allocated to clusters based on computed distances (parallelized if enabled).
     * **Centroid Update:** New centroids are computed based on the mean of assigned points until convergence or the maximum number of iterations is reached.
  4. **Hyperparameter Tuning:**  
Optionally, the algorithm can refine the cluster number by testing a range of k values using cross-validation or the elbow method.
  5. **Evaluation and Output:**  
After clustering, the algorithm computes evaluation metrics and generates a plot history for each iteration. It then outputs the final cluster assignments, centroids, and evaluation scores.

****

## Getting Started in Qniverse

**Useage with Iris Dataset**

**Below is a full example with the provided Iris dataset:**

from qniverse.algorithms import QuantumKMeans

**# Initialize QuantumKMeans**

qkmeans = QuantumKMeans()

**# Train the model using the integrated training pipeline**

results = qkmeans.train_model(

csv_path=’iris.csv’,

k=3, # Number of clusters (this may be overridden by the k-selection method)

feature_columns=None, # All features are used for clustering

label_column=”variety”, # Target column used for evaluation

shots=1024,

test_size=0.2,

k_selection_method=”elbow”, # Alternatively, use “cv” for cross-validation

candidate_k_start=2,

candidate_k_end=8

)

**# The results dictionary now contains cluster assignments, centroids, and the plot history.**

print(results)

## Understanding the Parameters

**Clustering Settings**

  * **k****:**  
Sets the number of clusters. You can start with an estimated value. When using hyperparameter tuning methods (elbow or cross validation), this value may be adjusted automatically.
  * **max_iters****:**  
This is the maximum number of iterations the clustering algorithm will run. It is set to 100 by default, which generally works well for convergence.
  * **shots****:**  
Refers to the number of quantum simulation executions to obtain robust measurements from the quantum circuit. A higher number provides more precise measurements at the cost of increased computation time.
  * **mini_batch_size****:**  
For larger datasets, mini-batch clustering processes a subset of data at each iteration, speeding up each clustering step.
  * **parallel****:**  
Enabling parallel processing helps when clustering a large number of points by distributing computations over multiple threads.

**Hyperparameter Tuning Options**

  * **k_selection_method****:**  
Choose between: 
    * “elbow”: Uses the inertia (sum of squared distances) reduction to choose the optimal number of clusters.
    * “cv”: Uses cross-validation with the silhouette score for selecting the best value of k.
  * **candidate_k_start****and****candidate_k_end****:**  
Define the range for candidate k values when tuning.

**Data Handling Settings**

  * **csv_path****:**  
The file path to your dataset in CSV format.
  * **feature_columns****and****label_column****:**  
Specify which columns in the CSV file should be used as features and which as target labels. This allows you to separate the data needed for clustering from the data used for evaluation.

**Hyperparameter Tuning**

When you are uncertain about the best number of clusters:

  * **Elbow Method:**  
The algorithm computes the inertia for different values of k. If the decrease in inertia (i.e., the improvement in cluster compactness) falls below a set threshold, the algorithm selects the optimal k from the previous value.
  * **Cross-Validation:**  
The silhouette score is averaged over several runs for candidate values of k, and the k with the highest score is chosen.

Both methods can be invoked through the train_model interface by setting k_selection_method to “elbow” or “cv” respectively.

**Evaluation Metrics and Plot History**

After running the clustering algorithm:

  * **Internal Evaluation:**
    * **Silhouette Score**
    * **Davies–Bouldin Index**
    * **Calinski–Harabasz Index**
  * **External Evaluation (if target labels are provided):**
    * **Adjusted Rand Index (ARI)**
    * **Normalized Mutual Information (NMI)**

These metrics are printed to the console and returned in the output dictionary.

  * **Plot History:**  
A record of the clustering process through iterations is maintained. Each entry in the plot history contains the cluster assignments, centroids, and (if available) the true labels (transformed to 2D with PCA if necessary). This is useful for visualizing how clusters evolve over iterations.

**Conclusion**

QuantumKMeans is a powerful tool for those interested in exploring quantum-enhanced clustering techniques. With support for GPU acceleration, mini-batch processing, and hyperparameter tuning, it offers both flexibility and performance for various data clustering tasks. By following this documentation, users can seamlessly integrate the algorithm into their workflow, experiment with different settings, and evaluate the clustering performance on their own datasets.
