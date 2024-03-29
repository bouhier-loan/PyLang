from Nodes.BinOp import BinOpNode


class WhileNode:
    def __init__(self, condition_node : BinOpNode, body_node : BinOpNode) -> None:
        self.condition_node = condition_node
        self.body_node = body_node

        self.pos_start = condition_node.pos_start
        self.pos_end = body_node.pos_end
    
    def __repr__(self) -> str:
        return f"while {self.condition_node} {'{'}{self.body_node}{'}'}"
