from __future__ import annotations
from Token import Token
from Nodes.BinOp import BinOpNode
from Value import Value
from RTResult import RTResult
from Interpreter import Interpreter
from BaseFunction import BaseFunction

class Function(BaseFunction):
    def __init__(self, name : Token, body_node : BinOpNode, arg_names : list[Token]) -> None:
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names

    def execute(self, args : list[Value]) -> RTResult:
        result = RTResult()
        interpreter = Interpreter()
        exec_context = self.generate_new_context()

        result.register(self.check_populate_args(self.arg_names, args, exec_context))
        if result.error: return result
        
        value = result.register(interpreter.visit(self.body_node, exec_context))
        if result.error: return result

        return result.success(value)
    
    def copy(self) -> Function:
        copy = Function(self.name, self.body_node, self.arg_names)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    
    def __repr__(self) -> str:
        return f'<function {self.name}>'