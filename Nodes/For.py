from Nodes.BinOp import BinOpNode


class ForNode:
    def __init__(self, var_name_token : BinOpNode, start_value_node : BinOpNode, end_value_node : BinOpNode, step_value_node : BinOpNode, body_node : BinOpNode) -> None:
        self.var_name_token = var_name_token
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node

        self.pos_start = var_name_token.pos_start
        self.pos_end = body_node.pos_end
    
    def __repr__(self) -> str:
        return f"for {self.var_name_token} = {self.start_value_node} to {self.end_value_node} {f'step {self.step_value_node}' if self.step_value_node else ''} {'{'}{self.body_node}{'}'}"
