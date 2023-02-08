from Errors.RunTimeError import RTError
from Position import Position
from Context import Context
##############
# ! VALUES ! #
##############

class Value:
    def __init__(self) -> None:
        self.set_pos()
        self.set_context()
    
    def set_pos(self, pos_start : Position = None, pos_end : Position = None) -> Value:
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def set_context(self, context: Context = None) -> Value:
        self.context = context
        return self
    
    def add(self, other : Number) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def subtract(self, other : Number) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def multiply(self, other : Number) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def divide(self, other : Number) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def modulo(self, other : Number) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def quotient(self, other : Number) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
        
    def power(self, other) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def copy(self) -> Exception:
        raise Exception("No copy method defined")
    
    def get_comparison_eq(self, other) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def get_comparison_ne(self, other) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def get_comparison_lt(self, other) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def get_comparison_gt(self, other) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def get_comparison_lte(self, other) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def get_comparison_gte(self, other) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def get_and(self, other) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
        
    def get_or(self, other) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def not_comp(self) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def is_true(self) -> bool:
        return False
    
    def illegal_operation(self, other = None) -> RTError:
        if not other: other = self
        return RTError(
            self.pos_start, self.pos_end,
            "Illegal operation",
            self.context
        )