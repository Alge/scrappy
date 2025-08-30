

import logging
import re
import sys
from typing import Dict, Iterable, List

from models import Token, TokenType


class InvalidTokenException(Exception):
    line_number: int
    input_string: str

    def __init__(self, line_number: int, input_string: str):
        self.line_number = line_number
        self.input_string = input_string

    def __repr__(self):
        return f"Invalid instruction on line {self.line_number}, input: '{self.input_string}'"


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

}


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
