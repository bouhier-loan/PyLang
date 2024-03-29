from __future__ import annotations

import math
from sys import argv
from os import listdir, remove
from os import path

from Values.Number import Number
from Values.String import String
from Values.List import List
from Values.BaseFunction import BaseFunction
from Values.Value import Value
from Values.Boolean import Boolean

from Nodes.BinOp import BinOpNode
from Nodes.UnaryOp import UnaryOpNode
from Nodes.Number import NumberNode
from Nodes.String import StringNode
from Nodes.List import ListNode
from Nodes.VarAccess import VarAccessNode
from Nodes.If import IfNode
from Nodes.VarAssign import VarAssignNode
from Nodes.For import ForNode
from Nodes.ForIn import ForInNode
from Nodes.FuncDef import FuncDefNode
from Nodes.Call import CallNode
from Nodes.While import WhileNode
from Nodes.Return import ReturnNode
from Nodes.Break import BreakNode
from Nodes.Continue import ContinueNode
from Nodes.Import import ImportNode

from Utils.Context import Context
from Utils.Token import Token
from Utils.RTResult import RTResult
from Utils.SymbolTable import SymbolTable

from Errors.RunTimeError import RTError
from Errors.Error import Error


from Core.Constants import *
from Core.Lexer import Lexer
from Core.Parser import Parser

