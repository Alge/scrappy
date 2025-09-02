import logging
from lexer import Token, TokenType
from parser import (
    Atom,
    Identifier,
    LiteralPattern,
    Parser,
    BinaryOperation,
    IntegerLiteral,
    FloatLiteral,
    Operator,
    FunctionDefinition,
    PatternClause,
    PatternMatchExpression,
    TextLiteral,
    TypeDefinition,
    TypeExpression,
    TypeVariant,
    UnaryOperation,
    Program,
    ExpressionStatement,
    VariantConstruction,
    WildcardPattern
)

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

       # --- A single identifier ---
       (
           # Code: `my_var`
           [
               Token(token_type=TokenType.IDENTIFIER, lexeme="my_var"),
               Token(token_type=TokenType.END_OF_FILE, lexeme=""),
           ],
           # Expected AST:
           Identifier(name="my_var")
       ),

       # An identifier as part of a larger expression
       (
           # Code: `x + 1`
           [
               Token(token_type=TokenType.IDENTIFIER, lexeme="x"),
               Token(token_type=TokenType.PLUS, lexeme="+"),
               Token(token_type=TokenType.INTEGER, lexeme="1"),
               Token(token_type=TokenType.END_OF_FILE, lexeme=""),
           ],
           # Expected AST:
           BinaryOperation(
               left=Identifier(name="x"),
               operator=Operator.ADD,
               right=IntegerLiteral(1)
           )
       ),

       # pattern_match_expression with infix operator
       (
           # Code: `(| 1 -> 10) + 5`
           [
               Token(token_type=TokenType.START_PARANTHESIS, lexeme="("),
               Token(token_type=TokenType.PIPE, lexeme=""),
               Token(token_type=TokenType.INTEGER, lexeme="1"),
               Token(token_type=TokenType.RIGHT_ARROW, lexeme="->"),
               Token(token_type=TokenType.INTEGER, lexeme="10"),
               Token(token_type=TokenType.END_PARANTHESIS, lexeme=")"),
               Token(token_type=TokenType.PLUS, lexeme="+"),
               Token(token_type=TokenType.INTEGER, lexeme="5"),
               Token(token_type=TokenType.END_OF_FILE, lexeme=""),
           ],
           # Expected AST:
           BinaryOperation(
               left=PatternMatchExpression(
                   clauses=[
                       PatternClause(
                           pattern=LiteralPattern(literal=IntegerLiteral(1)),
                           body=IntegerLiteral(10)
                       )
                   ]
               ),
               operator=Operator.ADD,
               right=IntegerLiteral(5)
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
       ),
       # --- Test Case: A function whose body is a pattern match expression ---
       (
           # Code: `f = | 1 -> "one" | _ -> "many"`
           [
               Token(token_type=TokenType.IDENTIFIER, lexeme="f"),
               Token(token_type=TokenType.EQUALS, lexeme="="),
               Token(token_type=TokenType.PIPE, lexeme="|"),
               Token(token_type=TokenType.INTEGER, lexeme="1"),
               Token(token_type=TokenType.RIGHT_ARROW, lexeme="->"),
               Token(token_type=TokenType.TEXT, lexeme='"one"'),
               Token(token_type=TokenType.PIPE, lexeme="|"),
               Token(token_type=TokenType.UNDERSCORE, lexeme="_"),
               Token(token_type=TokenType.RIGHT_ARROW, lexeme="->"),
               Token(token_type=TokenType.TEXT, lexeme='"many"'),
               Token(token_type=TokenType.END_OF_FILE, lexeme=""),
           ],
           # Expected AST:
           FunctionDefinition(
               name=Identifier("f"),
               body=PatternMatchExpression(
                   clauses=[
                       PatternClause(
                           pattern=LiteralPattern(literal=IntegerLiteral(1)),
                           body=TextLiteral(value='"one"')
                       ),
                       PatternClause(
                           pattern=WildcardPattern(),
                           body=TextLiteral(value='"many"')
                       )
                   ]
               )
           )
       ),
       #  body of a pattern clause is a full expression
       (
           # Code: `f = | 1 -> scoop::vanilla`
           [
               Token(token_type=TokenType.IDENTIFIER, lexeme="f"),
               Token(token_type=TokenType.EQUALS, lexeme="="),
               Token(token_type=TokenType.PIPE, lexeme="|"),
               Token(token_type=TokenType.INTEGER, lexeme="1"),
               Token(token_type=TokenType.RIGHT_ARROW, lexeme="->"),
               Token(token_type=TokenType.IDENTIFIER, lexeme="scoop"),
               Token(token_type=TokenType.DOUBLE_COLON, lexeme="::"),
               Token(token_type=TokenType.IDENTIFIER, lexeme="vanilla"),
               Token(token_type=TokenType.END_OF_FILE, lexeme=""),
           ],
           # Expected AST:
           FunctionDefinition(
               name=Identifier("f"),
               body=PatternMatchExpression(
                   clauses=[
                       PatternClause(
                           pattern=LiteralPattern(literal=IntegerLiteral(1)),
                           body=VariantConstruction(
                               type_name=Identifier("scoop"),
                               variant_name=Identifier("vanilla"),
                               arguments=[]
                           )
                       )
                   ]
               )
           )

       ),

   ]
   )
