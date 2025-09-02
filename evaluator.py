
from dataclasses import dataclass
from typing import Dict, Optional

from parser import Expression, Identifier, Program, Statement


class NameError(Exception):

    def __init__(self, name: Identifier):
        self.name = name

    def __repr__(self):
        return f"Name '{self.name}' is not defined"


class Scope():
    parent: Optional['Scope']
    variables: Dict[Identifier, 'Value'] = {}

    def __init__(self, parent=None):
        self.parent = parent

    def get(self, identifier: Identifier):
        if identifier in self.variables:
            return self.variables[identifier]

        if self.parent is not None:
            return self.parent.get(identifier=identifier)

        raise NameError(identifier)


class Value():  # Base class for runtime values
    pass


@dataclass
class IntegerValue(Value):
    value: int


@dataclass
class FloatValue(Value):
    value: float


@dataclass
class TextValue(Value):
    value: str


@dataclass
class Closure(Value):
    body: Expression
    scope: Scope


def evaluate_expression(node: Statement, scope: Scope):

    pass
