from Token import Token
#############
# ! NODES ! #
#############

class NumberNode:
    def __init__(self, token : Token) -> None:
        self.token = token

        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end
    
    def __repr__(self) -> str:
        return f'{self.token}'

class StringNode:
    def __init__(self, token : Token) -> None:
        self.token = token

        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end
    
    def __repr__(self) -> str:
        return f'{self.token}'

class BinOpNode:
    def __init__(self, left_node, op_token : Token, right_node) -> None:
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end
    
    def __repr__(self) -> str:
        return f'({self.left_node}, {self.op_token}, {self.right_node})'

class UnaryOpNode:
    def __init__(self, op_token, node) -> None:
        self.op_token = op_token
        self.node = node

        self.pos_start = self.op_token.pos_start
        self.pos_end = node.pos_end
    
    def __repr__(self) -> str:
        return f'({self.op_token}, {self.node})'

class VarAssignNode:
    def __init__(self, var_name_token : Token, value_node : BinOpNode | UnaryOpNode | NumberNode) -> None:
        self.var_name_token = var_name_token
        self.value_node = value_node

        self.pos_start = var_name_token.pos_start
        self.pos_end = value_node.pos_end

class VarAccessNode:
    def __init__(self, var_name_token : Token) -> None:
        self.var_name_token = var_name_token

        self.pos_start = var_name_token.pos_start
        self.pos_end = var_name_token.pos_end
    
class IfNode:
    def __init__(self,cases : tuple[BinOpNode, BinOpNode], else_case : BinOpNode) -> None:
        self.cases = cases
        self.else_case = else_case

        self.pos_start = cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[-1][0]).pos_end

class ForNode:
    def __init__(self, var_name_token : BinOpNode, start_value_node : BinOpNode, end_value_node : BinOpNode, step_value_node : BinOpNode, body_node : BinOpNode) -> None:
        self.var_name_token = var_name_token
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node

        self.pos_start = var_name_token.pos_start
        self.pos_end = body_node.pos_end

class WhileNode:
    def __init__(self, condition_node : BinOpNode, body_node : BinOpNode) -> None:
        self.condition_node = condition_node
        self.body_node = body_node

        self.pos_start = condition_node.pos_start
        self.pos_end = body_node.pos_end

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

class CallNode:
    def __init__(self, name_node, args_nodes : list[BinOpNode]) -> None:
        self.name_node = name_node
        self.args_nodes = args_nodes

        self.pos_start = name_node.pos_start

        if len(args_nodes) > 0:
            self.pos_end = args_nodes[-1].pos_end
        else:
            self.pos_end = name_node.pos_end

class ListNode:
    def __init__(self, elements_nodes, pos_start, pos_end) -> None:
        self.elements_nodes = elements_nodes

        self.pos_start = pos_start
        self.pos_end = pos_end