#################
# ! FUNCTIONS ! #
#################
class BuiltInFunction(BaseFunction):
    def __init__(self, name : Token) -> None:
        super().__init__(name)

    def execute(self, args : list[Token]) -> RTResult:
        result = RTResult()
        exec_context = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        result.register(self.check_populate_args(method.arg_names, args, exec_context))
        if result.error: return result

        return_value = result.register(method(exec_context))
        if result.error: return result

        return result.success(return_value)

    def no_visit_method(self) -> Exception:
        raise Exception(f'No execute_{self.name} method defined')
    
    def copy(self) -> BuiltInFunction:
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    
    def __repr__(self) -> str:
        return f'<built-in function {self.name}> '
    
    ########################

    def execute_print(self, exec_context : Context) -> RTResult:
        print(str(exec_context.symbol_table.get('value')), end='')
        return RTResult().success(Boolean.null)
    execute_print.arg_names = {"value" : String("")}

    def execute_println(self, exec_context : Context) -> RTResult:
        print(str(exec_context.symbol_table.get('value')))
        return RTResult().success(Boolean.null)
    execute_println.arg_names = {"value" : String("")}

    def execute_string(self, exec_context : Context) -> RTResult:
        try:
            text = str(exec_context.symbol_table.get('value').value)
        except ValueError:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                f"Cannot convert {exec_context.symbol_table.get('value').type} to STR",
                exec_context
            ))
        return RTResult().success(String(text))
    execute_string.arg_names = {"value" : None}

    def execute_int(self, exec_context : Context) -> RTResult:
        try:
            number = int(exec_context.symbol_table.get('value').value)
        except ValueError:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                f"Cannot convert {exec_context.symbol_table.get('value').type} to INT",
                exec_context
            ))
        return RTResult().success(Number(number))
    execute_int.arg_names = {"value" : None}

    def execute_float(self, exec_context : Context) -> RTResult:
        try:
            number = float(exec_context.symbol_table.get('value').value)
        except ValueError:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                f"Cannot convert {exec_context.symbol_table.get('value').type} to FLOAT",
                exec_context
            ))
        return RTResult().success(Number(number))
    execute_float.arg_names = {"value" : None}

    def execute_input(self, exec_context : Context) -> RTResult:
        text = input(exec_context.symbol_table.get('value').value)
        return RTResult().success(String(text))
    execute_input.arg_names = {"value" : String("")}

    def execute_clear(self, exec_context : Context) -> RTResult:
        os.system('cls' if os.name == 'nt' else 'clear')
        return RTResult().success(Boolean.null)
    execute_clear.arg_names = {}

    def execute_append(self, exec_context : Context) -> RTResult:
        list = exec_context.symbol_table.get('list')
        value = exec_context.symbol_table.get('value')

        if not isinstance(list, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be a LIST",
                exec_context
            ))
        
        list.elements.append(value)

        return RTResult().success(Boolean.null)
    execute_append.arg_names = {"list" : None, "value" : None}

    def execute_pop(self, exec_context : Context) -> RTResult:
        list = exec_context.symbol_table.get('list')
        value = exec_context.symbol_table.get('value')

        if not isinstance(list, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be LIST",
                exec_context
            ))
        
        if not isinstance(value, Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be INT",
                exec_context
            ))
        
        try:
            return_value = list.elements.pop(value.value)
        except:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Element at this index could not be removed from list because index is out of range",
                exec_context
            ))

        return RTResult().success(return_value)
    execute_pop.arg_names = {"list" : None, "value" : Number(-1)}


    def execute_extend(self, exec_context : Context) -> RTResult:
        list1 = exec_context.symbol_table.get('list1')
        list2 = exec_context.symbol_table.get('list2')

        if not isinstance(list1, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be LIST",
                exec_context
            ))
        
        if not isinstance(list2, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be LIST",
                exec_context
            ))

        list1.elements.extend(list2.elements)

        return RTResult().success(Boolean.null)
    execute_extend.arg_names = {"list1" : None, "list2"  : None}

    def execute_sqrt(self, exec_context : Context) -> RTResult:
        value = exec_context.symbol_table.get('value')

        if not isinstance(value, Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be INT or FLOAT",
                exec_context
            ))

        try:
            return_value = math.sqrt(value.value)
        except:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Math domain error: positive number expected",
                exec_context
            ))
        
        return RTResult().success(Number(return_value))
    execute_sqrt.arg_names = {"value" : None}

    def execute_len(self, exec_context : Context) -> RTResult:
        value = exec_context.symbol_table.get('value')

        if isinstance(value, List):
            return_value = len(value.elements)
            return RTResult().success(Number(return_value))

        
        elif isinstance(value, String):
            return_value = len(value.value)
            return RTResult().success(Number(return_value))
    
        return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be LIST or STRING",
                exec_context
            ))
    execute_len.arg_names = {"value" : None}

    def execute_sum(self, exec_context : Context) -> RTResult:
        list = exec_context.symbol_table.get('list')

        if not isinstance(list, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be LIST",
                exec_context
            ))
        return_value = 0
        for element in list.elements:
            if not isinstance(element, Number):
                return RTResult().failure(RTError(
                    self.pos_start, self.pos_end,
                    "Elements of list must be INT or FLOAT",
                    exec_context
                ))
            return_value += element.value
        return RTResult().success(Number(return_value))
    execute_sum.arg_names = {"list" : None}

    def execute_run(self, exec_context : Context) -> RTResult:
        file = exec_context.symbol_table.get('file')

        if not isinstance(file, String):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be STRING",
                exec_context
            ))
        
        file = file.value
        file_path = path.dirname(exec_context.symbol_table.get("__file__").value) + "/"
        file = file_path + file.value.replace('.', '/') + '.pyl'

        try:
            with open(file, "r") as f:
                script = f.read()
            
        except Exception as e:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                f"Failed to load script \"{file}\"\n" + str(e),
                exec_context
            ))
        
        _, error = _run(file, script)

        if error:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                f"Failed to finish executing script \"{file}\"\n" + error.as_string(),
                exec_context
            ))
        
        return RTResult().success(Boolean.null)
    execute_run.arg_names = {"file" : None}

    def execute_type(self, exec_context : Context) -> RTResult:
        value = exec_context.symbol_table.get('value')

        dict = {
            Number : "number",
            String : "str",
            List : "list",
            BaseFunction : "function",
            BuiltInFunction : "function",
            Boolean.null : "null",
            Boolean : "bool",
        }

        return_value = dict[type(value)]
        if return_value == "number":
            if type(value.value) == int:
                return_value = "int"
            else:
                return_value = "float"
        return RTResult().success(String(return_value))
    execute_type.arg_names = {"value" : None}

    def execute_upper(self, exec_context : Context) -> RTResult:
        value = exec_context.symbol_table.get('value')

        if not isinstance(value, String):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be STRING",
                exec_context
            ))
        
        return_value = value.value.upper()
        return RTResult().success(String(return_value))
    execute_upper.arg_names = {"value" : None}

    def execute_lower(self, exec_context : Context) -> RTResult:
        value = exec_context.symbol_table.get('value')

        if not isinstance(value, String):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be STRING",
                exec_context
            ))
        
        return_value = value.value.lower()
        return RTResult().success(String(return_value))
    execute_lower.arg_names = {"value" : None}

    def execute_range(self, exec_context : Context) -> RTResult:
        arg1 = exec_context.symbol_table.get('arg1')
        arg2 = exec_context.symbol_table.get('arg2')
        step = exec_context.symbol_table.get('step')

        if not isinstance(arg1, Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be INT or FLOAT",
                exec_context
            ))

        if arg2 == Boolean.null:
            arg2 = arg1
            arg1 = Number(0)

        elif not isinstance(arg2, Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be INT or FLOAT",
                exec_context
            ))

        if step == Boolean.null:
            step = Number(1)
        elif not isinstance(step, Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Third argument must be INT or FLOAT",
                exec_context
            ))
        
        if step.value == 0:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Third argument cannot be 0",
                exec_context
            ))
        
        return_value = []
        if step.value > 0:
            i = arg1.value
            while i < arg2.value:
                return_value.append(Number(i))
                i += step.value
        else:
            i = arg1.value
            while i > arg2.value:
                return_value.append(Number(i))
                i += step.value
        return RTResult().success(List(return_value))
    execute_range.arg_names = {"arg1" : None, "arg2" : Boolean.null, "step" : Boolean.null}