def test_parse_function(input, expected_output):

    logging.debug(f"Parsing: {input}")

    parser = Parser(tokens=input)

    result = parser.parse_function_definition()
    logging.debug(f"Got resut: {result}")

    logging.debug(f"Expected: {expected_output}")

    assert result == expected_output


@p("input_tokens, expected_ast",
    [
        # Simplest type definition
        (
            # Code: `scoop : #vanilla #chocolate`
            [
                Token(token_type=TokenType.IDENTIFIER, lexeme="scoop"),
                Token(token_type=TokenType.COLON, lexeme=":"),
                Token(token_type=TokenType.ATOM, lexeme="#vanilla"),
                Token(token_type=TokenType.ATOM, lexeme="#chocolate"),
                Token(token_type=TokenType.END_OF_FILE, lexeme=""),
            ],
            # Expected AST:
            TypeDefinition(
                name=Identifier("scoop"),
                body=TypeExpression(
                    variants=[
                        TypeVariant(tag=Atom("vanilla")),
                        TypeVariant(tag=Atom("chocolate")),
                    ]
                )
            )
        ),

        (
            # Code: `result : #ok int | #fail`
            [
                Token(token_type=TokenType.IDENTIFIER, lexeme="result"),
                Token(token_type=TokenType.COLON, lexeme=":"),
                Token(token_type=TokenType.ATOM, lexeme="#ok"),
                Token(token_type=TokenType.IDENTIFIER,
                      lexeme="int"),  # The parameter
                # The optional separator
                Token(token_type=TokenType.PIPE, lexeme="|"),
                Token(token_type=TokenType.ATOM, lexeme="#fail"),
                Token(token_type=TokenType.END_OF_FILE, lexeme=""),
            ],
            # Expected AST:
            TypeDefinition(
                name=Identifier("result"),
                body=TypeExpression(
                    variants=[
                        # The first variant now has a parameter
                        TypeVariant(
                            tag=Atom("ok"),
                            parameter=Identifier(name="int")
                        ),
                        # The second variant has no parameter
                        TypeVariant(
                            tag=Atom("fail")
                        ),
                    ]
                )
            )
        ),
        # ---  A variant with a nested, parenthesized type expression ---
        (
            # Code: `person : #parent (#m | #f)`
            [
                Token(token_type=TokenType.IDENTIFIER, lexeme="person"),
                Token(token_type=TokenType.COLON, lexeme=":"),
                Token(token_type=TokenType.ATOM, lexeme="#parent"),
                Token(token_type=TokenType.START_PARANTHESIS, lexeme="("),
                Token(token_type=TokenType.ATOM, lexeme="#m"),
                Token(token_type=TokenType.PIPE, lexeme="|"),
                Token(token_type=TokenType.ATOM, lexeme="#f"),
                Token(token_type=TokenType.END_PARANTHESIS, lexeme=")"),
                Token(token_type=TokenType.END_OF_FILE, lexeme=""),
            ],
            # Expected AST:
            TypeDefinition(
                name=Identifier("person"),
                body=TypeExpression(
                    variants=[
                        TypeVariant(
                            tag=Atom("parent"),
                            # The parameter is now a complete, nested TypeExpression
                            parameter=TypeExpression(
                                variants=[
                                    TypeVariant(tag=Atom("m")),
                                    TypeVariant(tag=Atom("f")),
                                ]
                            )
                        )
                    ]
                )
            )
        ),

        # A variant with a group FOLLOWED by another variant
        # This test is designed to catch the failure to consume the ')' token.
        (
            # Code: `person : #parent (#m) #cowboy`
            [
                Token(token_type=TokenType.IDENTIFIER, lexeme="person"),
                Token(token_type=TokenType.COLON, lexeme=":"),
                Token(token_type=TokenType.ATOM, lexeme="#parent"),
                Token(token_type=TokenType.START_PARANTHESIS, lexeme="("),
                Token(token_type=TokenType.ATOM, lexeme="#m"),
                Token(token_type=TokenType.END_PARANTHESIS,
                      lexeme=")"),  # The crucial token
                # The token that will cause the crash
                Token(token_type=TokenType.ATOM, lexeme="#cowboy"),
                Token(token_type=TokenType.END_OF_FILE, lexeme=""),
            ],
            # Expected AST:
            TypeDefinition(
                name=Identifier("person"),
                body=TypeExpression(
                    variants=[
                        # First variant with the group
                        TypeVariant(
                            tag=Atom("parent"),
                            parameter=TypeExpression(
                                variants=[TypeVariant(tag=Atom("m"))]
                            )
                        ),
                        # Second variant after the group
                        TypeVariant(
                            tag=Atom("cowboy")
                        )
                    ]
                )
            )
        ),

    ]
   )
