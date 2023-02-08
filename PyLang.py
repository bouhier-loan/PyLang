from __future__ import annotations
import os
import math

from Constants import *







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
        print(str(exec_context.symbol_table.get('value')))
        return RTResult().success(Number.null)
    execute_print.arg_names = ["value"]

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
    execute_string.arg_names = ["value"]

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
    execute_int.arg_names = ["value"]

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
    execute_float.arg_names = ["value"]

    def execute_input(self, exec_context : Context) -> RTResult:
        text = input(exec_context.symbol_table.get('value'))
        return RTResult().success(String(text))
    execute_input.arg_names = ["value"]

    def execute_clear(self, exec_context : Context) -> RTResult:
        os.system('cls' if os.name == 'nt' else 'clear')
        return RTResult().success(Number.null)
    execute_clear.arg_names = []

    def execute_is_int(self, exec_context : Context) -> RTResult:
        is_int = type(exec_context.symbol_table.get('value').value) == int
        return RTResult().success(Number.true if is_int else Number.false)
    execute_is_int.arg_names = ["value"]

    def execute_is_float(self, exec_context : Context) -> RTResult:
        is_float = type(exec_context.symbol_table.get('value').value) == float
        return RTResult().success(Number.true if is_float else Number.false)
    execute_is_float.arg_names = ["value"]

    def execute_is_string(self, exec_context : Context) -> RTResult:
        is_string = type(exec_context.symbol_table.get('value').value) == string
        return RTResult().success(Number.true if is_string else Number.false)
    execute_is_string.arg_names = ["value"]

    def execute_is_list(self, exec_context : Context) -> RTResult:
        is_list = type(exec_context.symbol_table.get('value').value) == list
        return RTResult().success(Number.true if is_list else Number.false)
    execute_is_list.arg_names = ["value"]

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

        return RTResult().success(Number.null)
    execute_append.arg_names = ["list", "value"]

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
    execute_pop.arg_names = ["list", "value"]

    def execute_get(self, exec_context : Context) -> RTResult:
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
            return_value = list.elements[value.value]
        except:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Element at this index could not be removed from list because index is out of range",
                exec_context
            ))
        
        return RTResult().success(return_value)
    execute_get.arg_names = ["list", "value"]

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

        return RTResult().success(Number.null)
    execute_extend.arg_names = ["list1", "list2"]

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
    execute_sqrt.arg_names = ["value"]

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
    execute_len.arg_names = ["value"]

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
    execute_sum.arg_names = ["list"]


BuiltInFunction.print               = BuiltInFunction("print")
BuiltInFunction.string              = BuiltInFunction("string")
BuiltInFunction.int                 = BuiltInFunction("int")
BuiltInFunction.float               = BuiltInFunction("float")
BuiltInFunction.input               = BuiltInFunction("input")
BuiltInFunction.clear               = BuiltInFunction("clear")
BuiltInFunction.is_int              = BuiltInFunction("is_int")
BuiltInFunction.is_float            = BuiltInFunction("is_float")
BuiltInFunction.is_string           = BuiltInFunction("is_string")
BuiltInFunction.is_list             = BuiltInFunction("is_list")
BuiltInFunction.append              = BuiltInFunction("append")
BuiltInFunction.pop                 = BuiltInFunction("pop")
BuiltInFunction.get                 = BuiltInFunction("get")
BuiltInFunction.extend              = BuiltInFunction("extend")
BuiltInFunction.sqrt                = BuiltInFunction("sqrt")
BuiltInFunction.len                 = BuiltInFunction("len")
BuiltInFunction.sum                 = BuiltInFunction("sum")


###################
# ! INTERPRETER ! #
###################

class Interpreter:
    def visit(self, node : BinOpNode | UnaryOpNode | NumberNode, context : Context) -> RTResult:
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
        result = RTResult()

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

        value_to_call : Function = result.register(self.visit(node.name_node, context))
        if result.error: return result

        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.args_nodes:
            args.append(result.register(self.visit(arg_node, context)))
            if result.error: return result
        
        return_value = result.register(value_to_call.execute(args))
        if result.error: return result

        return result.success(return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context))


###########
# ! RUN ! #
###########

global_symbol_table = SymbolTable()

# * Default values *
global_symbol_table.set("null", Number.null)
global_symbol_table.set("False", Number.false)
global_symbol_table.set("false", Number.false)
global_symbol_table.set("True", Number.true)
global_symbol_table.set("true", Number.true)

# * Built in functions *
global_symbol_table.set("print", BuiltInFunction.print)
global_symbol_table.set("string", BuiltInFunction.string)
global_symbol_table.set("int", BuiltInFunction.int)
global_symbol_table.set("float", BuiltInFunction.float)
global_symbol_table.set("input", BuiltInFunction.input)
global_symbol_table.set("clear", BuiltInFunction.clear)
global_symbol_table.set("cls", BuiltInFunction.clear)
global_symbol_table.set("is_int", BuiltInFunction.is_int)
global_symbol_table.set("is_float", BuiltInFunction.is_float)
global_symbol_table.set("is_list", BuiltInFunction.is_list)
global_symbol_table.set("is_string", BuiltInFunction.is_string)
global_symbol_table.set("append", BuiltInFunction.append)
global_symbol_table.set("pop", BuiltInFunction.pop)
global_symbol_table.set("get_value", BuiltInFunction.get)
global_symbol_table.set("extend", BuiltInFunction.extend)
global_symbol_table.set("sqrt", BuiltInFunction.sqrt)
global_symbol_table.set("len", BuiltInFunction.len)
global_symbol_table.set("sum", BuiltInFunction.sum)


def run(file_name : str, text : str) -> tuple[Token, Error]:
    # * Generate tokens *
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    #?print(tokens)

    # * Generate AST *
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error


    # * Run program *
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)


    return result.value, result.error