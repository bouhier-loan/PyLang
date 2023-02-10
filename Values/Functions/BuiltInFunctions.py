from __future__ import annotations

import math
import os

from Errors.RunTimeError import RTError
from Utils.Context import Context
from Utils.RTResult import RTResult
from Utils.Token import Token
from Values.Functions.BaseFunction import BaseFunction
from Values.List import List
from Values.Number import Number
from Values.String import String


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
        is_string = type(exec_context.symbol_table.get('value').value) == str
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