class Function(BaseFunction):
    def __init__(self, name : Token, body_node : BinOpNode, arg_names : dict, auto_return) -> None:
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.auto_return = auto_return

    def execute(self, args : dict) -> RTResult:
        result = RTResult()
        interpreter = Interpreter()
        exec_context = self.generate_new_context()

        result.register(self.check_populate_args(self.arg_names, args, exec_context))
        if result.should_return(): return result
        
        value = result.register(interpreter.visit(self.body_node, exec_context))
        if result.should_return() and result.func_return_value == None: return result

        return_value = (value if self.auto_return else None) or result.func_return_value or Boolean.null

        return result.success(return_value)
    
    def copy(self) -> Function:
        copy = Function(self.name, self.body_node, self.arg_names, self.auto_return)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    
    def __repr__(self) -> str:
        return f'<function {self.name}>'


# Builtin functions
BuiltInFunction.print               = BuiltInFunction("print")
BuiltInFunction.println             = BuiltInFunction("println")
BuiltInFunction.string              = BuiltInFunction("string")
BuiltInFunction.int                 = BuiltInFunction("int")
BuiltInFunction.float               = BuiltInFunction("float")
BuiltInFunction.input               = BuiltInFunction("input")
BuiltInFunction.clear               = BuiltInFunction("clear")
BuiltInFunction.append              = BuiltInFunction("append")
BuiltInFunction.pop                 = BuiltInFunction("pop")
BuiltInFunction.extend              = BuiltInFunction("extend")
BuiltInFunction.sqrt                = BuiltInFunction("sqrt")
BuiltInFunction.len                 = BuiltInFunction("len")
BuiltInFunction.sum                 = BuiltInFunction("sum")
BuiltInFunction.run                 = BuiltInFunction("run")
BuiltInFunction.type                = BuiltInFunction("type")
BuiltInFunction.upper               = BuiltInFunction("upper")
BuiltInFunction.lower               = BuiltInFunction("lower")
BuiltInFunction.range               = BuiltInFunction("range")

