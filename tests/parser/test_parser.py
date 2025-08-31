import logging
from lexer import Token, TokenType
from parser import Identifier, Parser, BinaryOperation, IntegerLiteral, FloatLiteral, Operator, FunctionDefinition, TextLiteral, UnaryOperation

from pytest import mark

p = mark.parametrize


@p("input, expected_output",
   [
       (
           [
               Token(token_type=TokenType.INTEGER, lexeme="1"),
               Token(token_type=TokenType.PLUS, lexeme="+"),
               Token(token_type=TokenType.INTEGER, lexeme="2"),
           ],
           BinaryOperation(
               left=IntegerLiteral(1),
               operator=Operator.ADD,
               right=IntegerLiteral(2),
           )
       ),
       (  # Multiply has precedence over addition
           [
               Token(token_type=TokenType.INTEGER, lexeme="1"),
               Token(token_type=TokenType.PLUS, lexeme="+"),
               Token(token_type=TokenType.INTEGER, lexeme="2"),
               Token(token_type=TokenType.MULTIPLY, lexeme="*"),
               Token(token_type=TokenType.INTEGER, lexeme="3"),
           ],
           BinaryOperation(
               left=IntegerLiteral(1),
               operator=Operator.ADD,
               right=BinaryOperation(
                   left=IntegerLiteral(2),
                   operator=Operator.MULTIPLY,
                   right=IntegerLiteral(3),
               )
           )
       ),
       (  # This works with floats too!
           [
               Token(token_type=TokenType.FLOAT, lexeme="1.23"),
               Token(token_type=TokenType.SLASH, lexeme="/"),
               Token(token_type=TokenType.FLOAT, lexeme="2.123"),
           ],
           BinaryOperation(
               left=FloatLiteral(1.23),
               operator=Operator.DIVIDE,
               right=FloatLiteral(2.123),
           )
       ),
       (  # Paranthesis can be used to increase precedence of a block
           [
               Token(token_type=TokenType.START_PARANTHESIS, lexeme="("),
               Token(token_type=TokenType.INTEGER, lexeme="1"),
               Token(token_type=TokenType.PLUS, lexeme="+"),
               Token(token_type=TokenType.INTEGER, lexeme="2"),
               Token(token_type=TokenType.END_PARANTHESIS, lexeme=")"),
               Token(token_type=TokenType.MULTIPLY, lexeme="*"),
               Token(token_type=TokenType.INTEGER, lexeme="3"),
           ],
           BinaryOperation(
               left=BinaryOperation(
                   left=IntegerLiteral(1),
                   operator=Operator.ADD,
                   right=IntegerLiteral(2)
               ),
               operator=Operator.MULTIPLY,
               right=IntegerLiteral(3),
           )
       ),

       (  # Unary expressions should be supported "-1 * 3"
           [
               Token(token_type=TokenType.MINUS, lexeme="-"),
               Token(token_type=TokenType.INTEGER, lexeme="1"),
               Token(token_type=TokenType.MULTIPLY, lexeme="*"),
               Token(token_type=TokenType.INTEGER, lexeme="3"),
           ],
           BinaryOperation(
               left=UnaryOperation(
                   expression=IntegerLiteral(1),
                   operator=Operator.SUBTRACT,
               ),
               operator=Operator.MULTIPLY,
               right=IntegerLiteral(3),
           )
       ),
       (  # Unary expressions have precedence over paranthesis "-(1 * 3)"
           [
               Token(token_type=TokenType.MINUS, lexeme="-"),
               Token(token_type=TokenType.START_PARANTHESIS, lexeme="("),
               Token(token_type=TokenType.INTEGER, lexeme="1"),
               Token(token_type=TokenType.MULTIPLY, lexeme="*"),
               Token(token_type=TokenType.INTEGER, lexeme="3"),
               Token(token_type=TokenType.END_PARANTHESIS, lexeme=")"),
           ],
           UnaryOperation(
               operator=Operator.SUBTRACT,
               expression=BinaryOperation(
                   left=IntegerLiteral(1),
                   operator=Operator.MULTIPLY,
                   right=IntegerLiteral(3),
               )
           )
       ),
   ]
   )
def test_parse_expression(input, expected_output):

    logging.debug(f"Parsing: {input}")

    parser = Parser(tokens=input)

    result = parser.parse_expression()
    logging.debug(f"Got resut: {result}")

    logging.debug(f"Expected: {expected_output}")

    assert result == expected_output


@p("input, expected_output",
   [
       (
           [
               Token(token_type=TokenType.IDENTIFIER, lexeme="hello"),
               Token(token_type=TokenType.EQUALS, lexeme=""),
               Token(token_type=TokenType.TEXT, lexeme="Hello world!"),
           ],

           FunctionDefinition(
               name=Identifier("hello"),
               body=TextLiteral("Hello world!"),
           )
       )
   ]
   )
def test_parse_function(input, expected_output):

    logging.debug(f"Parsing: {input}")

    parser = Parser(tokens=input)

    result = parser.parse_function_definition()
    logging.debug(f"Got resut: {result}")

    logging.debug(f"Expected: {expected_output}")

    assert result == expected_output
