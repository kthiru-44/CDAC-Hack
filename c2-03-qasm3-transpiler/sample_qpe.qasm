OPENQASM 3.0;
include "stdgates.inc";

// Quantum Phase Estimation slice (2 counting qubits + 1 eigenstate qubit)
qubit[3] q;
bit[2] c;

// Prepare eigenstate |1> on q[2]
x q[2];

// Superposition on counting register
h q[0];
h q[1];

// Controlled phase rotations
cp(pi / 2) q[0], q[2];
cp(pi) q[1], q[2];

// Inverse QFT on counting qubits
h q[1];
cp(-pi / 2) q[0], q[1];
h q[0];

c[0] = measure q[0];
c[1] = measure q[1];
