from Utils.Token import Token
from Nodes.BinOp import BinOpNode

class FuncDefNode:
    def __init__(self, var_name_token : Token, arg_name_tokens : list[Token], body_node : BinOpNode) -> None:
        self.var_name_token = var_name_token
        self.arg_name_tokens = arg_name_tokens
        self.body_node = body_node

        if var_name_token:
            self.pos_start = var_name_token.pos_start
        elif len(arg_name_tokens) > 0:
            self.pos_start = arg_name_tokens[0].pos_start
        else:
            self.pos_start = body_node.pos_start

        self.pos_end = body_node.pos_end