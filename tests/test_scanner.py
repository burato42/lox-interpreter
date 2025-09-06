import pytest

from app.errors import TokenError
from app.scanner import Scanner
from app.tokenization import TokenType, Token


TEST_TOKEN_MAPPING = [
    ("(", TokenType.LEFT_PAREN),
    (")", TokenType.RIGHT_PAREN),
    ("{", TokenType.LEFT_BRACE),
    ("}", TokenType.RIGHT_BRACE),
    (",", TokenType.COMMA),
    (".", TokenType.DOT),
    ("-", TokenType.MINUS),
    ("+", TokenType.PLUS),
    (";", TokenType.SEMICOLON),
    ("/", TokenType.SLASH),
    ("*", TokenType.STAR),
]


class TestScanner:
    """
    Test that empty file  just shows the end of the file
    """
    def test_empty(self):
        content = ""
        scanner = Scanner(content)

        tokens, errors = scanner.scan_tokens()

        assert len(tokens) == 1
        assert tokens[0] == Token(TokenType.EOF, "", None, 0)
        assert not errors

    """
    Test that known single character tokens are parsed correctly
    """
    @pytest.mark.parametrize("token_pair", TEST_TOKEN_MAPPING)
    def test_single_character_tokens(self, token_pair):
        character, token_type = token_pair
        scanner = Scanner(character)

        tokens, errors = scanner.scan_tokens()

        assert len(tokens) == 2
        assert tokens[0] == Token(token_type, character, None, 1)
        assert tokens[1] == Token(TokenType.EOF, "", None, 1)
        assert not errors


    def test_presence_of_unknown_sy(self):
        scanner = Scanner("({}%+;\n-/@")

        tokens, errors = scanner.scan_tokens()

        assert len(tokens) == 8
        assert len(errors) == 2
        assert vars(errors[0]) == vars(TokenError("%", 1))
        assert vars(errors[1]) == vars(TokenError("@", 2))
        assert tokens[0] == Token(TokenType.LEFT_PAREN, "(", None, 1)
        assert tokens[1] == Token(TokenType.LEFT_BRACE, "{", None, 1)
        assert tokens[2] == Token(TokenType.RIGHT_BRACE, "}", None, 1)
        assert tokens[3] == Token(TokenType.PLUS, "+", None, 1)
        assert tokens[4] == Token(TokenType.SEMICOLON, ";", None, 1)
        assert tokens[5] == Token(TokenType.MINUS, "-", None, 2)
        assert tokens[6] == Token(TokenType.SLASH, "/", None, 2)
        assert tokens[7] == Token(TokenType.EOF, "", None, 2)

    def test_two_char_tokens(self):
        scanner = Scanner("(>=!=!")

        tokens, errors = scanner.scan_tokens()
        assert not errors
        assert len(tokens) == 5
        assert tokens[0] == Token(TokenType.LEFT_PAREN, "(", None, 1)
        assert tokens[1] == Token(TokenType.GREATER_EQUAL, ">=", None, 1)
        assert tokens[2] == Token(TokenType.BANG_EQUAL, "!=", None, 1)
        assert tokens[3] == Token(TokenType.BANG, "!", None, 1)
        assert tokens[4] == Token(TokenType.EOF, "", None, 1)

    def test_comments(self):
        scanner = Scanner("()// Comment")
        tokens, errors = scanner.scan_tokens()
        assert len(tokens) == 3
        assert tokens[0] == Token(TokenType.LEFT_PAREN, "(", None, 1)
        assert tokens[1] == Token(TokenType.RIGHT_PAREN, ")", None, 1)
        assert tokens[2] == Token(TokenType.EOF, "", None, 1)
        assert not errors

    def test_division(self):
        scanner = Scanner("/()// Comment")
        tokens, errors = scanner.scan_tokens()
        assert len(tokens) == 4
        assert tokens[0] == Token(TokenType.SLASH, "/", None, 1)
        assert tokens[1] == Token(TokenType.LEFT_PAREN, "(", None, 1)
        assert tokens[2] == Token(TokenType.RIGHT_PAREN, ")", None, 1)
        assert tokens[3] == Token(TokenType.EOF, "", None, 1)
        assert not errors

    def test_space_characters(self):
        scanner = Scanner("(\t\n )")
        tokens, errors = scanner.scan_tokens()
        assert len(tokens) == 3
        assert tokens[0] == Token(TokenType.LEFT_PAREN, "(", None, 1)
        assert tokens[1] == Token(TokenType.RIGHT_PAREN, ")", None, 2)
        assert tokens[2] == Token(TokenType.EOF, "", None, 2)
        assert not errors
