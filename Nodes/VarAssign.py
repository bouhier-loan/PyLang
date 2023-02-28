from Utils.Token import Token


class VarAssignNode:
    def __init__(self, var_name_token : Token, value_node) -> None:
        self.var_name_token = var_name_token
        self.value_node = value_node

        self.pos_start = var_name_token.pos_start
        self.pos_end = value_node.pos_end
    
    def __repr__(self) -> str:
        return f"{self.var_name_token.value} = {self.value_node}"