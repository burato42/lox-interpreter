from decimal import Decimal

import pytest

from app.parser import Parser
from app.tokenization import Token, TokenType


class TestParser:
    def test_bool(self):
        parser = Parser(
            [
                Token(TokenType.TRUE, "true", None, 1),
                Token(TokenType.FALSE, "false", None, 2),
                Token(TokenType.NIL, "nil", None, 3),
            ]
        )
        lexemes = parser.parse()
        assert list(lexemes) == ["true", "false", "nil"]

    def test_numbers(self):
        parser = Parser(
            [
                Token(TokenType.NUMBER, "3.14", Decimal("3.14"), 1),
                Token(TokenType.NUMBER, "0", Decimal("0.0"), 1),
                Token(TokenType.NUMBER, "42", Decimal("42.0"), 1),
            ]
        )
        parsed = parser.parse()
        assert list(parsed) == [Decimal("3.14"), Decimal("0.0"), Decimal("42.0")]
