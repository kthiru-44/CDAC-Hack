"""
Tests for qnvkit.qasm.lexer: Universal Tokenizer.
"""

import pytest
from qnvkit.qasm.lexer import QASMLexer, TokenType


def test_lexer_tokens():
    code = """// Test comment
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
h q[0];
cx q[0], q[1];
c[0] = measure q[0];
"""
    lexer = QASMLexer(code)
    tokens = lexer.tokenize()

    types = [t.type for t in tokens]
    assert TokenType.IDENTIFIER in types  # OPENQASM, include, qubit, etc.
    assert TokenType.STRING in types      # "stdgates.inc"
    assert TokenType.ASSIGN in types      # =
    assert TokenType.EOF == types[-1]

    # Verify line numbers
    # Line 2: OPENQASM
    openqasm_tok = [t for t in tokens if t.value == "OPENQASM"][0]
    assert openqasm_tok.location.line == 2
    assert openqasm_tok.location.col == 1
