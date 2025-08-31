

from enum import Enum
import logging
import re
import sys
from typing import Dict, Iterable, List, Set


class InvalidTokenException(Exception):
    line_number: int
    input_string: str

    def __init__(self, line_number: int, input_string: str):
        self.line_number = line_number
        self.input_string = input_string

    def __repr__(self):
        return f"Invalid instruction on line {self.line_number}, input: '{self.input_string}'"


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
    ATOM = "#ATOM"
    INTERPOLATED_TEXT = "INTERPOLATED_TEXT"
    TEXT = "TEXT"
    SLASH = "/"
    MULTIPLY = "*"
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
    COMMENT = "-- Comment"
    EXCLAMATION_MARK = "!"


lexeme_mapper: Dict[str, TokenType] = {
    r"--.*": TokenType.COMMENT,
    r"\s+": TokenType.WHITE_SPACE,
    r"\|": TokenType.PIPE,
    r";": TokenType.SEMI_COLON,
    r":": TokenType.COLON,
    r"[a-zA-Z]+": TokenType.IDENTIFIER,
    r"#[a-zA-Z]+": TokenType.ATOM,
    r'"([^`]*`[^`]*`)+[^`]*"': TokenType.INTERPOLATED_TEXT,
    r'"[^"]*"': TokenType.TEXT,
    r"\->": TokenType.RIGHT_ARROW,
    r"=": TokenType.EQUALS,
    r"\+\+": TokenType.DOUBLE_PLUS,
    r"\+<": TokenType.APPEND,
    r"\+": TokenType.PLUS,
    r"-": TokenType.MINUS,
    r"/": TokenType.SLASH,
    r"\*": TokenType.MULTIPLY,
    r">>": TokenType.PIPE_FORWARD,
    r">": TokenType.GREATER_THAN,
    r"<": TokenType.LESS_THAN,
    r"\(": TokenType.START_PARANTHESIS,
    r"\)": TokenType.END_PARANTHESIS,
    r"\d+\.\d+": TokenType.FLOAT,
    r"\d+": TokenType.INTEGER,
    r"\{": TokenType.START_CURLY_BRACKETS,
    r"\}": TokenType.END_CURLY_BRACKETS,
    r"\.": TokenType.DOT,
    r",": TokenType.COMMA,
    r"~[0-9a-fA-F]+": TokenType.HEXADECIMAL,
    r"~~(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?": TokenType.BASE64,
    r"_": TokenType.UNDERSCORE,
    r"!": TokenType.EXCLAMATION_MARK,
}

ignored_tokens: Set[TokenType] = {TokenType.COMMENT, TokenType.WHITE_SPACE}


class Token:
    token_type: TokenType
    lexeme: str
    line: int

    def __init__(self, token_type: TokenType, lexeme: str, line: int = 0):
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


def extract_tokens(lines: Iterable[str]) -> List[Token]:
    tokens: List[Token] = []
    current_line_number = 0

    for line in lines:
        current_line_offset = 0
        current_line_number += 1
        while len(line) != 0:
            for pattern, token_type in lexeme_mapper.items():
                match = re.match(pattern, line)

                if match:
                    lexeme = match.group(0)
                    token = Token(token_type=token_type,
                                  lexeme=lexeme, line=current_line_number)

                    if token.token_type not in ignored_tokens:
                        tokens.append(token)
                    current_line_offset += len(token.lexeme)
                    line = line[len(token.lexeme):]
                    break

            else:
                raise InvalidTokenException(
                    line_number=current_line_number, input_string=line)

    tokens.append(Token(token_type=TokenType.END_OF_FILE,
                  lexeme="", line=current_line_number))

    return tokens
