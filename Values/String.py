from __future__ import annotations

from Errors.RunTimeError import RTError

from Values.Boolean import Boolean
from Values.Number import Number
from Values.Value import Value


class String(Value):
    def __init__(self, value : str) -> None:
        super().__init__()
        self.value = value

    def add(self, other : String) -> tuple[String, RTError]:
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        return None, Value.illegal_operation(self, other)
    
    def multiply(self, other : Number) -> tuple[String, RTError]:
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        return None, Value.illegal_operation(self, other)
    
    def get_comparison_eq(self, other : String) -> tuple[Boolean, RTError]:
        if isinstance(other, String):
            return Boolean(self.value == other.value).set_context(self.context), None
        return None, Value.illegal_operation(self, other)
    
    def get_comparison_ne(self, other : String) -> tuple[Boolean, RTError]:
        if isinstance(other, String):
            return Boolean(self.value != other.value).set_context(self.context), None
        return None, Value.illegal_operation(self, other)
    
    def get_comparison_lt(self, other : String) -> tuple[Boolean, RTError]:
        if isinstance(other, String):
            return Boolean(self.value < other.value).set_context(self.context), None
        return None, Value.illegal_operation(self, other)
    
    def get_comparison_gt(self, other : String) -> tuple[Boolean, RTError]:
        if isinstance(other, String):
            return Boolean(self.value > other.value).set_context(self.context), None
        return None, Value.illegal_operation(self, other)
    
    def get_comparison_lte(self, other : String) -> tuple[Boolean, RTError]:
        if isinstance(other, String):
            return Boolean(self.value <= other.value).set_context(self.context), None
        return None, Value.illegal_operation(self, other)
    
    def get_comparison_gte(self, other : String) -> tuple[Boolean, RTError]:
        if isinstance(other, String):
            return Boolean(self.value >= other.value).set_context(self.context), None
        return None, Value.illegal_operation(self, other)
    
    def is_true(self) -> bool:
        return len(self.value) > 0
    
    def get(self, index : Number) -> tuple[String, RTError]:
        if isinstance(index, Number):
            try:
                return String(self.value[index.value]).set_context(self.context), None
            except:
                return None, RTError(index.pos_start, index.pos_end, f'Index {index.value} out of range', self.context)
        return None, Value.illegal_operation(self, index)

    def get_slice(self, start : Number, end : Number) -> tuple[String, RTError]:
        if start == None:
            start = Number(0)
        if end == None:
            end = Number(len(self.value))
        if isinstance(start, Number) and isinstance(end, Number):
            try:
                return String(self.value[start.value:end.value]).set_context(self.context), None
            except:
                return None, RTError(start.pos_start, end.pos_end, 'Slice index out of range', self.context)
        return None, Value.illegal_operation(self, start)
    
    def copy(self) -> String:
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __str__(self) -> str:
        return f"{self.value}"
    
    def __repr__(self) -> str:
        return f'"{self.value}"'