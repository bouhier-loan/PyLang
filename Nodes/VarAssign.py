from Token import Token
from BinOp import BinOpNode
from UnaryOp import UnaryOpNode
from Number import NumberNode

class VarAssignNode:
    def __init__(self, var_name_token : Token, value_node : BinOpNode | UnaryOpNode | NumberNode) -> None:
        self.var_name_token = var_name_token
        self.value_node = value_node

        self.pos_start = var_name_token.pos_start
        self.pos_end = value_node.pos_end