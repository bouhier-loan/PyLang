from Token import Token

class UnaryOpNode:
    def __init__(self, op_token, node) -> None:
        self.op_token = op_token
        self.node = node

        self.pos_start = self.op_token.pos_start
        self.pos_end = node.pos_end
    
    def __repr__(self) -> str:
        return f'({self.op_token}, {self.node})'