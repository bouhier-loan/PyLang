from __future__ import annotations
from Values.Number import Number
from Values.String import String
from Values.List import List
from Values.Functions.BaseFunction import BaseFunction
from Values.Value import Value

from Nodes.BinOp import BinOpNode
from Nodes.UnaryOp import UnaryOpNode
from Nodes.Number import NumberNode
from Nodes.String import StringNode
from Nodes.List import ListNode
from Nodes.VarAccess import VarAccessNode
from Nodes.If import IfNode
from Nodes.VarAssign import VarAssignNode
from Nodes.For import ForNode
from Nodes.FuncDef import FuncDefNode
from Nodes.Call import CallNode
from Nodes.While import WhileNode

from Utils.Context import Context
from Utils.Token import Token
from Utils.RTResult import RTResult

from Core.Constants import *

from Errors.RunTimeError import RTError

###################
# ! INTERPRETER ! #
###################
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

###################
# ! INTERPRETER ! #
###################
class Interpreter:
    def visit(self, node, context : Context) -> RTResult:
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)
    
    def no_visit_method(self, node, context : Context) -> Exception:
        raise Exception(f'No visit_{type(node).__name__} method defined')
    
    ######

    def visit_NumberNode(self, node : NumberNode, context : Context) -> RTResult:
        return RTResult().success(
            Number(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_StringNode(self, node : StringNode, context : Context) -> RTResult:
        return RTResult().success(
            String(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_ListNode(self, node : ListNode, context : Context) -> RTResult:
        result = RTResult()
        elements = []

        for element_node in node.elements_nodes:
            elements.append(result.register(self.visit(element_node, context)))
            if result.error: return result
        
        return result.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_BinOpNode(self, node : BinOpNode, context : Context) -> RTResult:
        result = RTResult()
        left = result.register(self.visit(node.left_node, context))
        if result.error: return result
        right = result.register(self.visit(node.right_node, context))
        if result.error: return result

        methods = {
            TT_PLUS     : left.add, 
            TT_MINUS    : left.subtract, 
            TT_MUL      : left.multiply, 
            TT_DIV      : left.divide, 
            TT_POW      : left.power,
            TT_MOD      : left.modulo,
            TT_QUO      : left.quotient,
            TT_EE       : left.get_comparison_eq,
            TT_NE       : left.get_comparison_ne,
            TT_LT       : left.get_comparison_lt,
            TT_GT       : left.get_comparison_gt,
            TT_LTE      : left.get_comparison_lte,
            TT_GTE      : left.get_comparison_gte,
            TT_AND      : left.get_and,
            TT_OR       : left.get_or,
            }

        method_result, error = methods[node.op_token.type](right)

        if error: return result.failure(error)
        else : return result.success(method_result.set_pos(node.pos_start, node.pos_end))
    
    def visit_UnaryOpNode(self, node : UnaryOpNode, context : Context) -> RTResult:
        result = RTResult()
        number : Number = result.register(self.visit(node.node, context))
        if result.error: return result

        error = None

        if node.op_token.type == TT_MINUS:
            number, error = number.multiply(Number(-1))
        elif node.op_token.type == TT_NOT:
            number, error = number.not_comp()

        if error: return result.failure(error)
        else: return result.success(number.set_pos(node.pos_start, node.pos_end))
    
    def visit_VarAccessNode(self, node : VarAccessNode, context : Context) -> RTResult:
        result = RTResult()
        var_name = node.var_name_token.value
        value = context.symbol_table.get(var_name)
        if not value:
            return result.failure(RTError(
                node.pos_start, node.pos_end,
                f"'{var_name}' is not defined",
                context
            ))
        
        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return result.success(value)

    def visit_VarAssignNode(self, node : VarAssignNode, context : Context) -> RTResult:
        result = RTResult()
        var_name = node.var_name_token.value
        value = result.register(self.visit(node.value_node, context))
        if result.error: return result

        context.symbol_table.set(var_name, value)
        return result.success(value)

    def visit_IfNode(self, node : IfNode, context : Context) -> RTResult:
        #?print('visit_IfNode')
        result = RTResult()

        #?print('> Node cases - ' + str(node.cases))
        for condition, expression in node.cases:
            condition_value = result.register(self.visit(condition, context))
            if result.error: return result

            if condition_value.is_true():
                expr_value = result.register(self.visit(expression, context))
                if result.error: return result
                return result.success(expr_value)
        
        if node.else_case:
            else_value = result.register(self.visit(node.else_case, context))
            if result.error: return result
            return result.success(else_value)
        return result.success(None)
    
    def visit_ForNode(self, node : ForNode, context : Context) -> RTResult:
        result = RTResult()
        elements = []

        start_value = result.register(self.visit(node.start_value_node, context))
        if result.error: return result

        end_value = result.register(self.visit(node.end_value_node, context))
        if result.error: return result

        if node.step_value_node:
            step_value = result.register(self.visit(node.step_value_node, context))
            if result.error: return result
        else:
            step_value = Number(1 if start_value.value < end_value.value else -1)
        
        i = start_value.value

        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value
        
        while condition():
            context.symbol_table.set(node.var_name_token.value, Number(i))
            i += step_value.value

            elements.append(result.register(self.visit(node.body_node, context)))
            if result.error: return result
        
        return result.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_WhileNode(self, node : WhileNode, context : Context) -> RTResult:
        result = RTResult()
        elements = []

        while True:
            condition = result.register(self.visit(node.condition_node, context))
            if result.error: return result

            if not condition.is_true(): break

            elements.append(result.register(self.visit(node.body_node, context)))
            if result.error: return result

        return result.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_FuncDefNode(self, node : FuncDefNode, context : Context) -> RTResult:
        result = RTResult()

        func_name = node.var_name_token.value if node.var_name_token else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_tokens]

        func_value = Function(func_name, body_node, arg_names).set_context(context).set_pos(node.pos_start, node.pos_end)

        if node.var_name_token:
            context.symbol_table.set(func_name, func_value)

        return result.success(func_value)

    def visit_CallNode(self, node : CallNode, context : Context) -> RTResult:
        result = RTResult()
        args = []

        value_to_call = result.register(self.visit(node.name_node, context))
        if result.error: return result

        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.args_nodes:
            args.append(result.register(self.visit(arg_node, context)))
            if result.error: return result
        
        return_value = result.register(value_to_call.execute(args))
        if result.error: return result

        return result.success(return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context))