

from dataclasses import dataclass
from typing import Dict, Optional

from exceptions import ScrapNameError
from parser import Expression
from scrapscript_ast import Identifier


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
class Nil(Value):
    pass


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

        raise ScrapNameError(identifier.name)


@dataclass
class Closure(Value):
    body: Expression
    scope: Scope
