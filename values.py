from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from enums import Operator
from exceptions import ScrapEvalError, ScrapTypeError
from protocols import Addable, Concatenatable, Dividable, Multipliable, Negatable, Subtractable
from scrapscript_ast import Expression

if TYPE_CHECKING:
    from scope import Scope


class Value():  # Base class for runtime values
    pass


@dataclass
class HoleValue(Value):
    pass


@dataclass
class IntegerValue(Value, Addable, Subtractable, Multipliable, Dividable, Negatable):
    value: int

    def _do_math_operation(self, other: Value, operator: Operator) -> IntegerValue:
        if not isinstance(other, IntegerValue):
            raise ScrapTypeError(
                f"Cannot perform '{operator}' operation on {type(self)} and {type(other)}")

        match operator:
            case Operator.ADD:
                return IntegerValue(self.value + other.value)
            case Operator.SUBTRACT:
                return IntegerValue(self.value - other.value)
            case Operator.DIVIDE:
                return IntegerValue(int(self.value / other.value))
            case Operator.MULTIPLY:
                return IntegerValue(self.value * other.value)

        raise ScrapEvalError(
            f"Don't know how to apply operator '{operator} to <{type(self)}> and <{type(other)}> objects'"
        )

    def add(self, other) -> IntegerValue:
        return self._do_math_operation(other, operator=Operator.ADD)

    def subtract(self, other) -> IntegerValue:
        return self._do_math_operation(other, operator=Operator.SUBTRACT)

    def divide(self, other) -> IntegerValue:
        return self._do_math_operation(other, operator=Operator.DIVIDE)

    def multiply(self, other) -> IntegerValue:
        return self._do_math_operation(other, operator=Operator.MULTIPLY)

    def negate(self) -> IntegerValue:
        return IntegerValue(value=-self.value)

    def __str__(self):
        return f"{self.value}"

    def __repr__(self):
        return f"IntegerValue({self.value})"


@dataclass
class FloatValue(Value, Addable, Subtractable, Multipliable, Dividable, Negatable):
    value: float

    def _do_math_operation(self, other: Value, operator: Operator) -> FloatValue:
        if not isinstance(other, FloatValue):
            raise ScrapTypeError(
                f"Cannot perform '{operator}' operation on {type(self)} and {type(other)}")

        match operator:
            case Operator.ADD:
                return FloatValue(self.value + other.value)
            case Operator.SUBTRACT:
                return FloatValue(self.value - other.value)
            case Operator.DIVIDE:
                return FloatValue(self.value / other.value)
            case Operator.MULTIPLY:
                return FloatValue(self.value * other.value)

        raise ScrapEvalError(
            f"Don't know how to apply operator '{operator} to <{type(self)}> and <{type(other)}> objects'"
        )

    def add(self, other) -> FloatValue:
        return self._do_math_operation(other, operator=Operator.ADD)

    def subtract(self, other) -> FloatValue:
        return self._do_math_operation(other, operator=Operator.SUBTRACT)

    def divide(self, other) -> FloatValue:
        return self._do_math_operation(other, operator=Operator.DIVIDE)

    def multiply(self, other) -> FloatValue:
        return self._do_math_operation(other, operator=Operator.MULTIPLY)

    def negate(self) -> FloatValue:
        return FloatValue(value=-self.value)

    def __str__(self):
        return f"{self.value}"


@dataclass
class HexValue(Value, Addable, Subtractable, Multipliable, Dividable):
    value: str

    def add(self, other):
        assert isinstance(other, HexValue)
        return HexValue(value=self.value + other.value)

    def subtract(self, other):
        assert isinstance(other, HexValue)
        return HexValue(value=self.value - other.value)

    def divide(self, other):
        assert isinstance(other, HexValue)
        return HexValue(value=self.value / other.value)

    def multiply(self, other):
        assert isinstance(other, HexValue)
        return HexValue(value=self.value * other.value)

    def __str__(self):
        return f"#{self.value}"


@dataclass
class TextValue(Value, Concatenatable):
    value: str

    def concatenate(self, other):
        assert isinstance(other, TextValue)

        return TextValue(self.value + other.value)

    def __str__(self):
        return f"\"{self.value}\""


@dataclass
class Base64Value(Value):
    value: str

    def __str__(self):
        return self.value


@dataclass
class VariantValue(Value):
    tag: str
    payload: Value


@dataclass
@dataclass
class Closure(Value):
    body: Expression
    scope: "Scope"

    def __str__(self):
        return "<function>"


# TRUE = VariantValue(tag="true", payload=HoleValue())
# FALSE = VariantValue(tag="false", payload=HoleValue())
