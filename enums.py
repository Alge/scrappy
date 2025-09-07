from enum import Enum


class Operator(str, Enum):
    MULTIPLY = "*"
    DIVIDE = "/"
    ADD = "+"
    SUBTRACT = "-"


# You can also move PrecedencePosition here if you like.


class PrecedencePosition(str, Enum):
    PREFIX = "PREFIX"
    INFIX = "INFIX"
