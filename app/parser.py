from app.tokenization import Token
from app.tree import Tree


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens

    def parse(self) -> Tree:
        tree = Tree(None, True) # create a root node
        for token in self.tokens:
            tree.add_child(token)
        return tree