def test_parse_type_definition(input_tokens, expected_ast):
    """Tests the parser's ability to handle type definitions."""
    parser = Parser(tokens=input_tokens)

    logging.debug(f"input: {input_tokens}")
    logging.debug(f"expected: {expected_ast}")

    # We are testing the specific method for now. Later, you can test
    # it through the main `parse_program` entry point.
    result_ast = parser.parse_type_definition()
    logging.debug(f"actual: {result_ast}")

    assert result_ast == expected_ast


@p("input_tokens, expected_ast",
    [
        # Test just a single integer literal
        (
            [
                Token(token_type=TokenType.INTEGER, lexeme="42"),
                Token(token_type=TokenType.END_OF_FILE, lexeme=""),
            ],
            Program(
                declarations=[
                    ExpressionStatement(expression=IntegerLiteral(42))
                ]
            )
        ),

        # Test a function definition
        (
            [
                Token(token_type=TokenType.IDENTIFIER, lexeme="f"),
                Token(token_type=TokenType.EQUALS, lexeme="="),
                Token(token_type=TokenType.INTEGER, lexeme="1"),
                Token(token_type=TokenType.END_OF_FILE, lexeme=""),
            ],
            Program(
                declarations=[
                    FunctionDefinition(
                        name=Identifier("f"),
                        body=IntegerLiteral(1)
                    )
                ]
            )
        ),

        # Test function definition and a simple expression after each other
        (
            [
                Token(token_type=TokenType.IDENTIFIER, lexeme="f"),
                Token(token_type=TokenType.EQUALS, lexeme="="),
                Token(token_type=TokenType.INTEGER, lexeme="1"),
                Token(token_type=TokenType.SEMI_COLON, lexeme=";"),
                Token(token_type=TokenType.INTEGER, lexeme="5"),
                Token(token_type=TokenType.END_OF_FILE, lexeme=""),
            ],
            Program(
                declarations=[
                    FunctionDefinition(
                        name=Identifier("f"),
                        body=IntegerLiteral(1)
                    ),
                    ExpressionStatement(
                        expression=IntegerLiteral(5)
                    )
                ]
            )
        ),

        # Test a few semi colons after each other
        (
            [
                Token(token_type=TokenType.INTEGER, lexeme="1"),
                Token(token_type=TokenType.SEMI_COLON, lexeme=";"),
                Token(token_type=TokenType.SEMI_COLON, lexeme=";"),
                Token(token_type=TokenType.INTEGER, lexeme="2"),
                Token(token_type=TokenType.END_OF_FILE, lexeme=""),
            ],
            Program(
                declarations=[
                    ExpressionStatement(expression=IntegerLiteral(1)),
                    ExpressionStatement(expression=IntegerLiteral(2))
                ]
            )
        ),
    ]
   )
def test_parse_program(input_tokens, expected_ast):
    """
    Tests the parser's ability to handle a full program with
    different statement types.
    """
    logging.debug(f"Parsing Program: {input_tokens}")

    parser = Parser(tokens=input_tokens)
    result_ast = parser.parse_program()

    logging.debug(f"Got result: {result_ast}")
    logging.debug(f"Expected:   {expected_ast}")

    assert result_ast == expected_ast


