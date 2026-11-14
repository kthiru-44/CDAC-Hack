import sys, traceback, numpy as np
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
from qnvkit.transpile.api import transpile
from qnvkit.qasm.parser3 import parse_qasm3
from qnvkit.sim import compute_statevector
H='OPENQASM 3.0;\ninclude "stdgates.inc";\n'
progs={
'basic': H+'qubit[3] q; bit[3] c; h q[0]; cx q[0],q[1]; rx(pi/3) q[2]; ccx q[0],q[1],q[2]; c = measure q;',
'allstd': H+'qubit[3] q; p(0.3) q[0]; x q[0]; y q[1]; z q[2]; h q[0]; s q[1]; sdg q[2]; t q[0]; tdg q[1]; sx q[2]; rx(0.1) q[0]; ry(0.2) q[1]; rz(0.3) q[2]; cx q[0],q[1]; cy q[1],q[2]; cz q[0],q[2]; cp(0.4) q[0],q[1]; crx(0.5) q[1],q[2]; cry(0.6) q[0],q[2]; crz(0.7) q[0],q[1]; ch q[1],q[2]; swap q[0],q[2]; ccx q[0],q[1],q[2]; cswap q[0],q[1],q[2]; cu(0.1,0.2,0.3,0.4) q[0],q[1]; phase(0.2) q[1]; cphase(0.3) q[0],q[2]; id q[0]; u1(0.3) q[0]; u2(0.1,0.2) q[1]; u3(0.1,0.2,0.3) q[2]; U(0.3,0.2,0.1) q[0];',
'barrier': H+'qubit[2] q; bit[2] c; h q[0]; barrier q; cx q[0],q[1]; barrier q[0]; c[0] = measure q[0]; c[1] = measure q[1];',
'single': H+'qubit q; bit c; h q; c = measure q;',
'cond_bit': H+'qubit[2] q; bit[2] c; h q[0]; c[0] = measure q[0]; if (c[0] == 1) { x q[1]; } c[1] = measure q[1];',
'cond_reg': H+'qubit[2] q; bit[1] c; bit[1] d; h q[0]; c[0] = measure q[0]; if (c == 1) x q[1]; d[0] = measure q[1];',
'cond_u3': H+'qubit[2] q; bit[1] c; h q[0]; c[0] = measure q[0]; if (c == 1) U(0.3,0.2,0.1) q[1];',
'gatedef': H+'gate bell a, b { h a; cx a, b; }\ngate rot(t) a { rx(t/2) a; rz(2*t) a; }\nqubit[2] q; bell q[0], q[1]; rot(pi/4) q[1];',
'mods': H+'qubit[3] q; inv @ s q[0]; pow(2) @ t q[1]; ctrl @ x q[0], q[2]; ctrl @ rz(0.3) q[1], q[2]; inv @ rx(0.4) q[0]; negctrl @ x q[0], q[1];',
'forloop': H+'qubit[4] q; for int i in [0:2] { h q[i]; cx q[i], q[i+1]; }',
'broadcast': H+'qubit[3] q; qubit[3] r; h q; cx q, r;',
'const': H+'const float theta = pi/8; qubit[1] q; rx(2*theta + 0.1) q[0]; ry(sin(theta)) q[0];',
'qasm2': 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2]; creg c[2]; h q[0]; cx q[0],q[1]; measure q -> c;',
'multireg': H+'qubit[2] a; qubit[1] b; bit[3] c; x a[1]; cx a[1], b[0]; h a[0]; c[0] = measure a[0]; c[1] = measure a[1]; c[2] = measure b[0];',
'reset': H+'qubit[2] q; x q[0]; reset q[0]; h q[1];',
'gphase': H+'qubit[1] q; gphase(0.3); h q[0];',
}
bad={
'syntax': H+'qubit[2] q; h q[0] cx q[0], q[1];',
'undeclared': H+'qubit[2] q; h r[0];',
'range': H+'qubit[2] q; h q[5];',
'unknown gate': H+'qubit[2] q; foo q[0];',
'arity': H+'qubit[2] q; cx q[0];',
'params': H+'qubit[2] q; rx q[0];',
'while': H+'qubit[1] q; bit[1] c; while (c == 0) { h q[0]; }',
'dup': H+'qubit[2] q; cx q[0], q[0];',
'empty': '',
'neq': H+'qubit[2] q; bit[1] c; if (c != 1) x q[0];',
'clrange': H+'qubit[1] q; bit[1] c; c[3] = measure q[0];',
}
import qiskit, cirq
from qiskit.quantum_info import Statevector
def fid(a,b): return abs(np.vdot(a,b))**2
for name,src in progs.items():
    try:
        res=transpile(src, targets=("qiskit","cirq","cudaq","qniverse"))
    except Exception as e:
        print(f"{name:10s} PARSE-EXC {type(e).__name__}: {str(e)[:150]}"); continue
    ir=parse_qasm3(src); out=[]
    try: ref=compute_statevector(ir)
    except Exception as e: ref=None; out.append('REFSIM-EXC '+str(e)[:60])
    for t,r in res.items():
        st=r.report.status
        try: compile(r.code,t,'exec'); comp='compiles'
        except SyntaxError as e: comp='SYNTAXERR:'+str(e)[:50]
        extra=''
        if comp=='compiles' and t=='qiskit':
            try:
                ns={}; exec(r.code,ns); qc=ns['build_circuit']()
                if ref is not None and not any(o.condition for o in ir.ops) and not any(o.name=='reset' for o in ir.ops):
                    extra=' fid=%.6f'%fid(ref,np.array(Statevector(qc.remove_final_measurements(inplace=False))))
                else: extra=' built'
            except Exception as e: extra=' RUN-EXC '+type(e).__name__+':'+str(e)[:70]
        if comp=='compiles' and t=='cirq':
            try:
                ns={}; exec(r.code,ns); c=ns['build_circuit']()
                if ref is not None and not any(o.condition for o in ir.ops) and not any(o.name in('reset',) for o in ir.ops):
                    qs=[cirq.NamedQubit(f'{rg.name}_{i}') for rg in ir.qregs for i in range(rg.size)]
                    cu=cirq.Circuit(op for op in c.all_operations() if not isinstance(op.gate,cirq.MeasurementGate))
                    sv=cirq.Simulator(dtype=np.complex128).simulate(cu,qubit_order=qs).final_state_vector
                    n=ir.num_qubits; sv=np.transpose(sv.reshape((2,)*n),list(reversed(range(n)))).flatten()
                    extra=' fid=%.6f'%fid(ref,sv)
                else:
                    cirq.Simulator().run(c,repetitions=20); extra=' ran'
            except Exception as e: extra=' RUN-EXC '+type(e).__name__+':'+str(e)[:70]
        if comp=='compiles' and t=='qniverse':
            try:
                import qnvkit.qsdk_adapter
                ns={}; exec(r.code,ns); c=ns['build_circuit'](); c.qasm(); extra=' built'
            except Exception as e: extra=' RUN-EXC '+type(e).__name__+':'+str(e)[:70]
        out.append(f"{t}:{st}/{comp}{extra}" + (" UNSUP=%d"%len(r.report.unsupported_constructs) if r.report.unsupported_constructs else ""))
    print(f"{name:10s} "+" | ".join(out))
print('---- invalid inputs')
for name,src in bad.items():
    try:
        res=transpile(src, targets=("qiskit",)); print(f"{name:13s} ACCEPTED status={res['qiskit'].report.status} unsup={res['qiskit'].report.unsupported_constructs[:1]}")
    except Exception as e: print(f"{name:13s} {type(e).__name__}: {str(e).splitlines()[0][:130]}")
