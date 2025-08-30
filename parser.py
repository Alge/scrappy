from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Iterable, Iterator, List
from lexer import Token, TokenType

import logging


class Operator(str, Enum):
    MULTIPLY = "*"
    DIVIDE = "/"
    ADD = "+"
    SUBTRACT = "-"


# Used for calculating the precendence of tokens
OPERATOR_PRECEDENCE: MappingProxyType[TokenType, int] = MappingProxyType(
    {
        TokenType.PLUS: 10,
        TokenType.MINUS: 10,
        TokenType.MULTIPLY: 20,
        TokenType.SLASH: 20,
    }
)


@dataclass
class Statement():
    ...


@dataclass
class Expression():
    ...


@dataclass
class Identifier():
    name: str


@dataclass
class UnaryOperation(Expression):
    right: Expression
    operator: Token


@dataclass
class BinaryOperation(Expression):
    left: Expression
    right: Expression
    operator: Operator


@dataclass
class FunctionDefinition(Statement):
    name: Identifier
    body: Expression


@dataclass
class Literal(Expression):
    pass


@dataclass
class Program():
    declarations: List[Statement]


@dataclass
class IntegerLiteral(Literal):
    value: int


@dataclass
class FloatLiteral(Literal):
    value: float


@dataclass
class TextLiteral(Literal):
    value: str


@dataclass
class InterpolatedTextLiteral(Literal):
    value: str


@dataclass
class HexLiteral(Literal):
    value: str  # TODO, maybe store as int?


# @dataclass
# class Identifier(Literal):
#    name = str


@dataclass
class HashReference(Statement):
    hash: str


class Parser:
    _current_token: Token
    _next_token: Token
    _token_generator: Iterator[Token]

    def __init__(self, tokens: Iterable[Token]):
        # Create the generator from the iterable.
        self._token_generator = tokens.__iter__()

        self._eof_token = Token(TokenType.END_OF_FILE, '', 0)

        # Initialize the buffer slots to a known, safe state BEFORE they are used.
        self._current_token = self._eof_token
        self._next_token = self._eof_token

        # Load the first tokens into the buffers
        self.advance()
        self.advance()

    @staticmethod
    def get_operator_precedence(token_type: TokenType) -> int:
        return OPERATOR_PRECEDENCE.get(token_type, 0)

    def advance(self) -> None:
        self._current_token = self._next_token
        try:
            self._next_token = self._token_generator.__next__()

        except StopIteration:
            # This causes a duplicate end of file token to
            # be placed in the buffer, but it should not matter
            self._next_token = Token(
                token_type=TokenType.END_OF_FILE, lexeme="", line=0
            )

    @property
    def next_token(self) -> Token:
        return self._next_token

    @property
    def current(self):
        return self._current_token

    def parse_program(self) -> Program:

        statements: List[Statement] = []

        # Loop through all tokens
        while self._current_token.token_type != TokenType.END_OF_FILE:
            # Parse the next statement

            statement = self.parse_statement()
            logging.debug("Found a new statement")
            logging.debug(statement)
            statements.append(statement)

            # Statements can optionally end with a semi colon, let's
            # skip them
            while self.current.token_type == TokenType.SEMI_COLON:
                logging.debug("Skipping a semicolon")
                self.advance()

        return Program(statements)

    def parse_statement(self) -> Statement:

        # x = <Expression>
        if self.current.token_type == TokenType.IDENTIFIER\
                and self.next_token.token_type == TokenType.EQUALS:
            return self.parse_function_definition()

        raise Exception("Failed to parse a statement")

    def parse_function_definition(self) -> Statement:
        # name = <Expression>

        name = self.current.lexeme

        self.advance()

        assert self.current.token_type == TokenType.EQUALS, "Second token in function needs to be a equals sign"

        self.advance()

        body = self.parse_expression()

        return FunctionDefinition(name=Identifier(name=name), body=body)

    def parse_prefix(self) -> Expression:

        token = self.current
        self.advance()

        match token.token_type:
            case TokenType.INTEGER:
                return IntegerLiteral(int(token.lexeme))
            case TokenType.FLOAT:
                return FloatLiteral(float(token.lexeme))
            case TokenType.TEXT:
                # Strip quotation characters
                return TextLiteral(token.lexeme[1:-1])
            case TokenType.START_PARANTHESIS:
                # Here we have a nested expression.
                nested_expression = self.parse_expression()
                # The fetching of the expression should
                # make sure we have a new fresh token ready to read
                assert self.current.token_type == TokenType.END_PARANTHESIS
                self.advance()
                return nested_expression

        raise Exception("Failed parsing prefix")

    def parse_expression(self, precedence: int = 0) -> Expression:
        # Parse a expression. something like "5 + 1" or
        # (123 * 3) / 123
        # Note that each term (left and right) are both expressions,
        # but one, both or neither can also be literals (literals are also Expressions!)!

        left_term: Expression = self.parse_prefix()

        while precedence < self.get_operator_precedence(self.current.token_type):
            # If the current token has higher precedence than us, we need to
            # parse that expression first!

            operator_token = self.current

            operator = self.parse_operator()

            right_term = self.parse_expression(
                precedence=self.get_operator_precedence(
                    operator_token.token_type
                )
            )

            # Here we need to wrap the old left term with a new expression,
            # where the right term is the new right term
            left_term = BinaryOperation(
                left=left_term,
                operator=operator,
                right=right_term
            )

        return left_term

    def parse_operator(self) -> Operator:
        token = self.current

        self.advance()

        match token.token_type:
            case TokenType.PLUS:
                return Operator.ADD
            case TokenType.MINUS:
                return Operator.SUBTRACT
            case TokenType.MULTIPLY:
                return Operator.MULTIPLY
            case TokenType.SLASH:
                return Operator.DIVIDE

        raise Exception(
            f"Failed to parse operator, {token.token_type} is not a valid operator!")
