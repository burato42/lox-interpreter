from decimal import Decimal

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
        expression = parser.parse().traverse()
        assert [el.value for el in expression] == ["true", "false", "nil"]

    def test_numbers(self):
        parser = Parser(
            [
                Token(TokenType.NUMBER, "3.14", Decimal("3.14"), 1),
                Token(TokenType.NUMBER, "0", Decimal("0.0"), 1),
                Token(TokenType.NUMBER, "42", Decimal("42.0"), 1),
            ]
        )
        expression = parser.parse().traverse()
        assert [el.value for el in expression] == ["3.14", "0.0", "42.0"]

    def test_strings(self):
        parser = Parser(
            [
                Token(TokenType.STRING, '"abc"', "abc", 1),
                Token(TokenType.STRING, '"123"', "123", 1),
                Token(
                    TokenType.STRING, '"abc*&*U&D>=-123+!="', "abc*&*U&D>=-123+!=", 1
                ),
            ]
        )
        expression = parser.parse().traverse()

        assert [el.value for el in expression] == ["abc", "123", "abc*&*U&D>=-123+!="]

    def test_groups(self):
        parser = Parser(
            [
                Token(TokenType.LEFT_PAREN, "(", None, 1),
                Token(TokenType.STRING, '"bar"', "bar", 1),
                Token(TokenType.RIGHT_PAREN, ")", None, 2),
            ]
        )
        expression = parser.parse().traverse()
        assert [el.value for el in expression] == ["(group ", "bar", ")"]
