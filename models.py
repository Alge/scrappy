
from enum import Enum
from typing import Any


class TokenType(str, Enum):
    SEMI_COLON = "SEMI_COLON"
    WHITE_SPACE = "WHITE_SPACE"
    RIGHT_ARROW = "->"
    COLON = ":"
    END_OF_FILE = "EOF"
    PIPE = "|"
    IDENTIFIER = "IDENTIFIER"
    PLUS = "+"
    DOUBLE_PLUS = "++"
    MINUS = "-"
    EQUALS = "="
    ATOM = "ATOM"
    INTERPOLATED_TEXT = "INTERPOLATED_TEXT"
    TEXT = "TEXT"
    SLASH = "/"
    GREATER_THAN = ">"
    LESS_THAN = "<"
    PIPE_FORWARD = ">>"
    START_PARANTHESIS = "("
    END_PARANTHESIS = ")"
    FLOAT = "123.456"
    INTEGER = "123"
    START_CURLY_BRACKETS = "{"
    END_CURLY_BRACKETS = "}"
    DOT = "."
    COMMA = ","
    APPEND = "+<"
    HEXADECIMAL = "~f3123"
    BASE64 = "~~abcd123="
    UNDERSCORE = "_"
    COMMENT = "-- COMMENT"


class Token:
    token_type: TokenType
    lexeme: str
    line: int

    def __init__(self, token_type: TokenType, lexeme: str, line: int):
        self.token_type = token_type
        self.lexeme = lexeme
        self.line = line

    def __repr__(self):
        # Escape newline characters in the lexeme for a clean, single-line representation.
        # It's also good practice to escape tabs and carriage returns.
        escaped_lexeme = self.lexeme.replace('\n', r'\n') \
            .replace('\t', r'\t') \
            .replace('\r', r'\r')

        return f"Token [{self.token_type}], lexeme: '{escaped_lexeme}', line: {self.line}"
