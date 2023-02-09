from __future__ import annotations
from Values.Value import Value
from Utils.Token import Token
from Errors.RunTimeError import RTError
from Values.Number import Number


class List(Value):
    def __init__(self, elements : list) -> None:
        super().__init__()
        self.elements = elements
        self.value = []
    
    def multiply(self, other : Number) -> tuple[List, RTError]:
        if isinstance(other, Number):
            new_list = self.copy()
            new_list.elements *= other.value
            return new_list, None
        return None, Value.illegal_operation(self, other)
    
    def add(self, other : List) -> tuple[List, RTError]:
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        return None, Value.illegal_operation(self, other)
    
    def copy(self) -> List:
        copy = List(self.elements[:])
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __repr__(self) -> str:
        return f'[{", ".join([str(element) for element in self.elements])}]'