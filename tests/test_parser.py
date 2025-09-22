import pytest

from app.parser import Parser
from app.tokenization import Token, TokenType


class TestParser:

    def test_bool(self):
        parser = Parser(
            [
                Token(TokenType.TRUE, "true", None, 1),
                Token(TokenType.FALSE, "false", None, 2),
                Token(TokenType.NIL, "nil", None, 3),])
        lexemes = parser.parse()
        assert list(lexemes) == ["true", "false", "nil"]