# Public symbol table
global_symbol_table = SymbolTable()
_FileMain = True

# * Default values *
global_symbol_table.set("null", Boolean.null)
global_symbol_table.set("False", Boolean.false)
global_symbol_table.set("false", Boolean.false)
global_symbol_table.set("True", Boolean.true)
global_symbol_table.set("true", Boolean.true)

global_symbol_table.set("int", String.int)
global_symbol_table.set("float", String.float)
global_symbol_table.set("string", String.string)
global_symbol_table.set("list", String.list)
global_symbol_table.set("function", String.function)
global_symbol_table.set("boolean", String.boolean)

# * Built in functions *
global_symbol_table.set("print", BuiltInFunction.print)
global_symbol_table.set("str", BuiltInFunction.string)
global_symbol_table.set("int", BuiltInFunction.int)
global_symbol_table.set("float", BuiltInFunction.float)
global_symbol_table.set("input", BuiltInFunction.input)
global_symbol_table.set("clear", BuiltInFunction.clear)
global_symbol_table.set("cls", BuiltInFunction.clear)
global_symbol_table.set("append", BuiltInFunction.append)
global_symbol_table.set("pop", BuiltInFunction.pop)
global_symbol_table.set("extend", BuiltInFunction.extend)
global_symbol_table.set("sqrt", BuiltInFunction.sqrt)
global_symbol_table.set("len", BuiltInFunction.len)
global_symbol_table.set("sum", BuiltInFunction.sum)
global_symbol_table.set("run", BuiltInFunction.run)
global_symbol_table.set("type", BuiltInFunction.type)
global_symbol_table.set("upper", BuiltInFunction.upper)
global_symbol_table.set("lower", BuiltInFunction.lower)
global_symbol_table.set("println", BuiltInFunction.println)
global_symbol_table.set("range", BuiltInFunction.range)


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
        # If {expr} is in string, replace it with the value of the expression
        if '{' and '}' in node.token.value:
            result = RTResult()

            string = node.token.value

            while '{' and '}' in string:
                expr = string[string.find('{') + 1 : string.find('}')]

                tokens, error = Lexer(context.display_name, expr).make_tokens()
                if error: return result.failure(error)

                ast = Parser(tokens).parse()
                if ast.error: return result.failure(ast.error)

                value = result.register(self.visit(ast.node, context))
                if result.should_return(): return result

                string = string.replace(f'{{{expr}}}', str(value.elements[0]))
            return result.success(
                String(string).set_context(context).set_pos(node.pos_start, node.pos_end)
            )
        
        return RTResult().success(
            String(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
        
    def visit_ListNode(self, node : ListNode, context : Context) -> RTResult:
        result = RTResult()
        elements = []

        for element_node in node.elements_nodes:
            elements.append(result.register(self.visit(element_node, context)))
            if result.should_return(): return result
        
        return result.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_BinOpNode(self, node : BinOpNode, context : Context) -> RTResult:
        result = RTResult()
        left = result.register(self.visit(node.left_node, context))
        if result.should_return(): return result
        right = result.register(self.visit(node.right_node, context))
        if result.should_return(): return result

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
        if result.should_return(): return result

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
        value : Value = context.symbol_table.get(var_name)

        if not value:
            return result.failure(RTError(
                node.pos_start, node.pos_end,
                f"'{var_name}' is not defined",
                context
            ))
        
        if node.slice_or_getter != None:

            if len(node.slice_or_getter) == 1:
                ope1 : Number = result.register(self.visit(node.slice_or_getter[0], context))
                if result.should_return(): return result
                value, error = value.get(ope1)
                if error: return result.failure(error)

            elif len(node.slice_or_getter) == 2:
                ope1 = node.slice_or_getter[0]
                if ope1 != None:
                    ope1 = result.register(self.visit(ope1, context))
                    if result.should_return(): return result

                ope2 = node.slice_or_getter[1]
                if ope2!= None:
                    ope2 = result.register(self.visit(ope2, context))
                    if result.should_return(): return result

                value, error = value.get_slice(ope1, ope2)
                if error: return result.failure(error)

        
        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return result.success(value)

    def visit_VarAssignNode(self, node : VarAssignNode, context : Context) -> RTResult:
        result = RTResult()
        var_name = node.var_name_token.value
        value = result.register(self.visit(node.value_node, context))
        if result.should_return(): return result

        context.symbol_table.set(var_name, value)
        return result.success(value)

    def visit_IfNode(self, node : IfNode, context : Context) -> RTResult:
        #?print('visit_IfNode')
        result = RTResult()

        #?print('> Node cases - ' + str(node.cases))
        for condition, expression in node.cases:
            condition_value = result.register(self.visit(condition, context))
            if result.should_return(): return result

            if condition_value.is_true():
                expr_value = result.register(self.visit(expression, context))
                if result.should_return(): return result
                return result.success(expr_value)
        
        if node.else_case:
            else_value = result.register(self.visit(node.else_case, context))
            if result.should_return(): return result
            return result.success(else_value)
        return result.success(None)
    
    def visit_ForNode(self, node : ForNode, context : Context) -> RTResult:
        result = RTResult()
        elements = []
        recursion_count = 0

        start_value = result.register(self.visit(node.start_value_node, context))
        if result.should_return(): return result

        end_value = result.register(self.visit(node.end_value_node, context))
        if result.should_return(): return result

        if node.step_value_node:
            step_value = result.register(self.visit(node.step_value_node, context))
            if result.should_return(): return result
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
            if recursion_count > LOOP_MAX_RECUR:
                return result.failure(RTError(
                    node.pos_start, node.pos_end,
                    f"Max recursion limit reached ({LOOP_MAX_RECUR})",
                    context
                ))
            recursion_count += 1

            value= result.register(self.visit(node.body_node, context))
            if result.should_return() and result.loop_continue == False: return result

            if result.loop_continue:
                continue

            if result.loop_break:
                break

            elements.append(value)
        
        return result.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_ForInNode(self, node : ForInNode, context : Context) -> RTResult:
        result = RTResult()
        elements = []
        recursion_count = 0

        iterated_value = result.register(self.visit(node.iterated_value_node, context))
        if result.should_return(): return result

        if isinstance(iterated_value, String):
            iterated_value = List([String(char) for char in iterated_value.value])
            
        if isinstance(iterated_value, List):
            for i in range(len(iterated_value.elements)):
                context.symbol_table.set(node.var_name_token.value, iterated_value.elements[i])
                if recursion_count > LOOP_MAX_RECUR:
                    return result.failure(RTError(
                        node.pos_start, node.pos_end,
                        f"Max recursion limit reached ({LOOP_MAX_RECUR})",
                        context
                    ))
                recursion_count += 1

                value = result.register(self.visit(node.body_node, context))
                if result.should_return() and result.loop_continue == False: return result

                if result.loop_continue:
                    continue

                if result.loop_break:
                    break

                elements.append(value)
            return result.success(
                List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
            )
        else:
            return result.failure(RTError(
                node.pos_start, node.pos_end,
                f"Can't iterate over {iterated_value}",
                context
            ))

    def visit_WhileNode(self, node : WhileNode, context : Context) -> RTResult:
        result = RTResult()
        elements = []
        recursion_count = 0

        while True:
            if recursion_count > LOOP_MAX_RECUR:
                return result.failure(RTError(
                    node.pos_start, node.pos_end,
                    f"Max recursion limit reached ({LOOP_MAX_RECUR})",
                    context
                ))
            recursion_count += 1

            condition = result.register(self.visit(node.condition_node, context))
            if result.should_return(): return result

            if not condition.is_true(): break

            value = result.register(self.visit(node.body_node, context))
            if result.should_return() and result.loop_break == False and result.loop_continue == False: return result

            if result.loop_continue:
                continue

            if result.loop_break:
                break

            elements.append(value)

        return result.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_FuncDefNode(self, node : FuncDefNode, context : Context) -> RTResult:
        result = RTResult()

        func_name = node.var_name_token.value if node.var_name_token else None
        body_node = node.body_node
        arg_names = node.arg_name_tokens
        new_arg_names = {}

        for key, value in arg_names.items():
            key = key.value
            if value != Boolean.null:
                result = self.visit(value, context)
                if result.should_return(): return result
                new_arg_names[key] = result.value
            else:
                new_arg_names[key] = value

        func_value = Function(func_name, body_node, new_arg_names, node.auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)

        if node.var_name_token:
            context.symbol_table.set(func_name, func_value)

        return result.success(func_value)

    def visit_CallNode(self, node : CallNode, context : Context) -> RTResult:
        result = RTResult()
        args = []

        value_to_call = result.register(self.visit(node.name_node, context))
        if result.should_return(): return result

        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.args_nodes:
            args.append(result.register(self.visit(arg_node, context)))
            if result.should_return(): return result
        
        return_value = result.register(value_to_call.execute(args))
        if result.should_return(): return result

        return result.success(return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context))
    
    def visit_ReturnNode(self, node : ReturnNode, context : Context) -> RTResult:
        result = RTResult()

        if node.return_node:
            value = result.register(self.visit(node.return_node, context))
            if result.should_return(): return result
        else:
            value = Boolean.null

        return result.success_return(value)
    
    def visit_ContinueNode(self, node : ContinueNode, context : Context) -> RTResult:
        return RTResult().success_continue()
    
    def visit_BreakNode(self, node : BreakNode, context : Context) -> RTResult:
        return RTResult().success_break()
    
    def visit_ImportNode(self, node: ImportNode, context : Context) -> RTResult:
        result = RTResult()

        file = node.module_name_token
        file_path = path.dirname(context.symbol_table.get("__file__").value) + "/"
        file = file_path + file.value.replace('.', '/') + '.pyl'

        try:
            with open(file, "r") as f:
                script = f.read()
            
        except Exception as e:
            return RTResult().failure(RTError(
                node.pos_start, node.pos_end,
                f"Failed to load script \"{file}\"\n" + str(e),
                context
            ))
        
        _, error = _run(file, script, global_symbol_table)

        if error:
            return RTResult().failure(RTError(
                node.pos_start, node.pos_end,
                f"Failed to finish executing script \"{file}\"\n {error}",
                context
            ))
        
        return result.success(Boolean.null)

###########
# ! RUN ! #
###########

def _run(file_name : str, text : str, symbol_table : SymbolTable = SymbolTable(global_symbol_table)) -> tuple[Token, Error]:
    global _FileMain
    # * Generate tokens *
    lexer = Lexer(file_name, text, GLOBAL_TESTING)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    #?print('> Tokens - ' + str(tokens))

    # * Generate AST *
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error

    #?print('> Nodes - ' + str(ast.node))

    # * Run program *
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = symbol_table
    if _FileMain:
        context.symbol_table.set('__name__', String('__main__'))
        _FileMain = False
    else:
        context.symbol_table.set('__name__', String(path.basename(file_name.strip('.pyl'))))
    context.symbol_table.set('__file__', String(path.abspath(file_name)))
    result = interpreter.visit(ast.node, context)


    return result.value, result.error
        

if __name__ == '__main__':
    args = argv
    if len(args) == 1:
        exec(open(path.dirname(args[0]) + "/shell.py").read())
    elif len(args) <= 3:
        if '-test' in args:
            args.remove('-test')
            GLOBAL_TESTING = True

        _, error = _run(args[1], open(args[1]).read())
        if error: print(error)
    
    for p in __import__('pathlib').Path(path.dirname(__file__)).rglob('*.py[co]'): p.unlink()
    for p in __import__('pathlib').Path(path.dirname(__file__)).rglob('__pycache__'): p.rmdir()
        