@p("input_tokens, expected_ast",
    [
        # --- Simple variant construction with no arguments ---
        (
            # Code: `scoop::chocolate`
            [
                Token(token_type=TokenType.IDENTIFIER, lexeme="scoop"),
                Token(token_type=TokenType.DOUBLE_COLON, lexeme="::"),
                Token(token_type=TokenType.IDENTIFIER, lexeme="chocolate"),
                Token(token_type=TokenType.END_OF_FILE, lexeme=""),
            ],
            # Expected AST:
            VariantConstruction(
                type_name=Identifier("scoop"),
                variant_name=Identifier("chocolate"),
                arguments=[]  # No arguments in this case
            )
        ),

        # Construction with a single, simple argument ---
        (
            # Code: `point::d2 1`
            [
                Token(token_type=TokenType.IDENTIFIER, lexeme="point"),
                Token(token_type=TokenType.DOUBLE_COLON, lexeme="::"),
                Token(token_type=TokenType.IDENTIFIER, lexeme="d2"),
                Token(token_type=TokenType.INTEGER, lexeme="1"),
                Token(token_type=TokenType.END_OF_FILE, lexeme=""),
            ],
            # Expected AST:
            VariantConstruction(
                type_name=Identifier("point"),
                variant_name=Identifier("d2"),
                arguments=[
                    IntegerLiteral(1)
                ]
            )
        ),

        # Construction with a identifier as a argument
        (
            # Code: `point::d2 x`
            [
                Token(token_type=TokenType.IDENTIFIER, lexeme="point"),
                Token(token_type=TokenType.DOUBLE_COLON, lexeme="::"),
                Token(token_type=TokenType.IDENTIFIER, lexeme="d2"),
                Token(token_type=TokenType.IDENTIFIER, lexeme="x"),
                Token(token_type=TokenType.END_OF_FILE, lexeme=""),
            ],
            # Expected AST:
            VariantConstruction(
                type_name=Identifier("point"),
                variant_name=Identifier("d2"),
                arguments=[
                    Identifier("x")
                ]
            )
        ),

        # Construction with multiple, mixed arguments ---
        (
            # Code: `person::full "Max" 30`
            [
                Token(token_type=TokenType.IDENTIFIER, lexeme="person"),
                Token(token_type=TokenType.DOUBLE_COLON, lexeme="::"),
                Token(token_type=TokenType.IDENTIFIER, lexeme="full"),
                Token(token_type=TokenType.TEXT, lexeme='"Max"'),
                Token(token_type=TokenType.INTEGER, lexeme="30"),
                Token(token_type=TokenType.END_OF_FILE, lexeme=""),
            ],
            # Expected AST:
            VariantConstruction(
                type_name=Identifier("person"),
                variant_name=Identifier("full"),
                arguments=[
                    TextLiteral('"Max"'),
                    IntegerLiteral(30)
                ]
            )
        ),

        # Testing for correct high precedence - --
        # This is the most important one. It proves the argument loop stops correctly.
        (
            # Code: `point::d2 1 + 2`
            # Should be parsed as `(point::d2 1) + 2`
            [
                Token(token_type=TokenType.IDENTIFIER, lexeme="point"),
                Token(token_type=TokenType.DOUBLE_COLON, lexeme="::"),
                Token(token_type=TokenType.IDENTIFIER, lexeme="d2"),
                Token(token_type=TokenType.INTEGER, lexeme="1"),
                Token(token_type=TokenType.PLUS, lexeme="+"),
                Token(token_type=TokenType.INTEGER, lexeme="2"),
                Token(token_type=TokenType.END_OF_FILE, lexeme=""),
            ],
            # Expected AST: The root is a BinaryOperation!
            BinaryOperation(
                left=VariantConstruction(
                    type_name=Identifier("point"),
                    variant_name=Identifier("d2"),
                    arguments=[IntegerLiteral(1)]
                ),
                operator=Operator.ADD,
                right=IntegerLiteral(2)
            )
        ),

        # Variant construction where one argument is a parenthesize expression
        (
            # Code: `point::d2 (1 + 2) 3 `
            [
                Token(token_type=TokenType.IDENTIFIER, lexeme="point"),
                Token(token_type=TokenType.DOUBLE_COLON, lexeme="::"),
                Token(token_type=TokenType.IDENTIFIER, lexeme="d2"),
                Token(token_type=TokenType.START_PARANTHESIS, lexeme="("),
                Token(token_type=TokenType.INTEGER, lexeme="1"),
                Token(token_type=TokenType.PLUS, lexeme="+"),
                Token(token_type=TokenType.INTEGER, lexeme="2"),
                Token(token_type=TokenType.END_PARANTHESIS, lexeme=")"),
                Token(token_type=TokenType.INTEGER, lexeme="3"),
                Token(token_type=TokenType.END_OF_FILE, lexeme=""),
            ],

            VariantConstruction(
                type_name=Identifier("point"),
                variant_name=Identifier("d2"),
                arguments=[
                    BinaryOperation(
                        left=IntegerLiteral(1),
                        operator=Operator.ADD,
                        right=IntegerLiteral(2)
                    ),
                    IntegerLiteral(3)
                ]
            )
        ),


    ]
   )
def test_parse_variant_construction(input_tokens, expected_ast):
    """Tests the parser's ability to handle variant construction expressions."""
    logging.debug(f"Input: {input_tokens}")
    logging.debug(f"Expected: {expected_ast}")
    parser = Parser(tokens=input_tokens)
    # A variant construction is an expression
    result_ast = parser.parse_expression()
    logging.debug(f"Actual:   {result_ast}")

    assert result_ast == expected_ast
