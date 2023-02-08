from Node import NumberNode, BinOpNode
#####################
# ! PARSER RESULT ! #
#####################

class ParseResult:
    def __init__(self) -> None:
        self.error = None
        self.node = None
        self.advance_count = 0

    def register_advance(self):
        self.advance_count += 1
    
    def register(self, result) -> ParseResult | BinOpNode | NumberNode:
        self.advance_count += result.advance_count
        if result.error: self.error = result.error
        return result.node

    def success(self, node) -> ParseResult:
        self.node = node
        return self

    def failure(self, error : Error) -> ParseResult:
        if not self.error or self.advance_count == 0:
            self.error = error
        return self