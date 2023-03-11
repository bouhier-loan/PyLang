from __future__ import annotations

from Errors.RunTimeError import RTError
from Utils.Token import Token
from Values.Number import Number
from Values.Value import Value


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
    
    def get(self, index : Number) -> tuple[Value, RTError]:
        if isinstance(index, Number):
            try:
                return self.elements[index.value], None
            except:
                return None, RTError(index.pos_start, index.pos_end, f'Index {index.value} out of range', self.context)
        return None, Value.illegal_operation(self, index)
    
    def get_slice(self, start : Number | None, end : Number | None) -> tuple[List, RTError]:
        if isinstance(start, Number) and isinstance(end, Number):
            if start.value > len(self.elements):
                return None, RTError(start.pos_start, start.pos_end, f'Start index {start.value} out of range', self.context)
            if end.value > len(self.elements):
                return None, RTError(end.pos_start, end.pos_end, f'End index {end.value} out of range', self.context)
            new_list = self.copy()
            new_list.elements = new_list.elements[start.value:end.value]
            return new_list, None
        return None, Value.illegal_operation(self, start)
    
    def copy(self) -> List:
        copy = List(self.elements[:])
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __repr__(self) -> str:
        return f'[{", ".join([str(element) for element in self.elements])}]'