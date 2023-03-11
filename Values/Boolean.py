from __future__ import annotations

from Errors.RunTimeError import RTError
from Values.Value import Value


class Boolean(Value):
    def __init__(self, value : str) -> None:
        super().__init__()
        self.value = value

    def get_comparison_eq(self, other : Boolean) -> tuple[Boolean, RTError]:
        if isinstance(other, Boolean):
            return Boolean(self.value == other.value).set_context(self.context), None
        return None, Value.illegal_operation(self, other)
    
    def get_comparison_ne(self, other : Boolean) -> tuple[Boolean, RTError]:
        if isinstance(other, Boolean):
            return Boolean(self.value != other.value).set_context(self.context), None
        return None, Value.illegal_operation(self, other)
    
    def get_and(self, other : Boolean) -> tuple[Boolean, RTError]:
        if isinstance(other, Boolean):
            return Boolean(self.value and other.value).set_context(self.context), None
        return None, Value.illegal_operation(self, other)
    
    def get_or(self, other : Boolean) -> tuple[Boolean, RTError]:
        if isinstance(other, Boolean):
            return Boolean(self.value or other.value).set_context(self.context), None
        return None, Value.illegal_operation(self, other)
    
    def not_comp(self) -> tuple[Boolean, RTError]:
        return Boolean(not self.value).set_context(self.context), None
    
    def is_true(self) -> bool:
        return self.value
    
    def copy(self) -> Boolean:
        copy = Boolean(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __str__(self) -> str:
        return f"{self.value}"
    
    def __repr__(self) -> str:
        return f'{self.value if self.value else ""}'