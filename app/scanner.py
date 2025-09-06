from app.errors import TokenError
from app.tokenization import Token, TOKEN_MAPPING, TokenType, COMMENT, SPACE, TAB


class Scanner:
    def __init__(self, source: str):
        self.source_lines: list[str] = source.splitlines()
        self.tokens: list[Token] = []
        self.errors: list[TokenError] = []

    def scan_tokens(self) -> tuple[list[Token], list[TokenError]]:
        for line_idx, line in enumerate(self.source_lines):
            position_start = 0
            while position_start < len(line):
                character = line[position_start]

                # Check for two-character tokens
                if position_start + 1 < len(line):
                    two_chars = character + line[position_start + 1]
                    if two_chars == COMMENT:
                        # If we see the comment we ignore the whole remaining line
                        break

                    if two_chars in TOKEN_MAPPING:
                        self.tokens.append(Token(TOKEN_MAPPING[two_chars], two_chars, None, line_idx + 1))
                        position_start += 2
                        continue

                # Handle single-character tokens
                if character in TOKEN_MAPPING:
                    self.tokens.append(Token(TOKEN_MAPPING[character], character, None, line_idx + 1))
                elif character in [SPACE, TAB]:
                    pass  # Ignore whitespace characters
                else:
                    self.errors.append(TokenError(character, line_idx + 1))

                position_start += 1

        self.tokens.append(Token(TokenType.EOF, "", None, len(self.source_lines)))
        return self.tokens, self.errors
