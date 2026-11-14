---
title: "Shor’s Algorithm"
category: "Algorithms"
url: "https://qniverse.in/docs/shors-algorithm-factorization/"
breadcrumb: "Home > Docs > Algorithms > Shor’s Algorithm"
---

# Shor’s Algorithm

> **Category:** Algorithms | **Source:** [https://qniverse.in/docs/shors-algorithm-factorization/](https://qniverse.in/docs/shors-algorithm-factorization/)


## What is Shor’s Algorithm??

Shor’s algorithm is a quantum algorithm that can be used to factor integers. It efficiently factors large semi prime numbers into their prime factors, a task that is believed to be classically hard and forms the basis of modern cryptographic schemes like RSA. Shor’s algorithm demonstrates the quantum computer’s potential to break classical cryptographic protocols.

The algorithm is a quantum algorithm, which means that it relies on quantum entanglement to perform its calculations.

In Shor’s algorithm, the key steps are:

1\. Generate a random number.

2\. Factor the number.

3\. Compute the factors. The overall complexity of Shor’s algorithm is the Order of Polynomial in log N, where N is the number to be factored.

## How does Shor’s Algorithm help in factorization?

Shor’s algorithm tackles factoring large integers by exploiting the strangeness of quantum mechanics, specifically the concept of periodicity. Here’s how it helps with factorization:

**1\. Periodicity and Order:**

Shor’s algorithm relies on the connection between the periodicity of a mathematical function and the order of an element in a group. Let’s break this down:

  * **Periodicity:** A function f(x) is periodic with period p if f(x + p) = f(x) for all values of x. In simpler terms, the function repeats itself every ‘p’ input value.
  * **Order of an Element (a):** In a group (a set with a specific operation), the order of an element ‘a’ is the smallest positive integer ‘o’ such that a^o = the identity element (e.g., 1 in multiplication).

**2\. Shor’s Function and Order:**

Shor’s algorithm defines a function f(x) based on the integer you want to factor (N). This function uses modular arithmetic (denoted by %). Here’s the basic structure:
    
    
    ```python
    f(x) = a^x (mod N)
    ```

where ‘a’ is a random integer co-prime to N (meaning they share no common factors other than 1). The crucial part is that the order of ‘a’ modulo N (denoted as ord_a(N)) is related to the factors of N.

**3\. Quantum Period Finding:**

Here’s where the quantum magic comes in. Shor’s algorithm uses a quantum circuit to find the period (p) of the function f(x). This involves putting a superposition of possible input values (x) and manipulating the output using the function ‘f(x)’. By exploiting quantum properties like entanglement, the algorithm can efficiently determine the period.

**4\. Order and Factorization:**

Once the period (p) is found, Shor’s algorithm uses a mathematical technique (usually the Euclidean algorithm) to determine the order (ord_a(N)) of the element ‘a’ modulo N. Here’s the key connection:

  * If ord_a(N) is even (say 2k), then it can be shown that N has at least one factor that is greater than 1 and less than N. This factor can be obtained using the greatest common divisor GCD(a^k -1, N) or GCD(a^k +1, N).

**Showing a video example for the number 42 and the corresponding circuit generated in editable Qiskit.**

[▶️ Video Demonstration: https://qniverse.in/wp-content/uploads/2024/05/Shors-Algo.mp4?_=1](https://qniverse.in/wp-content/uploads/2024/05/Shors-Algo.mp4?_=1)

## How is Shor’s Algorithm achieved?

**1\. Oracle Function (f):**

Shor’s algorithm utilizes a function **`f(a)` **that takes an integer `**a**` (coprime to the target number `N` being factored) as input and outputs the remainder when **`a`** is raised to a certain unknown power (`b`) modulo `N`:

**`f(b) = a^b (mod N)  
`**

This function serves as a “black box” for the quantum circuit. There is no need to know the exact value of **`b`** , but it has a special relationship with the prime factors of `N`.

**2\. Quantum Fourier Transform (QFT):**

Shor’s algorithm leverages the Quantum Fourier Transform (QFT) to analyze the output of the oracle function. The QFT takes a superposition of states and distributes the amplitudes across the basis states. In this case, the QFT operates on a register of qubits used to represent the possible values of `a`.

**3\. Period Finding (Expressions get more involved here):**

A key step in Shor’s algorithm is finding the period of the function **`f(x)`**. This period refers to the smallest value `p` such that:

**`a^(p+t)= a^t (mod N) // for all integers t  
`**

In simpler terms, the function repeats its output values after a specific number of iterations (`p`). Finding this period is crucial for factoring `N`.

While the exact expressions for period finding involve concepts like modular arithmetic and continued fractions, here’s a simplified representation:

**`a^p=a^(bp) (mod N) = 1 (mod N) // where b is any natural number since the period repeats the output of 1  
`**

This expresses the condition for finding the period **`p`.**

**4\. Continued Fraction Method (Optional):**

Shor’s algorithm often uses the continued fraction method to efficiently find the period from the oracle function’s outputs. This method involves expressing the fraction `b/q` (where `b` is the unknown power and `q` is related to `N`) as a sequence of quotients. The period `p` can then be extracted from the continued fraction representation.

**5\. Factoring`N`:**

Once the period **`p` **is found, Shor’s algorithm uses mathematical properties (Euclid’s algorithm) to efficiently determine the greatest common divisor (GCD) between GCD(a^(p/2) -1, N) or GCD(a^(p/2) +1, N) With a high probability, this GCD will be one of the prime factors of `N`.

**Overall Complexity:**

Shor’s algorithm offers a significant speedup compared to classical factoring algorithms, especially for large integers. The number of qubits needed scales polynomially with the number of digits in **`N`** , making it a promising approach for future quantum computers.

It can efficiently factor large numbers exponentially faster than the best-known classical algorithms. This means that, in theory, it could break commonly used encryption schemes in a fraction of the time it would take classical computers.

## Application of Shor’s Algorithm??

  * **Quantum Advantage** : Shor’s Algorithm exploits the inherent parallelism and superposition properties of quantum computing to perform calculations much faster than classical computers. Specifically, it utilizes quantum Fourier transform and modular exponentiation to find the period of a function, which is then used to extract the factors of the number being factored.

  * **Impact** : If large-scale, fault-tolerant quantum computers become a reality, Shor’s Algorithm would pose a significant threat to current encryption standards. This has spurred research into post-quantum cryptography, which aims to develop encryption methods resistant to quantum attacks.

  * **Current Status** : While Shor’s Algorithm has been demonstrated on small-scale quantum computers to factorize small numbers, scaling it up to factor large numbers remains a considerable challenge due to the requirements of quantum error correction and the complexity of quantum hardware.
