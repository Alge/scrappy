

import logging
from exceptions import ScrapEvalError, ScrapTypeError
from scope import Scope
from values import *
from scrapscript_ast import *
from enums import Operator


def evaluate_program(program: Program):

    scope = Scope()

    return_value: Value = HoleValue()

    for n, statement in enumerate(reversed(program.declarations)):
        logging.debug(f"evaluating statement #{n}, {statement}")

        match statement:
            case ExpressionStatement():
                logging.debug(
                    f"Running expression statement ({type(statement.expression)}): {statement.expression}")
                return_value = evaluate_node(statement.expression, scope=scope)
                logging.debug(f"Got return value: {return_value}")
            case FunctionDefinitionStatement():
                name = statement.name
                body = evaluate_node(statement.body, scope=scope)

                logging.debug(f"Storing in scope: {name} = {body}")
                # Store returned value!
                scope.put(name, body)
                return_value = HoleValue()

            # case TypeDefinitionStatment():
            #     raise NotImplementedError
            case _:
                raise ScrapEvalError(
                    f"Unknown statement type: {type(statement)}")

    return return_value


def evaluate_node(node: ASTNode, scope: Scope = Scope()) -> Value:

    logging.debug(f"Evaluating [{type(node)}] node: {node}")

    match node:
        case IntegerLiteral():
            return IntegerValue(value=node.value)
        case FloatLiteral():
            return FloatValue(value=node.value)
        case TextLiteral():
            return TextValue(value=node.value)
        case HexLiteral():
            return HexValue(value=node.value)
        case Base64Literal():
            return Base64Value(value=node.value)

        case Identifier():
            return scope.get(node.name)

        case FunctionDefinitionStatement():
            closure = Closure(body=node.body, scope=scope)

            # Store the closure in the scope
            scope.put(node.name, closure)

            return HoleValue()

        case UnaryOperation():
            value = evaluate_node(node.expression, scope=scope)
            match node.operator:
                case Operator.SUBTRACT:
                    if not isinstance(value, Negatable):
                        raise ScrapTypeError(
                            f"Operator + not valid on <{type(value)}> objects")
                    return value.negate()

                case _:
                    raise ScrapEvalError(
                        f"Operator <{node.operator}> is not a valid unary operator")

        case BinaryOperation():
            left = evaluate_node(node=node.left, scope=scope)
            right = evaluate_node(node=node.right, scope=scope)
            match node.operator:
                case Operator.ADD:
                    if not isinstance(left, Addable):
                        raise ScrapTypeError(
                            f"Operator + not valid on <{type(left)}> objects")

                    return left.add(right)

                case Operator.SUBTRACT:
                    if not isinstance(left, Subtractable):
                        raise ScrapTypeError(
                            f"Operator + not valid on <{type(left)}> objects")

                    return left.subtract(right)

                case Operator.MULTIPLY:
                    if not isinstance(left, Multipliable):
                        raise ScrapTypeError(
                            f"Operator + not valid on <{type(left)}> objects")

                    return left.multiply(right)

                case Operator.DIVIDE:
                    if not isinstance(left, Dividable):
                        raise ScrapTypeError(
                            f"Operator + not valid on <{type(left)}> objects")

                    return left.divide(right)

    raise ScrapEvalError(f"Don't know how to handle node: <{node}>")
