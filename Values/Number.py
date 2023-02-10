from __future__ import annotations

from Errors.RunTimeError import RTError
from Utils.Context import Context
from Utils.Position import Position
from Values.Value import Value


class Number(Value):
    def __init__(self, value : int | float) -> None:
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start : Position = None, pos_end : Position = None) -> Number:
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def set_context(self, context : Context = None) -> Context:
        self.context = context
        return self

    def add(self, other : Number) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def subtract(self, other : Number) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def multiply(self, other : Number) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def divide(self, other : Number) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    "Division by zero",
                    self.context
                )
            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def modulo(self, other : Number) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    "Division by zero",
                    self.context
                )
            return Number(self.value % other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def quotient(self, other : Number) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    "Division by zero",
                    self.context
                )
            return Number(self.value // other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
        
    def power(self, other) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def copy(self) -> Number:
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def get_comparison_eq(self, other) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def get_comparison_ne(self, other) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def get_comparison_lt(self, other) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def get_comparison_gt(self, other) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def get_comparison_lte(self, other) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def get_comparison_gte(self, other) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def get_and(self, other) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
        
    def get_or(self, other) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def not_comp(self) -> tuple[Number, RTError]:
        return Number(1 if self.value == 0 else 0).set_context(self.context), None
    
    def is_true(self) -> bool:
        return self.value != 0
    
    def __repr__(self) -> str:
        return f'{self.value}'
