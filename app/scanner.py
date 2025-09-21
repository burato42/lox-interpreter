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
    RESERVED_WORDS,
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

    def scan_tokens(self) -> tuple[list[Token], list[InterpretationError]]:
        for line_idx, line in enumerate(self.source_lines):
            self.position_start = 0
            self.quote_start = None
            self._scan_line(line_idx, line)

        self.tokens.append(Token(TokenType.EOF, "", None, len(self.source_lines)))
        return self.tokens, self.errors

    def _scan_line(self, line_idx: int, line: str):
        while self.position_start < len(line):
            character = line[self.position_start]

            # Check for two-character tokens (like <=,!=, // etc.)
            two_char_special_token_present = self._extract_two_char_tokens(
                character, line_idx, line
            )
            if two_char_special_token_present is None:
                # We faces comment block
                break
            elif two_char_special_token_present:
                continue

            if self._extract_identifier(character, line_idx, line):
                if self.digits:
                    # If there is no gap between the number and the identifier
                    # we just add a number token, so we don't need to process it later
                    self._add_number(line_idx)
                continue

            if self._extract_number(character, line_idx, line):
                continue

            # Handle single-character tokens and strings
            self._extract_strings_and_single_tokens(character, line_idx, line)

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
            self._add_number(line_idx)
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
            self._add_identifier(line_idx)
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
            self._add_number(line_idx)
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
            self._add_identifier(line_idx)
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

    def _extract_two_char_tokens(
        self, character: str, line_idx: int, line: str
    ) -> Optional[bool]:
        # Check for two-character tokens
        if self.position_start + 1 < len(line) and self.quote_start is None:
            two_chars = character + line[self.position_start + 1]
            if two_chars == COMMENT:
                # If we see the comment we ignore the whole remaining line
                return None

            if two_chars in TOKEN_MAPPING:
                self.tokens.append(
                    Token(TOKEN_MAPPING[two_chars], two_chars, None, line_idx + 1)
                )
                self.position_start += 2
                return True
        return False

    def _extract_strings_and_single_tokens(
        self, character: str, line_idx: int, line: str
    ) -> Optional[bool]:
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
        # Extracting a string here
        elif self.quote_start is not None and character == QUOTE:
            lexeme = line[self.quote_start : self.position_start + 1]
            literal = lexeme[1:-1]
            self.tokens.append(Token(TokenType.STRING, lexeme, literal, line_idx + 1))
            self.quote_start = None
        elif (
            self.quote_start is not None
            and self._is_last_character(line)
            and character != QUOTE
        ):
            self.errors.append(UnterminatedStringError(line_idx + 1))

    def _add_number(self, line_idx: int) -> None:
        self.tokens.append(
            Token(
                TokenType.NUMBER,
                self.digits,
                Decimal(str(float(self.digits))),
                line_idx + 1,
            )
        )
        self.digits = ""

    def _add_identifier(self, line_idx: int) -> None:
        if self.identifier in RESERVED_WORDS:
            self.tokens.append(
                Token(
                    RESERVED_WORDS[self.identifier],
                    self.identifier,
                    None,
                    line_idx + 1,
                )
            )
        else:
            self.tokens.append(
                Token(
                    TokenType.IDENTIFIER,
                    self.identifier,
                    None,
                    line_idx + 1,
                )
            )
        self.identifier = ""
