from __future__ import annotations

from Errors.RunTimeError import RTError
from Values.Value import Value


class ImportModule(Value):
    def __init__(self, value : str) -> None:
        super().__init__()
        self.value = value

    def copy(self) -> ImportModule:
        copy = ImportModule(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __str__(self) -> str:
        return f"{self.value}"
    
    def __repr__(self) -> str:
        return f'"{self.value}"'