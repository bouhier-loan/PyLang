from __future__ import annotations
from Errors.RunTimeError import RTError
from Number import Number
from Value import Value

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
    
    def is_true(self) -> bool:
        return len(self.value) > 0
    
    def copy(self) -> String:
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __str__(self) -> str:
        return f"{self.value}"
    
    def __repr__(self) -> str:
        return f'"{self.value}"'