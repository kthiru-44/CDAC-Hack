"""
qnvkit.qasm.lexer: Universal tokenizer for OpenQASM 2.0 and 3.0 with source location tracking.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Any
from qnvkit.qasm.diagnostics import SourceLocation, Diagnostic, QASMError


class TokenType(Enum):
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    SEMICOLON = auto()
    COMMA = auto()
    COLON = auto()       # :
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    ARROW = auto()       # ->
    EQUALS = auto()      # ==
    ASSIGN = auto()      # =
    AT = auto()          # @
    PLUS = auto()        # +
    MINUS = auto()       # -
    STAR = auto()        # *
    SLASH = auto()       # /
    CARET = auto()       # ^ or **
    OPERATOR = auto()    # != <= >= < > (comparison operators)
    EOF = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    location: SourceLocation

    def __init__(self, type_or_kind: Any, value: str, location_or_line: Any = 1, col: int = 1):
        if isinstance(location_or_line, SourceLocation):
            loc = location_or_line
        else:
            loc = SourceLocation(int(location_or_line), int(col))

        if isinstance(type_or_kind, TokenType):
            ttype = type_or_kind
        else:
            kind_map = {
                "NUMBER": TokenType.NUMBER,
                "STRING": TokenType.STRING,
                "IDENT": TokenType.IDENTIFIER,
                "KEYWORD": TokenType.IDENTIFIER,
                "SYMBOL": TokenType.SEMICOLON,
                "EOF": TokenType.EOF,
            }
            ttype = kind_map.get(type_or_kind, TokenType.IDENTIFIER)
        object.__setattr__(self, "type", ttype)
        object.__setattr__(self, "value", str(value))
        object.__setattr__(self, "location", loc)

    @property
    def line(self) -> int:
        return self.location.line

    @property
    def col(self) -> int:
        return self.location.col

    @property
    def kind(self) -> str:
        if self.type == TokenType.EOF:
            return "EOF"
        if self.type == TokenType.NUMBER:
            return "NUMBER"
        if self.type == TokenType.STRING:
            return "STRING"
        if self.type == TokenType.IDENTIFIER:
            if self.value in {
                "OPENQASM", "include", "qubit", "bit", "qreg", "creg", "gate",
                "def", "barrier", "reset", "measure", "if", "else", "for", "in",
                "return", "const", "inv", "pow", "ctrl", "negctrl",
                "while", "extern", "delay", "cal", "defcal", "defcalgrammar", "input", "output", "let"
            }:
                return "KEYWORD"
            return "IDENT"
        return "SYMBOL"




class QASMLexer:
    """Universal OpenQASM Lexer."""
    def __init__(self, source: str, filename: Optional[str] = None):
        self.source = source
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.col = 1
        self.length = len(source)

    def _peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        if idx < self.length:
            return self.source[idx]
        return ""

    def _advance(self) -> str:
        if self.pos < self.length:
            ch = self.source[self.pos]
            self.pos += 1
            if ch == "\n":
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            return ch
        return ""

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []

        while self.pos < self.length:
            ch = self._peek()

            # Skip whitespace
            if ch in " \t\r\n":
                self._advance()
                continue

            # Skip single-line comments
            if ch == "/" and self._peek(1) == "/":
                while self.pos < self.length and self._peek() != "\n":
                    self._advance()
                continue

            # Skip block comments
            if ch == "/" and self._peek(1) == "*":
                self._advance()
                self._advance()
                while self.pos < self.length:
                    if self._peek() == "*" and self._peek(1) == "/":
                        self._advance()
                        self._advance()
                        break
                    self._advance()
                continue

            loc = SourceLocation(self.line, self.col, self.filename)

            # Two-character operators
            if ch == "-" and self._peek(1) == ">":
                self._advance(); self._advance()
                tokens.append(Token(TokenType.ARROW, "->", loc))
                continue
            if ch == "=" and self._peek(1) == "=":
                self._advance(); self._advance()
                tokens.append(Token(TokenType.EQUALS, "==", loc))
                continue
            if ch in "!<>" and self._peek(1) == "=":
                self._advance(); self._advance()
                tokens.append(Token(TokenType.OPERATOR, ch + "=", loc))
                continue
            if ch in "<>":
                self._advance()
                tokens.append(Token(TokenType.OPERATOR, ch, loc))
                continue
            if ch == "*" and self._peek(1) == "*":
                self._advance(); self._advance()
                tokens.append(Token(TokenType.CARET, "**", loc))
                continue

            # Single-character tokens
            simple_tokens = {
                ";": TokenType.SEMICOLON,
                ",": TokenType.COMMA,
                ":": TokenType.COLON,
                "(": TokenType.LPAREN,
                ")": TokenType.RPAREN,
                "[": TokenType.LBRACKET,
                "]": TokenType.RBRACKET,
                "{": TokenType.LBRACE,
                "}": TokenType.RBRACE,
                "=": TokenType.ASSIGN,
                "@": TokenType.AT,
                "+": TokenType.PLUS,
                "-": TokenType.MINUS,
                "*": TokenType.STAR,
                "/": TokenType.SLASH,
                "^": TokenType.CARET,
                "%": TokenType.OPERATOR,
            }
            if ch in simple_tokens:
                self._advance()
                tokens.append(Token(simple_tokens[ch], ch, loc))
                continue

            # Strings: "..."
            if ch == '"':
                self._advance()
                start_str = []
                while self.pos < self.length and self._peek() != '"':
                    start_str.append(self._advance())
                if self.pos < self.length:
                    self._advance()  # closing quote
                tokens.append(Token(TokenType.STRING, "".join(start_str), loc))
                continue

            # Numbers
            if ch.isdigit() or (ch == "." and self._peek(1).isdigit()):
                num_chars = []
                while self.pos < self.length and (self._peek().isalnum() or self._peek() in ".eE+-"):
                    # Check for scientific notation or simple number
                    curr = self._peek()
                    if curr in "+-" and num_chars and num_chars[-1] not in "eE":
                        break
                    num_chars.append(self._advance())
                tokens.append(Token(TokenType.NUMBER, "".join(num_chars), loc))
                continue

            # Identifiers
            if ch.isalpha() or ch == "_":
                ident_chars = []
                while self.pos < self.length and (self._peek().isalnum() or self._peek() == "_"):
                    ident_chars.append(self._advance())
                tokens.append(Token(TokenType.IDENTIFIER, "".join(ident_chars), loc))
                continue

            # Unknown character
            bad_ch = self._advance()
            raise QASMError(f"Unexpected character '{bad_ch}'", loc.line, loc.col, self.source)

        tokens.append(Token(TokenType.EOF, "", SourceLocation(self.line, self.col, self.filename)))
        return tokens
