from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class TokenType(Enum):
     # Single-character tokens.
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    COMMA = ","
    DOT = "."
    MINUS = "-"
    PLUS = "+"
    SEMICOLON = ";"
    SLASH = "/"
    STAR = "*"

    # # One or two character tokens.
    # BANG = auto()
    # BANG_EQUAL = auto()
    # EQUAL = auto()
    # EQUAL_EQUAL = auto()
    # GREATER = auto()
    # GREATER_EQUAL = auto()
    # LESS = auto()
    # LESS_EQUAL = auto()
    #
    # # Literals.
    # IDENTIFIER = auto()
    # STRING = auto()
    # NUMBER = auto()
    #
    # # Keywords.
    # AND = auto()
    # CLASS = auto()
    # ELSE = auto()
    # FALSE = auto()
    # FUN = auto()
    # FOR = auto()
    # IF = auto()
    # NIL = auto()
    # OR = auto()
    # PRINT = auto()
    # RETURN = auto()
    # SUPER = auto()
    # THIS = auto()
    # TRUE = auto()
    # VAR = auto()
    # WHILE = auto()

    EOF = ""


@dataclass
class Token:
    type: TokenType
    lexeme: str
    literal: Any
    line: int

    def __str__(self) -> str:
        if self.type == TokenType.EOF:
            return f"{TokenType.EOF.name}  null"
        return f"{self.type.name} {self.lexeme} {self.literal if self.literal else "null"}"


class Scanner:
    def __init__(self, source: str):
        self.source_lines: list[str] = source.splitlines()
        self.tokens: list[Token] = []

    def scan(self):
        for idx, line in enumerate(self.source_lines):
            for character in line:
                match character:
                    case TokenType.LEFT_PAREN.value:
                        self.tokens.append(Token(TokenType.LEFT_PAREN, character, None, idx))
                    case TokenType.RIGHT_PAREN.value:
                        self.tokens.append(Token(TokenType.RIGHT_PAREN, character, None, idx))

        self.tokens.append(Token(TokenType.EOF, "", None, len(self.source_lines)))
