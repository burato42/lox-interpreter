from decimal import Decimal

import pytest

from app.errors import TokenError, UnterminatedStringError
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
        assert isinstance(errors[0], TokenError)
        assert isinstance(errors[1], TokenError)
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

    def test_string_literals(self):
        scanner = Scanner('"foo baz"')
        tokens, errors = scanner.scan_tokens()
        assert len(tokens) == 2
        assert tokens[0] == Token(TokenType.STRING, '"foo baz"', "foo baz", 1)
        assert tokens[1] == Token(TokenType.EOF, "", None, 1)
        assert not errors

    def test_unterminated_string(self):
        scanner = Scanner('"bar')
        tokens, errors = scanner.scan_tokens()
        assert len(tokens) == 1
        assert tokens[0] == Token(TokenType.EOF, "", None, 1)
        assert len(errors) == 1
        assert isinstance(errors[0], UnterminatedStringError)
        assert vars(errors[0]) == vars(UnterminatedStringError(1))

    def test_string_with_comments(self):
        scanner = Scanner('"foo \tbar 123 // hello world!"')
        tokens, errors = scanner.scan_tokens()
        assert len(tokens) == 2
        assert tokens[0] == Token(
            TokenType.STRING,
            '"foo \tbar 123 // hello world!"',
            "foo \tbar 123 // hello world!",
            1,
        )
        assert tokens[1] == Token(TokenType.EOF, "", None, 1)
        assert not errors

    def test_number_literals(self):
        scanner = Scanner("42")
        tokens, errors = scanner.scan_tokens()
        assert len(tokens) == 2
        assert tokens[0] == Token(TokenType.NUMBER, "42", Decimal("42.0"), 1)
        assert tokens[1] == Token(TokenType.EOF, "", None, 1)
        assert not errors

    def test_different_number_forms(self):
        scanner = Scanner("1\n2345.6789\n42.0000")
        tokens, errors = scanner.scan_tokens()
        assert len(tokens) == 4
        assert tokens[0] == Token(TokenType.NUMBER, "1", Decimal("1.0"), 1)
        assert tokens[1] == Token(
            TokenType.NUMBER, "2345.6789", Decimal("2345.6789"), 2
        )
        assert tokens[2] == Token(TokenType.NUMBER, "42.0000", Decimal("42.0"), 3)
        assert tokens[3] == Token(TokenType.EOF, "", None, 3)
        assert not errors

    def test_math_sentence(self):
        scanner = Scanner('(29+78) > 69 != ("Success" != "Failure") != (15.5 >= 52)')
        tokens, errors = scanner.scan_tokens()
        assert len(tokens) == 20
        assert tokens[0] == Token(TokenType.LEFT_PAREN, "(", None, 1)
        assert tokens[1] == Token(TokenType.NUMBER, "29", Decimal("29.0"), 1)
        assert tokens[2] == Token(TokenType.PLUS, "+", None, 1)
        assert tokens[3] == Token(TokenType.NUMBER, "78", Decimal("78.0"), 1)
        assert tokens[4] == Token(TokenType.RIGHT_PAREN, ")", None, 1)
        assert tokens[5] == Token(TokenType.GREATER, ">", None, 1)
        assert tokens[6] == Token(TokenType.NUMBER, "69", Decimal("69.0"), 1)
        assert tokens[7] == Token(TokenType.BANG_EQUAL, "!=", None, 1)
        assert tokens[8] == Token(TokenType.LEFT_PAREN, "(", None, 1)
        assert tokens[9] == Token(TokenType.STRING, '"Success"', "Success", 1)
        assert tokens[10] == Token(TokenType.BANG_EQUAL, "!=", None, 1)
        assert tokens[11] == Token(TokenType.STRING, '"Failure"', "Failure", 1)
        assert tokens[12] == Token(TokenType.RIGHT_PAREN, ")", None, 1)
        assert tokens[13] == Token(TokenType.BANG_EQUAL, "!=", None, 1)
        assert tokens[14] == Token(TokenType.LEFT_PAREN, "(", None, 1)
        assert tokens[15] == Token(TokenType.NUMBER, "15.5", Decimal("15.5"), 1)
        assert tokens[16] == Token(TokenType.GREATER_EQUAL, ">=", None, 1)
        assert tokens[17] == Token(TokenType.NUMBER, "52", Decimal("52.0"), 1)
        assert tokens[4] == Token(TokenType.RIGHT_PAREN, ")", None, 1)
        assert tokens[19] == Token(TokenType.EOF, "", None, 1)
        assert not errors

    def test_identifiers(self):
        scanner = Scanner("_1236ar 6az baz foo7 bar")
        tokens, errors = scanner.scan_tokens()
        assert len(tokens) == 7
        assert tokens[0] == Token(TokenType.IDENTIFIER, "_1236ar", None, 1)
        assert tokens[1] == Token(TokenType.NUMBER, "6", Decimal(float("6.0")), 1)
        assert tokens[2] == Token(TokenType.IDENTIFIER, "az", None, 1)
        assert tokens[3] == Token(TokenType.IDENTIFIER, "baz", None, 1)
        assert tokens[4] == Token(TokenType.IDENTIFIER, "foo7", None, 1)
        assert tokens[5] == Token(TokenType.IDENTIFIER, "bar", None, 1)
        assert tokens[6] == Token(TokenType.EOF, "", None, 1)
        assert not errors

    def test_reserved_words(self):
        scanner = Scanner("var foo if bar else 0")
        tokens, errors = scanner.scan_tokens()
        assert len(tokens) == 7
        assert tokens[0] == Token(TokenType.VAR, "var", None, 1)
        assert tokens[1] == Token(TokenType.IDENTIFIER, "foo", None, 1)
        assert tokens[2] == Token(TokenType.IF, "if", None, 1)
        assert tokens[3] == Token(TokenType.IDENTIFIER, "bar", None, 1)
        assert tokens[4] == Token(TokenType.ELSE, "else", None, 1)
        assert tokens[5] == Token(TokenType.NUMBER, "0", Decimal(float("0")), 1)
        assert tokens[6] == Token(TokenType.EOF, "", None, 1)
        assert not errors

    def test_code_sample(self):
        scanner = Scanner("""var result = (a + b) > 7 or "Success" != "Failure" or x >= 5
        while (result) {
            var counter = 0
            counter = counter + 1
            if (counter == 10) {
                return nil
            }
        }""")
        tokens, errors = scanner.scan_tokens()
        assert not errors
        expected_result = """VAR var null
IDENTIFIER result null
EQUAL = null
LEFT_PAREN ( null
IDENTIFIER a null
PLUS + null
IDENTIFIER b null
RIGHT_PAREN ) null
GREATER > null
NUMBER 7 7.0
OR or null
STRING "Success" Success
BANG_EQUAL != null
STRING "Failure" Failure
OR or null
IDENTIFIER x null
GREATER_EQUAL >= null
NUMBER 5 5.0
WHILE while null
LEFT_PAREN ( null
IDENTIFIER result null
RIGHT_PAREN ) null
LEFT_BRACE { null
VAR var null
IDENTIFIER counter null
EQUAL = null
NUMBER 0 0.0
IDENTIFIER counter null
EQUAL = null
IDENTIFIER counter null
PLUS + null
NUMBER 1 1.0
IF if null
LEFT_PAREN ( null
IDENTIFIER counter null
EQUAL_EQUAL == null
NUMBER 10 10.0
RIGHT_PAREN ) null
LEFT_BRACE { null
RETURN return null
NIL nil null
RIGHT_BRACE } null
RIGHT_BRACE } null
EOF  null
        """
        for token, expect in zip(tokens, expected_result.splitlines()):
            assert str(token) == expect
