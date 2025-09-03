class TokenError(Exception):
    def __init__(self, character: str, line_idx: int):
        self.character = character
        self.line_idx = line_idx

    def __str__(self):
        return f"[line {self.line_idx}] Error: Unexpected character: {self.character}"
