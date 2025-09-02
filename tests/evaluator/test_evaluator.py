# tests/evaluator/test_evaluator.py

import pytest
from parser import (
    Expression,
    IntegerLiteral,
    FloatLiteral,
    BinaryOperation,
    Operator
)
# We will create these in the next step
from evaluator import Scope, evaluate_expression, FloatValue, IntegerValue, Value

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

       # A simple binary operation
       (
           BinaryOperation(
               left=IntegerLiteral(10),
               operator=Operator.ADD,
               right=IntegerLiteral(5)
           ),
           IntegerValue(value=15)
       ),
   ]
   )
def test_evaluate_expression(input_ast_node: Expression, expected_value_object: Value):
    """
    Tests that the evaluator can correctly evaluate a single expression node.
    """

    result_value = evaluate_expression(
        expression=input_ast_node, scope=Scope()
    )

    # 3. Assert that the resulting value object is correct
    assert result_value == expected_value_object
