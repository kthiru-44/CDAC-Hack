"""
qnvkit.qasm.parser2: OpenQASM 2.0 Parser for extracting CircuitIR from qc.qasm().
"""

import re
from typing import List, Dict, Tuple, Optional
from qnvkit.ir import CircuitIR, Register, Op
from qnvkit.qasm.expr import evaluate_expression

# Regex patterns
_COMMENT_RE = re.compile(r"//.*")
_QREG_RE = re.compile(r"^\s*qreg\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\[\s*(\d+)\s*\]\s*$")
_CREG_RE = re.compile(r"^\s*creg\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\[\s*(\d+)\s*\]\s*$")
_IF_RE = re.compile(r"^\s*if\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*==\s*(\d+)\s*\)\s*(.+)$")
_MEASURE_RE = re.compile(r"^\s*measure\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\[\s*(\d+)\s*\]\s*->\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\[\s*(\d+)\s*\]\s*$")
_BARRIER_RE = re.compile(r"^\s*barrier\s*(.*)$")
_RESET_RE = re.compile(r"^\s*reset\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\[\s*(\d+)\s*\]\s*$")
_GATE_RE = re.compile(r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\(\s*([^)]*)\s*\))?\s*(.+)$")
_ARG_RE = re.compile(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\[\s*(\d+)\s*\]")


def parse_qasm2(qasm_text: str) -> CircuitIR:
    """
    Parses OpenQASM 2.0 string and returns an immutable CircuitIR.
    """
    # Remove comments
    lines = []
    for line in qasm_text.splitlines():
        cleaned = _COMMENT_RE.sub("", line).strip()
        if cleaned:
            lines.append(cleaned)
            
    full_text = " ".join(lines)
    statements = [s.strip() for s in full_text.split(";") if s.strip()]

    qregs: List[Register] = []
    cregs: List[Register] = []
    ops: List[Op] = []

    # Wire offset mapping
    qreg_offsets: Dict[str, int] = {}
    creg_offsets: Dict[str, int] = {}
    num_qubits = 0
    num_clbits = 0

    for stmt in statements:
        # Check OPENQASM / include headers
        if stmt.startswith("OPENQASM") or stmt.startswith("include"):
            continue

        # Check qreg
        m_qreg = _QREG_RE.match(stmt)
        if m_qreg:
            name, size_s = m_qreg.group(1), int(m_qreg.group(2))
            qregs.append(Register(name, size_s, is_classical=False))
            qreg_offsets[name] = num_qubits
            num_qubits += size_s
            continue

        # Check creg
        m_creg = _CREG_RE.match(stmt)
        if m_creg:
            name, size_s = m_creg.group(1), int(m_creg.group(2))
            cregs.append(Register(name, size_s, is_classical=True))
            creg_offsets[name] = num_clbits
            num_clbits += size_s
            continue

        # Check conditional
        condition = None
        m_if = _IF_RE.match(stmt)
        if m_if:
            cname = m_if.group(1)
            cval = int(m_if.group(2))
            condition = (cname, cval)
            stmt = m_if.group(3).strip()

        # Check measure
        m_meas = _MEASURE_RE.match(stmt)
        if m_meas:
            qr, qi, cr, ci = m_meas.group(1), int(m_meas.group(2)), m_meas.group(3), int(m_meas.group(4))
            q_wire = qreg_offsets[qr] + qi
            c_wire = creg_offsets[cr] + ci
            ops.append(Op("measure", qubits=(q_wire,), clbits=(c_wire,), condition=condition))
            continue

        # Check reset
        m_res = _RESET_RE.match(stmt)
        if m_res:
            qr, qi = m_res.group(1), int(m_res.group(2))
            q_wire = qreg_offsets[qr] + qi
            ops.append(Op("reset", qubits=(q_wire,), condition=condition))
            continue

        # Check barrier
        m_bar = _BARRIER_RE.match(stmt)
        if m_bar:
            args_str = m_bar.group(1).strip()
            qubits = []
            if args_str:
                for arg_match in _ARG_RE.finditer(args_str):
                    qr, qi = arg_match.group(1), int(arg_match.group(2))
                    qubits.append(qreg_offsets[qr] + qi)
            else:
                qubits = list(range(num_qubits))
            ops.append(Op("barrier", qubits=tuple(qubits), condition=condition))
            continue

        # Gate application
        m_gate = _GATE_RE.match(stmt)
        if m_gate:
            gname = m_gate.group(1).lower()
            params_raw = m_gate.group(2)
            args_raw = m_gate.group(3)

            params = ()
            if params_raw:
                params = tuple(evaluate_expression(p) for p in params_raw.split(","))

            qubits = []
            for arg_match in _ARG_RE.finditer(args_raw):
                qr, qi = arg_match.group(1), int(arg_match.group(2))
                qubits.append(qreg_offsets[qr] + qi)

            ops.append(Op(gname, qubits=tuple(qubits), params=params, condition=condition))
        else:
            raise ValueError(f"Unable to parse OpenQASM 2 statement: '{stmt}'")

    return CircuitIR(
        num_qubits=num_qubits,
        num_clbits=num_clbits,
        qregs=tuple(qregs),
        cregs=tuple(cregs),
        ops=tuple(ops),
    )
