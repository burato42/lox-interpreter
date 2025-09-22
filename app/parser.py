from typing import Any, Iterator

from app.tokenization import Token, TokenType


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens

    def parse(self) -> Iterator[Any]:
        for token in self.tokens:
            # Seems overcomplicated
            if token.type == TokenType.TRUE:
                yield token.lexeme
            elif token.type == TokenType.FALSE:
                yield token.lexeme
            elif token.type == TokenType.NIL:
                yield token.lexeme
