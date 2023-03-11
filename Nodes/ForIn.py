from Nodes.BinOp import BinOpNode

class ForInNode:
    def __init__(self, var_name_token : BinOpNode, iterated_value : BinOpNode, body_node : BinOpNode) -> None:
        self.var_name_token = var_name_token
        self.iterated_value_node = iterated_value
        self.body_node = body_node

        self.pos_start = var_name_token.pos_start
        self.pos_end = body_node.pos_end
    
    def __repr__(self) -> str:
        return f"for {self.var_name_token} in {self.iterated_value_node} {'{'}{self.body_node}{'}'}"
