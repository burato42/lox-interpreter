from typing import Optional

from app.tokenization import Token, TokenType

class Node:
    def __init__(self, token: Optional[Token] = None, is_root: bool = False):
        self.token = token
        self.is_root = is_root
        self.children: list[Node] = []

    @property
    def value(self) -> str:
        if not self.token or self.is_root:
            return ""
        elif self.token.type == TokenType.TRUE:
            return self.token.lexeme
        elif self.token.type == TokenType.FALSE:
            return self.token.lexeme
        elif self.token.type == TokenType.NIL:
            return self.token.lexeme
        elif self.token.type == TokenType.NUMBER:
            return str(self.token.literal)
        elif self.token.type == TokenType.STRING:
            return self.token.literal
        elif self.token.type == TokenType.LEFT_PAREN:
            return self.token.lexeme + "group "
        elif self.token.type == TokenType.RIGHT_PAREN:
            return self.token.lexeme

        return ""


class Tree:
    def __init__(self, token: Optional[Token] = None, is_root: bool = False):
        self.node = Node(token, is_root)

    def print(self):
        if not self.node.is_root: # root is a dummy value, no need to print
            print(self.node)

        for child in self.node.children:
            print(child)

    def add_child(self, child_value: Token):
        self.node.children.append(Node(child_value))


    def traverse(self, node: Optional[Node] = None) -> list[Optional[Node]]:
        if node is None:
            node = self.node

        if not node:
            return []

        if node.is_root:
            result = []
        else:
            result = [node]

        for child in node.children:
            result.extend(self.traverse(child))

        return result
