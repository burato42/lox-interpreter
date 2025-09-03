from app.errors import TokenError
from app.tokenization import Token, TOKEN_MAPPING, TokenType


class Scanner:
    def __init__(self, source: str):
        self.source_lines: list[str] = source.splitlines()
        self.tokens: list[Token] = []
        self.errors: list[TokenError] = []

    def scan_tokens(self) -> tuple[list[Token], list[TokenError]]:
        for line_idx, line in enumerate(self.source_lines):
            for character in line:
                if character in TOKEN_MAPPING:
                    self.tokens.append(Token(TOKEN_MAPPING[character], character, None, line_idx + 1))
                else:
                    self.errors.append(TokenError(character, line_idx + 1))

        self.tokens.append(Token(TokenType.EOF, "", None, len(self.source_lines)))
        return self.tokens, self.errors
