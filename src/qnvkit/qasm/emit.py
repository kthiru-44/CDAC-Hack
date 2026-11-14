"""
qnvkit.qasm.emit: OpenQASM 2.0 and OpenQASM 3.0 emitter from CircuitIR.
"""

from qnvkit.ir import CircuitIR, Condition


def emit_qasm2(ir: CircuitIR) -> str:
    """Emits standard OpenQASM 2.0 code."""
    return ir.to_qasm2()


def emit_qasm3(ir: CircuitIR) -> str:
    """Emits standard OpenQASM 3.0 code."""
    lines = [
        "OPENQASM 3.0;",
        'include "stdgates.inc";',
    ]

    for qr in ir.qregs:
        lines.append(f"qubit[{qr.size}] {qr.name};")
    for cr in ir.cregs:
        lines.append(f"bit[{cr.size}] {cr.name};")

    q_map = ir.get_qubit_reg_map()
    c_map = ir.get_clbit_reg_map()

    for op in ir.ops:
        q_args = []
        for q in op.qubits:
            r_name, r_idx = q_map.get(q, ('q', q))
            q_args.append(f"{r_name}[{r_idx}]")

        prefix = ""
        if op.condition:
            if isinstance(op.condition, Condition):
                c = op.condition
                target = f"{c.register}[{c.index}]" if c.index is not None else c.register
                prefix = f"if ({target} == {c.value}) "
            else:
                cname, cval = op.condition
                prefix = f"if ({cname} == {cval}) "

        if op.name == "barrier":
            lines.append(f"{prefix}barrier {', '.join(q_args)};")
        elif op.name == "reset":
            for qa in q_args:
                lines.append(f"{prefix}reset {qa};")
        elif op.name == "measure":
            for q_idx, c_idx in zip(op.qubits, op.clbits):
                qr_name, qr_i = q_map.get(q_idx, ('q', q_idx))
                cr_name, cr_i = c_map.get(c_idx, ('c', c_idx))
                lines.append(f"{prefix}{cr_name}[{cr_i}] = measure {qr_name}[{qr_i}];")
        else:
            param_str = ""
            if op.params:
                param_str = f"({', '.join(f'{p:.10g}' for p in op.params)})"
            lines.append(f"{prefix}{op.name}{param_str} {', '.join(q_args)};")

    return "\n".join(lines) + "\n"
