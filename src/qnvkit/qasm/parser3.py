"""
Recursive Descent Parser for OpenQASM 3.0 and OpenQASM 2.0.

Parses declarations, register allocations, gate applications, custom gate inlining,
modifiers (inv@, pow@, ctrl@), unrolled for-loops, measurement semantics,
classical conditions, and produces CircuitIR with precise line:column diagnostics.
"""

from __future__ import annotations
import math
from typing import List, Dict, Optional, Tuple, Any, Set, Union
from qnvkit.ir import CircuitIR, Register, QubitRef, ClbitRef, Op, Condition
from qnvkit.qasm.lexer import QASMLexer, Token
from qnvkit.qasm.diagnostics import QASMError
from qnvkit.qasm.expr import ExprEvaluator, evaluate_expression
from qnvkit.gates import get_gate_def


class CustomGateDef:
    """In-memory representation of a user-defined custom gate."""
    def __init__(self, name: str, params: List[str], qubits: List[str], body_tokens: List[Token]):
        self.name = name
        self.params = params
        self.qubits = qubits
        self.body_tokens = body_tokens


class QASM3Parser:
    """Recursive descent parser generating CircuitIR from OpenQASM 3/2 source."""

    def __init__(self, source: str, name: str = "circuit"):
        self.source = source
        self.name = name
        self.lexer = QASMLexer(source)
        self.tokens = self.lexer.tokenize()
        self.pos = 0
        self.qregs: Dict[str, int] = {}
        self.cregs: Dict[str, int] = {}
        self.ops: List[Op] = []
        self.custom_gates: Dict[str, CustomGateDef] = {}
        self.constants: Dict[str, float] = {}

    def parse(self) -> CircuitIR:
        while not self._is_at_end():
            self._parse_statement()

        num_qubits = sum(self.qregs.values())
        num_clbits = sum(self.cregs.values())
        qregs_tuple = tuple(Register(name, size) for name, size in self.qregs.items())
        cregs_tuple = tuple(Register(name, size, is_classical=True) for name, size in self.cregs.items())

        return CircuitIR(
            num_qubits=num_qubits,
            num_clbits=num_clbits,
            qregs=qregs_tuple,
            cregs=cregs_tuple,
            ops=tuple(self.ops),
            name=self.name
        )

    def _qubit_to_flat(self, reg_name: str, idx: int) -> int:
        if reg_name not in self.qregs:
            raise KeyError(f"Undefined quantum register '{reg_name}'")
        offset = 0
        for r_name, r_size in self.qregs.items():
            if r_name == reg_name:
                if 0 <= idx < r_size:
                    return offset + idx
                raise IndexError(f"Index {idx} out of range for {reg_name}[{r_size}]")
            offset += r_size
        raise KeyError(f"Register '{reg_name}' not found")

    def _clbit_to_flat(self, reg_name: str, idx: int) -> int:
        if reg_name not in self.cregs:
            raise KeyError(f"Undefined classical register '{reg_name}'")
        offset = 0
        for r_name, r_size in self.cregs.items():
            if r_name == reg_name:
                if 0 <= idx < r_size:
                    return offset + idx
                raise IndexError(f"Index {idx} out of range for {reg_name}[{r_size}]")
            offset += r_size
        raise KeyError(f"Register '{reg_name}' not found")

    def _current(self) -> Token:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else self.tokens[-1]

    def _is_at_end(self) -> bool:
        return self._current().kind == "EOF"

    def _peek_next(self) -> Token:
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return self.tokens[-1]

    def _match(self, value: str, kind: Optional[str] = None) -> bool:
        t = self._current()
        if t.kind == "EOF":
            return False
        if kind and t.kind != kind:
            return False
        if t.value == value:
            self.pos += 1
            return True
        return False

    def _consume(self, value: str, message: Optional[str] = None) -> Token:
        t = self._current()
        if t.value == value:
            self.pos += 1
            return t
        msg = message or f"Expected '{value}', got '{t.value}'"
        raise QASMError(msg, t.line, t.col, self.source)

    def _consume_kind(self, kind: str, message: Optional[str] = None) -> Token:
        t = self._current()
        if t.kind == kind:
            self.pos += 1
            return t
        msg = message or f"Expected token kind '{kind}', got '{t.kind}' ({t.value})"
        raise QASMError(msg, t.line, t.col, self.source)

    def _parse_statement(self, condition: Optional[Tuple[str, int]] = None) -> None:
        t = self._current()

        # 1. OPENQASM version declaration
        if self._match("OPENQASM"):
            ver = self._consume_kind("NUMBER").value
            self._consume(";", "Expected ';' after OPENQASM version declaration")
            return

        # 2. include "..."
        if self._match("include"):
            inc = self._consume_kind("STRING").value
            self._consume(";", "Expected ';' after include directive")
            return

        # 3. Explicit unsupported constructs (clean diagnostics)
        if t.value in ("while", "extern", "def", "delay", "cal", "defcal", "defcalgrammar", "input", "output"):
            raise QASMError(
                f"Unsupported OpenQASM 3 construct '{t.value}'. Dynamic runtime control flow and pulse calibration are unsupported on target backends.",
                t.line, t.col, self.source
            )

        # 4. const declarations: const float[64] x = ...;
        if self._match("const"):
            self._consume_kind("IDENT")
            if self._match("["):
                while not self._match("]") and not self._is_at_end():
                    self.pos += 1
            name = self._consume_kind("IDENT").value
            self._consume("=")
            expr_str = self._collect_until_semicolon()
            val = evaluate_expression(expr_str, variables=self.constants)
            self.constants[name] = val
            self._consume(";")
            return

        # 5. Quantum register declaration: qubit[n] name; or qreg name[n];
        if self._match("qubit"):
            self._consume("[")
            size_tok = self._consume_kind("NUMBER")
            size = int(size_tok.value)
            self._consume("]")
            name = self._consume_kind("IDENT").value
            self._consume(";")
            if name in self.qregs:
                raise QASMError(f"Quantum register '{name}' already declared", t.line, t.col, self.source)
            self.qregs[name] = size
            return

        if self._match("qreg"):
            name = self._consume_kind("IDENT").value
            self._consume("[")
            size = int(self._consume_kind("NUMBER").value)
            self._consume("]")
            self._consume(";")
            if name in self.qregs:
                raise QASMError(f"Quantum register '{name}' already declared", t.line, t.col, self.source)
            self.qregs[name] = size
            return

        # 6. Classical register declaration: bit[n] name; or creg name[n];
        if self._match("bit"):
            size = 1
            if self._match("["):
                size = int(self._consume_kind("NUMBER").value)
                self._consume("]")
            name = self._consume_kind("IDENT").value
            self._consume(";")
            if name in self.cregs:
                raise QASMError(f"Classical register '{name}' already declared", t.line, t.col, self.source)
            self.cregs[name] = size
            return

        if self._match("creg"):
            name = self._consume_kind("IDENT").value
            self._consume("[")
            size = int(self._consume_kind("NUMBER").value)
            self._consume("]")
            self._consume(";")
            if name in self.cregs:
                raise QASMError(f"Classical register '{name}' already declared", t.line, t.col, self.source)
            self.cregs[name] = size
            return

        # 7. Barrier: barrier q[0], q[1]; or barrier;
        if self._match("barrier"):
            line, col = t.line, t.col
            flat_qubits: List[int] = []
            if not self._match(";"):
                while True:
                    q_ref = self._parse_bit_or_register_ref(is_quantum=True)
                    flat_qubits.extend(self._expand_qubit_target(q_ref))
                    if self._match(";"):
                        break
                    self._consume(",")
            else:
                total_qubits = sum(self.qregs.values())
                flat_qubits = list(range(total_qubits))
            self.ops.append(Op("barrier", qubits=tuple(flat_qubits), condition=condition, line=line, col=col))
            return

        # 8. Reset: reset q[0]; or reset q;
        if self._match("reset"):
            line, col = t.line, t.col
            q_ref = self._parse_bit_or_register_ref(is_quantum=True)
            self._consume(";")
            for q in self._expand_qubit_target(q_ref):
                self.ops.append(Op("reset", qubits=(q,), condition=condition, line=line, col=col))
            return

        # 9. Measurement: c[0] = measure q[0]; OR measure q[0] -> c[0];
        if self._match("measure"):
            line, col = t.line, t.col
            q_ref = self._parse_bit_or_register_ref(is_quantum=True)
            self._consume("->")
            c_ref = self._parse_bit_or_register_ref(is_quantum=False)
            self._consume(";")
            self._emit_measurement(q_ref, c_ref, line, col, condition)
            return

        # 10. Classical assignment or classical measure form: c = measure q; or c[0] = measure q[0];
        if t.kind == "IDENT" and t.value in self.cregs and self._peek_next().value in ("[", "="):
            c_ref = self._parse_bit_or_register_ref(is_quantum=False)
            self._consume("=")
            if self._match("measure"):
                line, col = t.line, t.col
                q_ref = self._parse_bit_or_register_ref(is_quantum=True)
                self._consume(";")
                self._emit_measurement(q_ref, c_ref, line, col, condition)
                return
            else:
                expr_str = self._collect_until_semicolon()
                self._consume(";")
                return

        # 11. Classical Condition: if (c == 1) ...
        if self._match("if"):
            self._consume("(")
            cond_obj = self._parse_condition()
            self._consume(")")
            cond_tuple = (cond_obj.register, cond_obj.value)
            if self._match("{"):
                while not self._match("}") and not self._is_at_end():
                    self._parse_statement(condition=cond_tuple)
            else:
                self._parse_statement(condition=cond_tuple)
            return

        # 12. For loop unrolling: for uint[32] i in [0:n-1] { ... }
        if self._match("for"):
            self._parse_for_loop(condition=condition)
            return

        # 13. Gate definition: gate my_gate(p0, p1) q0, q1 { ... }
        if self._match("gate"):
            self._parse_gate_definition()
            return

        # 14. Gate applications and Modifiers (inv@, pow(k)@, ctrl@)
        self._parse_gate_application(condition=condition)

    def _parse_condition(self) -> Condition:
        var_tok = self._consume_kind("IDENT")
        var_name = var_tok.value
        bit_idx = None
        if self._match("["):
            bit_idx = int(self._consume_kind("NUMBER").value)
            self._consume("]")

        op_tok = self._consume_kind("SYMBOL", "Expected comparison operator (==, !=, <, <=, >, >=)")
        val_tok = self._consume_kind("NUMBER", "Expected integer value in condition")
        val = int(val_tok.value)
        return Condition(register=var_name, value=val, index=bit_idx, op=op_tok.value)

    def _parse_for_loop(self, condition: Optional[Tuple[str, int]]) -> None:
        if self._current().value in ("int", "uint") or self._current().value.startswith("uint") or self._current().value.startswith("int"):
            self.pos += 1
            if self._match("["):
                while not self._match("]") and not self._is_at_end():
                    self.pos += 1

        var_name = self._consume_kind("IDENT").value
        self._consume("in")
        self._consume("[")

        start_expr = self._collect_until_colon_or_bracket()
        start_val = int(round(evaluate_expression(start_expr, variables=self.constants)))
        self._consume(":")

        step_val = 1
        second_expr = self._collect_until_colon_or_bracket()
        if self._match(":"):
            step_val = int(round(evaluate_expression(second_expr, variables=self.constants)))
            end_expr = self._collect_until_colon_or_bracket()
            end_val = int(round(evaluate_expression(end_expr, variables=self.constants)))
        else:
            end_val = int(round(evaluate_expression(second_expr, variables=self.constants)))

        self._consume("]")
        self._consume("{")

        loop_body_tokens: List[Token] = []
        brace_depth = 1
        while brace_depth > 0 and not self._is_at_end():
            t = self._current()
            if t.value == "{":
                brace_depth += 1
            elif t.value == "}":
                brace_depth -= 1
                if brace_depth == 0:
                    self.pos += 1
                    break
            loop_body_tokens.append(t)
            self.pos += 1

        loop_values = range(start_val, end_val + 1, step_val)
        for val in loop_values:
            local_constants = dict(self.constants)
            local_constants[var_name] = float(val)

            substituted_tokens: List[Token] = []
            for tok in loop_body_tokens:
                if tok.kind == "IDENT" and tok.value == var_name:
                    substituted_tokens.append(Token("NUMBER", str(val), tok.line, tok.col))
                else:
                    substituted_tokens.append(tok)
            substituted_tokens.append(Token("EOF", "", 0, 0))

            sub_parser = QASM3Parser(self.source, name=self.name)
            sub_parser.tokens = substituted_tokens
            sub_parser.pos = 0
            sub_parser.qregs = self.qregs
            sub_parser.cregs = self.cregs
            sub_parser.ops = self.ops
            sub_parser.custom_gates = self.custom_gates
            sub_parser.constants = local_constants
            while not sub_parser._is_at_end():
                sub_parser._parse_statement(condition=condition)

    def _parse_gate_definition(self) -> None:
        name_tok = self._consume_kind("IDENT")
        name = name_tok.value

        params: List[str] = []
        if self._match("("):
            if not self._match(")"):
                while True:
                    p = self._consume_kind("IDENT").value
                    params.append(p)
                    if self._match(")"):
                        break
                    self._consume(",")

        qubits: List[str] = []
        while True:
            q = self._consume_kind("IDENT").value
            qubits.append(q)
            if self._current().value == "{":
                break
            self._consume(",")

        self._consume("{")
        body_tokens: List[Token] = []
        brace_depth = 1
        while brace_depth > 0 and not self._is_at_end():
            t = self._current()
            if t.value == "{":
                brace_depth += 1
            elif t.value == "}":
                brace_depth -= 1
                if brace_depth == 0:
                    self.pos += 1
                    break
            body_tokens.append(t)
            self.pos += 1

        self.custom_gates[name] = CustomGateDef(name, params, qubits, body_tokens)

    def _parse_gate_application(self, condition: Optional[Tuple[str, int]] = None) -> None:
        start_tok = self._current()
        line, col = start_tok.line, start_tok.col

        modifiers: List[Tuple[str, Any]] = []
        while self._current().value in ("inv", "pow", "ctrl", "negctrl"):
            mod_name = self._consume_kind("KEYWORD").value
            mod_arg = None
            if self._match("("):
                expr_str = self._collect_until_closing_paren()
                mod_arg = evaluate_expression(expr_str, variables=self.constants)
                self._consume(")")
            self._consume("@")
            modifiers.append((mod_name, mod_arg))

        gate_name_tok = self._consume_kind("IDENT", "Expected gate name")
        gate_name = gate_name_tok.value

        params: List[float] = []
        if self._match("("):
            if not self._match(")"):
                while True:
                    expr_str = self._collect_until_comma_or_paren()
                    val = evaluate_expression(expr_str, variables=self.constants)
                    params.append(val)
                    if self._match(")"):
                        break
                    self._consume(",")

        qubit_targets: List[Union[Tuple[str, int], Tuple[str, None]]] = []
        while True:
            target = self._parse_bit_or_register_ref(is_quantum=True)
            qubit_targets.append(target)
            if self._match(";"):
                break
            self._consume(",")

        is_broadcast = any(t[1] is None for t in qubit_targets)
        if is_broadcast:
            first_reg = next(t[0] for t in qubit_targets if t[1] is None)
            reg_size = self.qregs[first_reg]
            for i in range(reg_size):
                expanded_targets = []
                for t in qubit_targets:
                    if t[1] is None:
                        expanded_targets.append(self._qubit_to_flat(t[0], i))
                    else:
                        expanded_targets.append(self._qubit_to_flat(t[0], t[1]))
                self._apply_resolved_gate(gate_name, params, expanded_targets, modifiers, condition, line, col)
        else:
            flat_qubits = [self._qubit_to_flat(t[0], t[1]) for t in qubit_targets]
            self._apply_resolved_gate(gate_name, params, flat_qubits, modifiers, condition, line, col)

    def _apply_resolved_gate(
        self,
        gate_name: str,
        params: List[float],
        qubits: List[int],
        modifiers: List[Tuple[str, Any]],
        condition: Optional[Tuple[str, int]],
        line: int,
        col: int
    ) -> None:
        if gate_name in self.custom_gates:
            self._inline_custom_gate(gate_name, params, qubits, modifiers, condition, line, col)
            return

        final_gate_name = gate_name.lower()
        final_params = list(params)
        final_qubits = list(qubits)

        for mod_name, mod_arg in reversed(modifiers):
            if mod_name == "inv":
                if final_gate_name == "s":
                    final_gate_name = "sdg"
                elif final_gate_name == "sdg":
                    final_gate_name = "s"
                elif final_gate_name == "t":
                    final_gate_name = "tdg"
                elif final_gate_name == "tdg":
                    final_gate_name = "t"
                elif final_gate_name == "sx":
                    final_gate_name = "sxdg"
                elif final_gate_name == "sxdg":
                    final_gate_name = "sx"
                elif final_gate_name in ("rx", "ry", "rz", "p", "phase", "u1"):
                    if final_params:
                        final_params[0] = -final_params[0]
                elif final_gate_name in ("u", "u3"):
                    if len(final_params) >= 3:
                        final_params = [-final_params[0], -final_params[2], -final_params[1]]
                elif final_gate_name in ("x", "y", "z", "h", "cx", "cz", "swap", "ccx"):
                    pass
                else:
                    raise QASMError(f"inv modifier not supported for gate '{final_gate_name}'", line, col, self.source)
            elif mod_name == "ctrl":
                if final_gate_name == "x":
                    final_gate_name = "cx"
                elif final_gate_name == "z":
                    final_gate_name = "cz"
                elif final_gate_name == "cx":
                    final_gate_name = "ccx"
            elif mod_name == "pow":
                power = float(mod_arg) if mod_arg is not None else 1.0
                if final_gate_name in ("rx", "ry", "rz", "p", "phase", "u1") and final_params:
                    final_params[0] = final_params[0] * power
                elif final_gate_name == "z" and abs(power - 0.5) < 1e-9:
                    final_gate_name = "s"
                elif final_gate_name == "s" and abs(power - 0.5) < 1e-9:
                    final_gate_name = "t"
                elif final_gate_name == "z" and abs(power - 0.25) < 1e-9:
                    final_gate_name = "t"
                elif power.is_integer() and int(power) >= 1:
                    k = int(power)
                    for _ in range(k):
                        self.ops.append(Op(
                            name=final_gate_name,
                            qubits=tuple(final_qubits),
                            params=tuple(final_params),
                            condition=condition,
                            line=line,
                            col=col
                        ))
                    return
                else:
                    raise QASMError(f"pow({power}) modifier not supported for gate '{final_gate_name}'", line, col, self.source)

        self.ops.append(Op(
            name=final_gate_name,
            qubits=tuple(final_qubits),
            params=tuple(final_params),
            condition=condition,
            line=line,
            col=col
        ))

    def _inline_custom_gate(
        self,
        gate_name: str,
        params: List[float],
        qubits: List[int],
        modifiers: List[Tuple[str, Any]],
        condition: Optional[Tuple[str, int]],
        line: int,
        col: int
    ) -> None:
        cg = self.custom_gates[gate_name]
        if len(params) != len(cg.params):
            raise QASMError(f"Gate '{gate_name}' expects {len(cg.params)} parameters, got {len(params)}", line, col, self.source)
        if len(qubits) != len(cg.qubits):
            raise QASMError(f"Gate '{gate_name}' expects {len(cg.qubits)} qubits, got {len(qubits)}", line, col, self.source)

        param_sub = {formal: actual for formal, actual in zip(cg.params, params)}
        q_map = {reg: flat_idx for reg, flat_idx in zip(cg.qubits, qubits)}

        sub_tokens: List[Token] = []
        for tok in cg.body_tokens:
            if tok.kind == "IDENT" and tok.value in q_map:
                flat_idx = q_map[tok.value]
                # Synthesize flat wire access using special __flat__ register
                sub_tokens.extend([
                    Token("IDENT", "__flat__", tok.line, tok.col),
                    Token("SYMBOL", "[", tok.line, tok.col),
                    Token("NUMBER", str(flat_idx), tok.line, tok.col),
                    Token("SYMBOL", "]", tok.line, tok.col)
                ])
            elif tok.kind == "IDENT" and tok.value in param_sub:
                sub_tokens.append(Token("NUMBER", str(param_sub[tok.value]), tok.line, tok.col))
            else:
                sub_tokens.append(tok)
        sub_tokens.append(Token("EOF", "", 0, 0))

        sub_parser = QASM3Parser(self.source, name=self.name)
        sub_parser.tokens = sub_tokens
        sub_parser.pos = 0
        total_qubits = sum(self.qregs.values())
        sub_parser.qregs = dict(self.qregs)
        sub_parser.qregs["__flat__"] = total_qubits
        sub_parser.cregs = self.cregs
        sub_parser.ops = self.ops
        sub_parser.custom_gates = self.custom_gates
        sub_parser.constants = self.constants
        while not sub_parser._is_at_end():
            sub_parser._parse_statement(condition=condition)

    def _parse_bit_or_register_ref(self, is_quantum: bool = True) -> Tuple[str, Optional[int]]:
        name_tok = self._consume_kind("IDENT")
        name = name_tok.value
        reg_map = self.qregs if is_quantum else self.cregs
        if name not in reg_map:
            kind_str = "quantum" if is_quantum else "classical"
            raise QASMError(f"Undefined {kind_str} register '{name}'", name_tok.line, name_tok.col, self.source)

        if self._match("["):
            expr_tokens: List[str] = []
            bracket_depth = 1
            start_line = self._current().line
            start_col = self._current().col
            while bracket_depth > 0 and not self._is_at_end():
                t = self._current()
                if t.value == "[":
                    bracket_depth += 1
                elif t.value == "]":
                    bracket_depth -= 1
                    if bracket_depth == 0:
                        self.pos += 1
                        break
                expr_tokens.append(t.value)
                self.pos += 1
            expr_str = " ".join(expr_tokens)
            idx = int(round(evaluate_expression(expr_str, variables=self.constants)))
            return (name, idx)
        else:
            return (name, None)

    def _expand_qubit_target(self, target: Tuple[str, Optional[int]]) -> List[int]:
        reg_name, idx = target
        if idx is not None:
            return [self._qubit_to_flat(reg_name, idx)]
        size = self.qregs[reg_name]
        return [self._qubit_to_flat(reg_name, i) for i in range(size)]

    def _emit_measurement(self, q_target: Tuple[str, Optional[int]], c_target: Tuple[str, Optional[int]], line: int, col: int, condition: Optional[Tuple[str, int]]) -> None:
        q_reg, q_idx = q_target
        c_reg, c_idx = c_target

        if q_idx is None and c_idx is None:
            q_size = self.qregs[q_reg]
            c_size = self.cregs[c_reg]
            if q_size != c_size:
                raise QASMError(f"Cannot measure register '{q_reg}' of size {q_size} into register '{c_reg}' of size {c_size}", line, col, self.source)
            for i in range(q_size):
                q_flat = self._qubit_to_flat(q_reg, i)
                c_flat = self._clbit_to_flat(c_reg, i)
                self.ops.append(Op("measure", qubits=(q_flat,), clbits=(c_flat,), condition=condition, line=line, col=col))
            return

        if q_idx is not None and c_idx is not None:
            q_flat = self._qubit_to_flat(q_reg, q_idx)
            c_flat = self._clbit_to_flat(c_reg, c_idx)
            self.ops.append(Op("measure", qubits=(q_flat,), clbits=(c_flat,), condition=condition, line=line, col=col))
            return

        raise QASMError("Mismatched measurement register and bit targets", line, col, self.source)

    def _collect_until_semicolon(self) -> str:
        parts: List[str] = []
        while self._current().value != ";" and not self._is_at_end():
            parts.append(self._current().value)
            self.pos += 1
        return " ".join(parts)

    def _collect_until_comma_or_paren(self) -> str:
        parts: List[str] = []
        paren_depth = 0
        while not self._is_at_end():
            v = self._current().value
            if v == "(":
                paren_depth += 1
            elif v == ")":
                if paren_depth == 0:
                    break
                paren_depth -= 1
            elif v == "," and paren_depth == 0:
                break
            parts.append(v)
            self.pos += 1
        return " ".join(parts)

    def _collect_until_closing_paren(self) -> str:
        parts: List[str] = []
        paren_depth = 0
        while not self._is_at_end():
            v = self._current().value
            if v == "(":
                paren_depth += 1
            elif v == ")":
                if paren_depth == 0:
                    break
                paren_depth -= 1
            parts.append(v)
            self.pos += 1
        return " ".join(parts)

    def _collect_until_colon_or_bracket(self) -> str:
        parts: List[str] = []
        while not self._is_at_end():
            v = self._current().value
            if v in (":", "]"):
                break
            parts.append(v)
            self.pos += 1
        return " ".join(parts)


def parse_qasm3(source: str) -> CircuitIR:
    """Convenience function to parse an OpenQASM 3/2 string into CircuitIR."""
    return QASM3Parser(source).parse()
