from Value import Value
from Context import Context
from Errors.RunTimeError import RTError
from RTResult import RTResult
from Token import Token

class BaseFunction(Value):
    def __init__(self, name : str) -> None:
        super().__init__()
        self.name = name or "<anonymous>"
                 
    def generate_new_context(self) -> Context:
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context
    
    def check_args(self, arg_names : list[Value], args : list[Value]) -> RTResult:
        result = RTResult()
        
        if len(args) > len(arg_names):
            return result.failure(RTError(
                self.pos_start, self.pos_end,
                f"Too many args passed into '{self.name}'!\nNeeded {len(arg_names)}, given {len(args)}",
                self.context
            ))
        elif len(args) < len(arg_names):
            return result.failure(RTError(
                self.pos_start, self.pos_end,
                f"Too few args passed into '{self.name}'!\nNeeded {len(arg_names)}, given {len(args)}",
                self.context
            ))
        return result.success(None)
    
    def populate_args(self, arg_names : list[Value], args : list[Value], execution_context : Context):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(execution_context)
            execution_context.symbol_table.set(arg_name, arg_value)
    
    def check_populate_args(self, arg_names : list[Token], args : list[Token], execution_context : Context) -> RTResult:
        result = RTResult()
        result.register(self.check_args(arg_names, args))
        if result.error: return result
        self.populate_args(arg_names, args, execution_context)
        return result.success(None)