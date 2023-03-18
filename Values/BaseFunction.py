from Errors.RunTimeError import RTError

from Utils.Context import Context
from Utils.RTResult import RTResult
from Utils.SymbolTable import SymbolTable
from Utils.Token import Token

from Values.Value import Value

from Core.Constants import *


class BaseFunction(Value):
    def __init__(self, name : str) -> None:
        super().__init__()
        self.name = name or "<anonymous>"
                 
    def generate_new_context(self) -> Context:
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context
    
    def check_args(self, arg_names : dict, args : list[Value]) -> RTResult:
        result = RTResult()

        minimum_args = len([0 for default_value in arg_names.values() if default_value == Boolean.null])
        
        if len(args) > len(arg_names):
            return result.failure(RTError(
                self.pos_start, self.pos_end,
                f"Too many args passed into '{self.name}'!\nNeeded {len(arg_names)}, given {len(args)}",
                self.context
            ))
        elif len(args) < minimum_args:
            return result.failure(RTError(
                self.pos_start, self.pos_end,
                f"Too few args passed into '{self.name}'!\nNeeded at least {minimum_args}, given {len(args)}",
                self.context
            ))
        return result.success(None)
    
    def populate_args(self, arg_names : dict, args : list[Value], execution_context : Context):
        for i in range(len(arg_names)):
            arg_name = list(arg_names.keys())[i]
            if i > len(args) - 1:
                arg_value = list(arg_names.values())[i]
            else:
                arg_value = args[i]
            arg_value.set_context(execution_context)
            execution_context.symbol_table.set(arg_name, arg_value)
    
    def check_populate_args(self, arg_names : dict, args : list[Token], execution_context : Context) -> RTResult:
        result = RTResult()
        result.register(self.check_args(arg_names, args))
        if result.error: return result
        self.populate_args(arg_names, args, execution_context)
        return result.success(None)