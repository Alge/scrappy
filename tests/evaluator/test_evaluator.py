# tests/evaluator/test_evaluator.py

from values import Closure  # Your new value class
from scrapscript_ast import FunctionDefinitionStatement, Identifier
import logging
import pytest
from exceptions import ScrapNameError, ScrapTypeError
from scope import Scope
from scrapscript_ast import (
    Expression,
    Identifier,
    IntegerLiteral,
    FloatLiteral,
    BinaryOperation,
    TextLiteral,
    UnaryOperation,
)
from enums import (
    Operator
)
# We will create these in the next step
from evaluator import evaluate_node
from values import FloatValue, IntegerValue, Value

p = pytest.mark.parametrize


@p("input_ast_node, expected_value_object",
   [
       # The simplest expression, an integer literal
       (
           IntegerLiteral(value=42),
           IntegerValue(value=42)
       ),

       # A simple float literal
       (
           FloatLiteral(value=3.14),
           FloatValue(value=3.14)
       ),

       # Simple binary operation on integers
       (
           BinaryOperation(
               left=IntegerLiteral(10),
               operator=Operator.ADD,
               right=IntegerLiteral(5)
           ),
           IntegerValue(value=15)
       ),
       (
           BinaryOperation(
               left=IntegerLiteral(10),
               operator=Operator.SUBTRACT,
               right=IntegerLiteral(5)
           ),
           IntegerValue(value=5)
       ),
       (
           BinaryOperation(
               left=IntegerLiteral(10),
               operator=Operator.MULTIPLY,
               right=IntegerLiteral(5)
           ),
           IntegerValue(value=50)
       ),
       (
           BinaryOperation(
               left=IntegerLiteral(10),
               operator=Operator.DIVIDE,
               right=IntegerLiteral(5)
           ),
           IntegerValue(value=2)
       ),
       (  # Division should floor the value
           BinaryOperation(
               left=IntegerLiteral(7),
               operator=Operator.DIVIDE,
               right=IntegerLiteral(2)
           ),
           IntegerValue(value=3)
       ),

       # Simple binary operation on floats
       (
           BinaryOperation(
               left=FloatLiteral(1.5),
               operator=Operator.ADD,
               right=FloatLiteral(5)
           ),
           FloatValue(value=6.5)
       ),
       (
           BinaryOperation(
               left=FloatLiteral(24.3),
               operator=Operator.SUBTRACT,
               right=FloatLiteral(-1.0)
           ),
           FloatValue(value=25.3)
       ),
       (
           BinaryOperation(
               left=FloatLiteral(1.1),
               operator=Operator.MULTIPLY,
               right=FloatLiteral(5)
           ),
           FloatValue(value=5.5)
       ),
       (
           BinaryOperation(
               left=FloatLiteral(10),
               operator=Operator.DIVIDE,
               right=FloatLiteral(-4)
           ),
           FloatValue(value=-2.5)
       ),

       # --- Test Case: Simple unary negation of an integer ---
       (
           UnaryOperation(
               operator=Operator.SUBTRACT,  # The '-' token is parsed as SUBTRACT
               expression=IntegerLiteral(value=3)
           ),
           IntegerValue(value=-3)
       ),

       # --- Test Case: Simple unary negation of a float ---
       (
           UnaryOperation(
               operator=Operator.SUBTRACT,
               expression=FloatLiteral(value=1.5)
           ),
           FloatValue(value=-1.5)
       ),

       # --- Test Case: Unary negation of a complex expression ---
       # This tests that the inner expression is evaluated first.
       (
           UnaryOperation(
               operator=Operator.SUBTRACT,
               expression=BinaryOperation(
                   left=IntegerLiteral(10),
                   operator=Operator.MULTIPLY,
                   right=IntegerLiteral(2)
               )
           ),
           IntegerValue(value=-20)
       ),
   ]
   )
def test_evaluate_expression(input_ast_node: Expression, expected_value_object: Value):
    """
    Tests that the evaluator can correctly evaluate a single expression node.
    """

    logging.debug(f"Input: {input_ast_node}")
    logging.debug(f"expected: {expected_value_object}")

    result_value = evaluate_node(
        node=input_ast_node, scope=Scope()
    )

    logging.debug(f"actual: {result_value}")

    assert result_value == expected_value_object


@p("left, operator, right", [
    (IntegerLiteral(1), Operator.ADD, FloatLiteral(1.2)),
    (IntegerLiteral(1), Operator.SUBTRACT, FloatLiteral(1.2)),
    (IntegerLiteral(1), Operator.MULTIPLY, FloatLiteral(1.2)),
    (IntegerLiteral(1), Operator.DIVIDE, FloatLiteral(1.2)),
])
def test_math_on_float_and_int_raises_errors(left, operator, right):
    """
    Tests that applying the unary '-' operator to a non-numeric type
    correctly raises a ScrapTypeError.
    """
    ast_node = BinaryOperation(
        left=left,
        operator=operator,
        right=right
    )

    with pytest.raises(ScrapTypeError) as e:
        evaluate_node(node=ast_node, scope=Scope())

    # Try it the other way around!

    ast_node = BinaryOperation(
        left=right,
        operator=operator,
        right=left
    )

    with pytest.raises(ScrapTypeError) as e:
        evaluate_node(node=ast_node, scope=Scope())


def test_evaluate_unary_negation_on_invalid_type_raises_error():
    """
    Tests that applying the unary '-' operator to a non-numeric type
    correctly raises a ScrapTypeError.
    """
    ast_node = UnaryOperation(
        operator=Operator.SUBTRACT,
        expression=TextLiteral(value='"hello"')
    )

    with pytest.raises(ScrapTypeError) as e:
        evaluate_node(node=ast_node, scope=Scope())


def test_evaluate_identifier_success():
    """
    Tests that the evaluator can correctly look up the value of a
    variable from the scope.
    """
    ast_node = Identifier(name="x")

    scope = Scope()
    scope.put(name="x", value=IntegerValue(value=99))

    expected_value = IntegerValue(value=99)

    result_value = evaluate_node(node=ast_node, scope=scope)

    assert result_value == expected_value


def test_evaluate_undefined_identifier_raises_error():
    """
    Tests that evaluating an undefined variable correctly raises a ScrapNameError.
    """
    ast_node = Identifier(name="undefined_var")

    scope = Scope()

    with pytest.raises(ScrapNameError) as excinfo:
        evaluate_node(node=ast_node, scope=scope)


# In your test_evaluator.py file


def test_evaluate_function_definition_creates_closure():
    """
    Tests that evaluating a FunctionDefinition creates a Closure
    and binds it in the current scope.
    """
    # The AST for `f = x -> x`
    ast_node = FunctionDefinitionStatement(
        name="f",
        # NOTE: Your parser will eventually create a real Function node here.
        # For now, we can just use a placeholder for the body.
        body=Identifier(name="x")  # A simplified body for now
    )

    # Setup a scope to evaluate in.
    scope = Scope()

    # ACTION: Evaluate the definition statement.
    evaluate_node(node=ast_node, scope=scope)

    # ASSERTIONS:
    # a) Check that the name 'f' now exists in the scope.
    assert "f" in scope.variables

    # b) Check that the value is a Closure.
    value = scope.variables["f"]
    assert isinstance(value, Closure)

    # c) Check that the closure has captured the correct body and scope.
    assert value.body == Identifier(name="x")
    # It should capture the scope it was defined in.
    assert value.scope is scope
