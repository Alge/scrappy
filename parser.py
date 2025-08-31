from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Dict, Iterable, Iterator, List
from lexer import Token, TokenType

import logging


class Operator(str, Enum):
    MULTIPLY = "*"
    DIVIDE = "/"
    ADD = "+"
    SUBTRACT = "-"


class PrecedencePosition(str, Enum):
    PREFIX = "PREFIX"
    INFIX = "INFIX"


# Used for calculating the precendence of tokens
OPERATOR_PRECEDENCE: MappingProxyType[PrecedencePosition, MappingProxyType[TokenType, int]] = MappingProxyType(
    {
        PrecedencePosition.INFIX: MappingProxyType({
            TokenType.PLUS: 10,
            TokenType.MINUS: 10,
            TokenType.MULTIPLY: 20,
            TokenType.SLASH: 20,
        }),
        PrecedencePosition.PREFIX: MappingProxyType({
            TokenType.MINUS: 100,
        })
    }
)


@dataclass
class Expression():
    ...


@dataclass
class Identifier():
    name: str

    def __repr__(self) -> str:
        # Represents an identifier just by its name for clarity.
        return self.name


@dataclass
class UnaryOperation(Expression):
    expression: Expression
    operator: Operator

    def __repr__(self) -> str:
        # Example: (- 5)
        return f"({self.operator} {self.expression})"


@dataclass
class BinaryOperation(Expression):
    left: Expression
    right: Expression
    operator: Operator

    def __repr__(self) -> str:
        # Example: (+ 1 (* 2 3))
        return f"({self.operator.value} {self.left} {self.right})"


@dataclass
class Literal(Expression):
    pass


@dataclass
class IntegerLiteral(Literal):
    value: int

    def __repr__(self) -> str:
        # Represents a number literal simply by its value.
        return str(self.value)


@dataclass
class FloatLiteral(Literal):
    value: float

    def __repr__(self) -> str:
        # Represents a number literal simply by its value.
        return str(self.value)


@dataclass
class TextLiteral(Literal):
    value: str

    def __repr__(self) -> str:
        # Represents a number literal simply by its value.
        return self.value


@dataclass
class InterpolatedTextLiteral(Literal):
    value: str

    def __repr__(self) -> str:
        # Use backticks to distinguish from normal strings
        return f'`{self.value}`'


@dataclass
class HexLiteral(Literal):
    value: str  # TODO, maybe store as int?

    def __repr__(self) -> str:
        return f"Hex({self.value})"


@dataclass
class HashReference(Literal):
    hash: str

    def __repr__(self) -> str:
        return self.hash


@dataclass
class Statement():
    ...


@dataclass
class ExpressionStatement(Statement):
    expression: Expression


@dataclass
class FunctionDefinition(Statement):
    name: Identifier
    body: Expression


@dataclass
class Program():
    declarations: List[Statement]


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
    def get_operator_precedence(token_type: TokenType, position: PrecedencePosition) -> int:
        table = OPERATOR_PRECEDENCE.get(position)
        if table is None:
            raise Exception(f"Can't find precedance table for {position}")

        return table.get(token_type, 0)

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
                return TextLiteral(token.lexeme)
            case TokenType.START_PARANTHESIS:
                # Here we have a nested expression.
                nested_expression = self.parse_expression()
                # The fetching of the expression should
                # make sure we have a new fresh token ready to read
                assert self.current.token_type == TokenType.END_PARANTHESIS
                self.advance()
                return nested_expression
            case TokenType.MINUS:
                # Unary operation "-3"
                return UnaryOperation(
                    operator=Operator.SUBTRACT,
                    expression=self.parse_expression(
                        precedence=self.get_operator_precedence(
                            token_type=TokenType.MINUS,
                            position=PrecedencePosition.PREFIX
                        )
                    )
                )

        raise Exception("Failed parsing prefix")

    def parse_expression(self, precedence: int = 0) -> Expression:
        # Parse a expression. something like "5 + 1" or
        # (123 * 3) / 123
        # Note that each term (left and right) are both expressions,
        # but one, both or neither can also be literals (literals are also Expressions!)!

        left_term: Expression = self.parse_prefix()

        while precedence < self.get_operator_precedence(self.current.token_type, position=PrecedencePosition.INFIX):
            # We have lower precedance than the next expression,
            # parse that expression first!

            operator_token = self.current

            operator = self.parse_operator()

            right_term = self.parse_expression(
                precedence=self.get_operator_precedence(
                    operator_token.token_type,
                    position=PrecedencePosition.INFIX
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
