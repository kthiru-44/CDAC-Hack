"""Valid and invalid OpenQASM programs shared by the C2-03 tests (same set as tools/c2_probe.py)."""

H = 'OPENQASM 3.0;\ninclude "stdgates.inc";\n'

PROGRAMS = {
    'basic': H + 'qubit[3] q; bit[3] c; h q[0]; cx q[0],q[1]; rx(pi/3) q[2]; ccx q[0],q[1],q[2]; c = measure q;',
    'allstd': H + 'qubit[3] q; p(0.3) q[0]; x q[0]; y q[1]; z q[2]; h q[0]; s q[1]; sdg q[2]; t q[0]; tdg q[1]; sx q[2]; rx(0.1) q[0]; ry(0.2) q[1]; rz(0.3) q[2]; cx q[0],q[1]; cy q[1],q[2]; cz q[0],q[2]; cp(0.4) q[0],q[1]; crx(0.5) q[1],q[2]; cry(0.6) q[0],q[2]; crz(0.7) q[0],q[1]; ch q[1],q[2]; swap q[0],q[2]; ccx q[0],q[1],q[2]; cswap q[0],q[1],q[2]; cu(0.1,0.2,0.3,0.4) q[0],q[1]; phase(0.2) q[1]; cphase(0.3) q[0],q[2]; id q[0]; u1(0.3) q[0]; u2(0.1,0.2) q[1]; u3(0.1,0.2,0.3) q[2]; U(0.3,0.2,0.1) q[0]; cs q[0],q[1]; csdg q[1],q[2]; ct q[0],q[2]; ctdg q[0],q[1]; cu1(0.2) q[1],q[2]; cu2(0.1,0.2) q[0],q[1]; cu3(0.1,0.2,0.3) q[1],q[0]; sxdg q[1];',
    'barrier': H + 'qubit[2] q; bit[2] c; h q[0]; barrier q; cx q[0],q[1]; barrier q[0]; c[0] = measure q[0]; c[1] = measure q[1];',
    'single': H + 'qubit q; bit c; h q; c = measure q;',
    'cond_bit': H + 'qubit[2] q; bit[2] c; h q[0]; c[0] = measure q[0]; if (c[0] == 1) { x q[1]; } c[1] = measure q[1];',
    'cond_reg': H + 'qubit[2] q; bit[1] c; bit[1] d; h q[0]; c[0] = measure q[0]; if (c == 1) x q[1]; d[0] = measure q[1];',
    'cond_u3': H + 'qubit[2] q; bit[1] c; h q[0]; c[0] = measure q[0]; if (c == 1) U(0.3,0.2,0.1) q[1];',
    'gatedef': H + 'gate bell a, b { h a; cx a, b; }\ngate rot(t) a { rx(t/2) a; rz(2*t) a; }\nqubit[2] q; bell q[0], q[1]; rot(pi/4) q[1];',
    'mods': H + 'qubit[3] q; inv @ s q[0]; pow(2) @ t q[1]; ctrl @ x q[0], q[2]; ctrl @ rz(0.3) q[1], q[2]; inv @ rx(0.4) q[0]; negctrl @ x q[0], q[1];',
    'forloop': H + 'qubit[4] q; for int i in [0:2] { h q[i]; cx q[i], q[i+1]; }',
    'broadcast': H + 'qubit[3] q; qubit[3] r; h q; cx q, r;',
    'const': H + 'const float theta = pi/8; qubit[1] q; rx(2*theta + 0.1) q[0]; ry(sin(theta)) q[0];',
    'qasm2': 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2]; creg c[2]; h q[0]; cx q[0],q[1]; measure q -> c;',
    'multireg': H + 'qubit[2] a; qubit[1] b; bit[3] c; x a[1]; cx a[1], b[0]; h a[0]; c[0] = measure a[0]; c[1] = measure a[1]; c[2] = measure b[0];',
    'reset': H + 'qubit[2] q; x q[0]; reset q[0]; h q[1];',
    'gphase': H + 'qubit[1] q; gphase(0.3); h q[0];',
    'gatedef_nonzero': H + 'gate rot(t) a, b { rx(t) b; cx a, b; }\nqubit[2] x; qubit[3] q; rot(0.5) q[2], x[1]; rot(0.25) q[0], q[1];',
    'ctrl_custom': H + 'gate g(t) a { ry(t) a; h a; }\nqubit[3] q; ctrl @ g(0.7) q[0], q[2]; inv @ g(0.3) q[1]; pow(2) @ g(0.1) q[1];',
    'negstep': H + 'qubit[4] q; for int i in [3:-1:1] { h q[i]; }',
    'reg_names': H + 'qubit[2] circuit; bit[2] np; h circuit[0]; cx circuit[0], circuit[1]; np = measure circuit;',
}

# status expected per target for programs the QSDK cannot express
QSDK_UNSUPPORTED = {'cond_bit'}

INVALID = {
    'syntax': H + 'qubit[2] q; h q[0] cx q[0], q[1];',
    'undeclared': H + 'qubit[2] q; h r[0];',
    'range': H + 'qubit[2] q; h q[5];',
    'unknown gate': H + 'qubit[2] q; foo q[0];',
    'arity': H + 'qubit[2] q; cx q[0];',
    'params': H + 'qubit[2] q; rx q[0];',
    'while': H + 'qubit[1] q; bit[1] c; while (c == 0) { h q[0]; }',
    'dup': H + 'qubit[2] q; cx q[0], q[0];',
    'empty': '',
    'neq': H + 'qubit[2] q; bit[1] c; if (c != 1) x q[0];',
    'clrange': H + 'qubit[1] q; bit[1] c; c[3] = measure q[0];',
    'bad char': H + 'qubit[1] q; h q[0] $;',
    'step0': H + 'qubit[2] q; for int i in [0:0:2] { h q[0]; }',
    'ctrl gphase': H + 'qubit[2] q; ctrl @ gphase(0.1) q[0];',
    'no ctrl form': H + 'qubit[2] q; ctrl @ sx q[0], q[1];',
    'attr': H + 'qubit[1] q; rx((1).__class__) q[0];',
    'cond range': H + 'qubit[1] q; bit[2] c; if (c[2] == 1) x q[0];',
    'cond value': H + 'qubit[1] q; bit[2] c; if (c == 7) x q[0];',
}
