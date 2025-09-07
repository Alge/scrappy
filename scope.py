from __future__ import annotations
from typing import Dict, Optional

from exceptions import ScrapNameError
from scrapscript_ast import Identifier
from values import Value


class Scope():
    parent: Optional[Scope]
    variables: Dict[str, Value] = {}

    def __init__(self, parent: Optional[Scope] = None):
        self.parent = parent
        self.variables = {}

    def put(self, name: str, value: Value):
        self.variables[name] = value

    def get(self, name: str) -> Value:
        if name in self.variables:
            return self.variables[name]

        if self.parent is not None:
            return self.parent.get(name=name)

        raise ScrapNameError(name)
