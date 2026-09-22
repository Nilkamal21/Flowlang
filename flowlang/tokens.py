from enum import Enum, auto
from typing import Any

class TokenType(Enum):
    # Keywords
    LET = auto()
    SHOW = auto()
    WHEN = auto()
    OTHERWISE = auto()
    DEFINE = auto()
    GIVE = auto()
    KEEP = auto()
    WHERE = auto()
    TRANSFORM = auto()
    INTO = auto()
    USING = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    # Literals
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    BOOLEAN = auto()

    # Identifiers
    IDENTIFIER = auto()

    # Operators
    ASSIGN = auto()         # <-
    PIPE = auto()           # |>
    PLUS = auto()           # +
    MINUS = auto()          # -
    STAR = auto()           # *
    SLASH = auto()          # /
    PERCENT = auto()        # %

    # Comparison
    EQUAL_EQUAL = auto()    # ==
    NOT_EQUAL = auto()      # !=
    LESS = auto()           # <
    LESS_EQUAL = auto()     # <=
    GREATER = auto()        # >
    GREATER_EQUAL = auto()  # >=

    # Punctuation & Delimiters
    COLON = auto()          # :
    COMMA = auto()          # ,
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    LBRACK = auto()         # [
    RBRACK = auto()         # ]

    # Indentation & Line Control
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()

# Mapping of literal keyword strings to TokenType
KEYWORDS = {
    "let": TokenType.LET,
    "show": TokenType.SHOW,
    "when": TokenType.WHEN,
    "otherwise": TokenType.OTHERWISE,
    "define": TokenType.DEFINE,
    "give": TokenType.GIVE,
    "keep": TokenType.KEEP,
    "where": TokenType.WHERE,
    "transform": TokenType.TRANSFORM,
    "into": TokenType.INTO,
    "using": TokenType.USING,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "true": TokenType.BOOLEAN,
    "false": TokenType.BOOLEAN,
}

class Token:
    """
    Represents a single Token in Flowlang.
    """
    def __init__(self, type: TokenType, value: Any, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {repr(self.value)}, line={self.line}, col={self.column})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return False
        return (
            self.type == other.type
            and self.value == other.value
            and self.line == other.line
            and self.column == other.column
        )
