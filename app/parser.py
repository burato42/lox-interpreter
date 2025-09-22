from typing import Any, Iterator

from app.tokenization import Token, TokenType


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens

    def parse(self) -> Iterator[Any]:
        for token in self.tokens:
            # Seems overcomplicated
            # there is a mix of lexemes and literals...
            if token.type == TokenType.TRUE:
                yield token.lexeme
            elif token.type == TokenType.FALSE:
                yield token.lexeme
            elif token.type == TokenType.NIL:
                yield token.lexeme
            elif token.type == TokenType.NUMBER:
                yield str(token.literal)
            elif token.type == TokenType.STRING:
                yield token.literal
            elif token.type == TokenType.LEFT_PAREN:
                yield token.lexeme + "group "
            elif token.type == TokenType.RIGHT_PAREN:
                yield token.lexeme
