from Utils.Token import Token


class BinOpNode:
    def __init__(self, left_node, op_token : Token, right_node) -> None:
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end
    
    def __repr__(self) -> str:
        return f'({self.left_node}, {self.op_token}, {self.right_node})'