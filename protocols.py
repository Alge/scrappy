"""
This module defines the abstract "protocols" or "interfaces" that
runtime Value objects can implement.

These abstract base classes (ABCs) define the contracts for operations
like addition, comparison, etc. The evaluator will use these interfaces
to dispatch operations in a polymorphic way, allowing different types
to define their own behavior for operators like '+'.
"""

from __future__ import annotations
from abc import ABC, abstractmethod

# The `typing.TYPE_CHECKING` block prevents circular import errors
# at runtime, while still allowing static type checkers like MyPy to
# understand the type hints.
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from values import Value


# =====================================================================
# == Arithmetic Protocols
# =====================================================================

class Addable(ABC):
    """An interface for objects that support the '+' operation."""
    @abstractmethod
    def add(self, other: Value) -> Value:
        pass


class Subtractable(ABC):
    """An interface for objects that support the '-' operation."""
    @abstractmethod
    def subtract(self, other: Value) -> Value:
        pass


class Multipliable(ABC):
    """An interface for objects that support the '*' operation."""
    @abstractmethod
    def multiply(self, other: Value) -> Value:
        pass


class Dividable(ABC):
    """An interface for objects that support the '/' operation."""
    @abstractmethod
    def divide(self, other: Value) -> Value:
        pass


class Negatable(ABC):
    """An interface for object supporting to be negated, e.g - 3"""

    @abstractmethod
    def negate(self) -> Value:
        pass


# =====================================================================
# == Collection Protocols
# =====================================================================

class Concatenatable(ABC):
    """
    An interface for objects that support the '++' operation (concatenation),
    typically used to combine two collections of the same type.
    """
    @abstractmethod
    def concatenate(self, other: Value) -> Value:
        pass


class Appendable(ABC):
    """
    An interface for objects that support the '+<' operation (appending an element),
    typically used to add an element to the end of a collection.
    """
    @abstractmethod
    def append(self, other: Value) -> Value:
        pass


# =====================================================================
# == Comparison Protocols
# =====================================================================

# class Equatable(ABC):
#     """An interface for objects that support equality ('==') and inequality ('/=') checks."""
#     @abstractmethod
#     def equals(self, other: Value) -> BooleanValue:
#         pass
#
#     def not_equals(self, other: Value) -> BooleanValue:
#         """Provides a default implementation for '!=' based on '=='."""
#         from .values import BooleanValue  # Local import to avoid circular dependency
#         return BooleanValue(not self.equals(other).value)
#
#
# class Orderable(ABC):
#     """An interface for objects that can be ordered ('<', '>', '<=', '>=')."""
#     @abstractmethod
#     def less_than(self, other: Value) -> BooleanValue:
#         pass
#
#     def greater_than(self, other: Value) -> BooleanValue:
#         """Provides a default implementation for '>' based on '<'."""
#         # The logic `a > b` is the same as `b < a`.
#         if isinstance(other, Orderable):
#             return other.less_than(self)
#         # If 'other' doesn't support ordering, the operation is invalid.
#         # The specific error message is best handled in the calling evaluator.
#         # We can raise a generic TypeError here.
#         raise TypeError(
#             f"Cannot compare order between {type(self).__name__} and {type(other).__name__}")
#
#     def less_than_or_equal(self, other: Value) -> BooleanValue:
#         """Provides a default implementation for '<='."""
#         from .values import BooleanValue  # Local import
#         # `a <= b` is the same as `not (a > b)`.
#         return BooleanValue(not self.greater_than(other).value)
#
#     def greater_than_or_equal(self, other: Value) -> BooleanValue:
#         """Provides a default implementation for '>='."""
#         from .values import BooleanValue  # Local import
#         # `a >= b` is the same as `not (a < b)`.
#         return BooleanValue(not self.less_than(other).value)
#
