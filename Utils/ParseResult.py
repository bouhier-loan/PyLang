from __future__ import annotations

from Errors.Error import Error
from Nodes.BinOp import BinOpNode
from Nodes.Number import NumberNode

#####################
# ! PARSER RESULT ! #
#####################

class ParseResult:
    def __init__(self) -> None:
        self.error = None
        self.node = None
        self.last_registered_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advance(self):
        self.last_registered_advance_count = 1
        self.advance_count += 1
    
    def register(self, result) -> ParseResult | BinOpNode | NumberNode:
        self.last_registered_advance_count = result.advance_count
        self.advance_count += result.advance_count
        if result.error: self.error = result.error
        return result.node

    def try_register(self, result) -> ParseResult | BinOpNode | NumberNode:
        if result.error:
            self.to_reverse_count += result.advance_count
            return None
        return self.register(result)

    def success(self, node) -> ParseResult:
        self.node = node
        return self

    def failure(self, error : Error) -> ParseResult:
        if not self.error or self.advance_count == 0:
            self.error = error
        return self
