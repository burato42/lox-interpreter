from decimal import Decimal
from typing import Optional

from app.errors import TokenError, UnterminatedStringError, InterpretationError
from app.tokenization import (
    Token,
    TOKEN_MAPPING,
    TokenType,
    COMMENT,
    SPACE,
    TAB,
    QUOTE,
    BORDER_CHARS,
    WHITESPACE_CHARS,
)


class Scanner:
    def __init__(self, source: str):
        self.source_lines: list[str] = source.splitlines()
        self.position_start: int = 0
        self.tokens: list[Token] = []
        self.errors: list[InterpretationError] = []
        self.quote_start: Optional[int] = None
        self.digits: str = ""
        self.identifier: str = ""

    def _scan_line(self, line_idx: int, line: str):
        while self.position_start < len(line):
            character = line[self.position_start]

            # Check for two-character tokens
            if self.position_start + 1 < len(line) and self.quote_start is None:
                two_chars = character + line[self.position_start + 1]
                if two_chars == COMMENT:
                    # If we see the comment we ignore the whole remaining line
                    break

                if two_chars in TOKEN_MAPPING:
                    self.tokens.append(
                        Token(TOKEN_MAPPING[two_chars], two_chars, None, line_idx + 1)
                    )
                    self.position_start += 2
                    continue

            if self._extract_identifier(character, line_idx, line):
                if self.digits:
                    # If there is no gap between the number and the identifier
                    # we just add a number token, so we don't need to process it later
                    self.tokens.append(
                        Token(
                            TokenType.NUMBER,
                            self.digits,
                            Decimal(str(float(self.digits))),
                            line_idx + 1,
                        )
                    )
                    self.digits = ""

                continue

            if self._extract_number(character, line_idx, line):
                continue

            # Handle single-character tokens
            if self.quote_start is None and character == QUOTE:
                self.quote_start = self.position_start
            elif self.quote_start is None:
                if character in TOKEN_MAPPING:
                    self.tokens.append(
                        Token(TOKEN_MAPPING[character], character, None, line_idx + 1)
                    )
                elif character in [SPACE, TAB]:
                    pass  # Ignore whitespace characters
                else:
                    self.errors.append(TokenError(character, line_idx + 1))
            elif self.quote_start is not None and character == QUOTE:
                lexeme = line[self.quote_start : self.position_start + 1]
                literal = lexeme[1:-1]
                self.tokens.append(
                    Token(TokenType.STRING, lexeme, literal, line_idx + 1)
                )
                self.quote_start = None
            elif (
                self.quote_start is not None
                and self._is_last_character(line)
                and character != QUOTE
            ):
                self.errors.append(UnterminatedStringError(line_idx + 1))

            self.position_start += 1

    def _is_last_character(self, line: str) -> bool:
        return self.position_start == len(line) - 1

    def _extract_number(self, character: str, line_idx: int, line: str) -> bool:
        if self.quote_start is None:
            if self._is_last_character_digital(character, line_idx, line):
                return True

            if self._is_digit_in_middle(character):
                return True

            if self._is_number_border_character(character, line_idx, line):
                return True
        return False

    def _is_last_character_digital(
        self, character: str, line_idx: int, line: str
    ) -> bool:
        if (character.isdigit() and self._is_last_character(line)) or (
            self.digits
            and (character.isdigit() or character == ".")
            and self._is_last_character(line)
        ):
            # the last or the only digit character in the line
            self.digits += character
            self.tokens.append(
                Token(
                    TokenType.NUMBER,
                    self.digits,
                    Decimal(str(float(self.digits))),
                    line_idx + 1,
                )
            )
            self.digits = ""
            self.position_start += 1
            return True
        return False

    def _is_last_character_identifierable(
        self, character: str, line_idx: int, line: str
    ) -> bool:
        if (
            (character.isalpha() or character == "_") and self._is_last_character(line)
        ) or (
            self.identifier
            and (character.isalnum() or character == "_")
            and self._is_last_character(line)
        ):
            self.identifier += character
            self.tokens.append(
                Token(
                    TokenType.IDENTIFIER,
                    self.identifier,
                    None,
                    line_idx + 1,
                )
            )
            self.identifier = ""
            self.position_start += 1
            return True
        return False

    def _is_digit_in_middle(self, character: str) -> bool:
        if character.isdigit() or (
            self.digits and (character.isdigit() or character == ".")
        ):
            self.digits += character
            self.position_start += 1
            return True
        return False

    def _is_identifier_in_middle(self, character: str) -> bool:
        if (
            character.isalpha()
            or character == "_"
            or (self.identifier and character.isalnum())
        ):
            self.identifier += character
            self.position_start += 1
            return True
        return False

    def _is_number_border_character(
        self, character: str, line_idx: int, line: str
    ) -> bool:
        if self.digits and (
            character in BORDER_CHARS + WHITESPACE_CHARS
            or self._is_last_character(line)
            or character.isalpha()
            or character == "_"
        ):
            self.tokens.append(
                Token(
                    TokenType.NUMBER,
                    self.digits,
                    Decimal(str(float(self.digits))),
                    line_idx + 1,
                )
            )
            self.digits = ""
            if character in WHITESPACE_CHARS:
                self.position_start += 1
            return True
        return False

    def _is_identifier_border_character(
        self, character: str, line_idx: int, line: str
    ) -> bool:
        if self.identifier and (
            character in BORDER_CHARS + WHITESPACE_CHARS
            or self._is_last_character(line)
        ):
            self.tokens.append(
                Token(
                    TokenType.IDENTIFIER,
                    self.identifier,
                    None,
                    line_idx + 1,
                )
            )
            self.identifier = ""
            if character in WHITESPACE_CHARS:
                self.position_start += 1
            return True
        return False

    def _extract_identifier(self, character: str, line_idx: int, line: str) -> bool:
        if self.quote_start is None:
            if self._is_last_character_identifierable(character, line_idx, line):
                return True

            if self._is_identifier_in_middle(character):
                return True

            if self._is_identifier_border_character(character, line_idx, line):
                return True
        return False

    def scan_tokens(self) -> tuple[list[Token], list[InterpretationError]]:
        # TODO current implementation is not straightforward,
        #  will be refactored when the whole scanner component is ready
        for line_idx, line in enumerate(self.source_lines):
            self.position_start = 0
            self.quote_start = None
            self._scan_line(line_idx, line)

        self.tokens.append(Token(TokenType.EOF, "", None, len(self.source_lines)))
        return self.tokens, self.errors
