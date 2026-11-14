OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[3] c;

// Prepare 3-qubit GHZ state (|000> + |111>) / sqrt(2)
h q[0];

for i in [0:1] {
    cx q[i], q[i+1];
}

c = measure q;
