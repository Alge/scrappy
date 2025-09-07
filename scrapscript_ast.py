"""
This module defines the data structures for the Abstract Syntax Tree (AST)
of the ScrapScript language.

The AST is a hierarchical representation of the code's structure, produced
by the parser. The evaluator will then "walk" this tree to execute the program.
"""

from dataclasses import dataclass
from typing import List, Optional, Union

# Note: We need to import the Operator enum as it's part of the BinaryOperation node.
# It's good practice to move shared enums like this to their own file later,
# but for now, we can import it from the parser.

from enums import Operator


# =====================================================================
# == Base Classes: The Foundation of the AST
# =====================================================================

@dataclass
class ASTNode:
    """The common base class for all nodes in the Abstract Syntax Tree."""
    # Common fields like source location (line number, column) could be added here later.
    pass


@dataclass
class Statement(ASTNode):
    """Base class for all statements (commands that perform an action)."""
    pass


@dataclass
class Expression(ASTNode):
    """Base class for all expressions (constructs that evaluate to a value)."""
    pass


# =====================================================================
# == Program Root
# =====================================================================

@dataclass
class Program(ASTNode):
    """The root node of the entire AST, representing a complete program."""
    declarations: List[Statement]


# =====================================================================
# == Statement Nodes
# =====================================================================

@dataclass
class FunctionDefinitionStatement(Statement):
    """A function definition, e.g., `f = 1 + 2`."""
    name: str
    body: Expression


@dataclass
class TypeDefinitionStatment(Statement):
    """A type definition, e.g., `point : #2d | #3d`."""
    name: 'Identifier'
    body: 'TypeExpression'


@dataclass
class ExpressionStatement(Statement):
    """A statement that consists of a single expression to be evaluated."""
    expression: Expression


# =====================================================================
# == Expression Nodes
# =====================================================================

@dataclass
class Identifier(Expression):
    """Represents a name, like a variable or function name."""
    name: str

    def __repr__(self) -> str:
        return self.name


@dataclass
class UnaryOperation(Expression):
    """A prefix operation, e.g., `-5`."""
    expression: Expression
    operator: Operator

    def __repr__(self) -> str:
        return f"({self.operator.value} {self.expression})"


@dataclass
class BinaryOperation(Expression):
    """An infix operation, e.g., `1 + 2`."""
    left: Expression
    right: Expression
    operator: Operator

    def __repr__(self) -> str:
        return f"({self.operator.value} {self.left} {self.right})"


@dataclass
class VariantConstruction(Expression):
    """A constructed variant, e.g., `scoop::chocolate 1`."""
    type_name: Identifier
    variant_name: Identifier
    arguments: List[Expression]


@dataclass
class PatternMatchExpression(Expression):
    """A pattern matching block, e.g., `| 1 -> "a" | _ -> "b"`."""
    clauses: List['PatternClause']


@dataclass
class PatternClause:
    """A single clause of a pattern match, e.g., `| 1 -> "a"`."""
    pattern: 'Pattern'
    body: Expression


# =====================================================================
# == Pattern Nodes (for Pattern Matching)
# =====================================================================

@dataclass
class Pattern(ASTNode):
    """Base class for all patterns used in pattern matching."""
    pass


@dataclass
class LiteralPattern(Pattern):
    """A pattern that matches a literal value."""
    literal: 'Literal'


@dataclass
class WildcardPattern(Pattern):
    """A pattern that matches anything and discards it (`_`)."""
    pass


@dataclass
class VariablePattern(Pattern):
    """A pattern that matches anything and binds it to a variable."""
    identifier: Identifier


# =====================================================================
# == Type Definition Nodes
# =====================================================================

@dataclass
class TypeExpression(ASTNode):
    """The body of a type definition, e.g., `#a int | #b`."""
    variants: List['TypeVariant']


@dataclass
class TypeVariant(ASTNode):
    """A single variant in a type definition, e.g., `#ok int`."""
    tag: 'Atom'
    parameter: Optional[Union[Identifier, TypeExpression]] = None


@dataclass
class Atom(ASTNode):
    """A symbolic tag, e.g., `#ok` (stored as 'ok')."""
    value: str


# =====================================================================
# == Literal Nodes (a sub-category of Expression)
# =====================================================================

@dataclass
class Literal(Expression):
    """Base class for all literal values."""
    pass


@dataclass
class IntegerLiteral(Literal):
    value: int

    def __repr__(self) -> str:
        return str(self.value)


@dataclass
class FloatLiteral(Literal):
    value: float

    def __repr__(self) -> str:
        return str(self.value)


@dataclass
class TextLiteral(Literal):
    value: str

    def __repr__(self) -> str:
        # Use Python's repr to keep the quotes, making it clear it's a string.
        return self.value


@dataclass
class InterpolatedTextLiteral(Literal):
    value: str

    def __repr__(self) -> str:
        return f'`{self.value}`'


@dataclass
class HexLiteral(Literal):
    value: str

    def __repr__(self) -> str:
        return f"Hex({self.value})"


@dataclass
class Base64Literal(Literal):
    value: str

    def __repr__(self) -> str:
        return self.value
