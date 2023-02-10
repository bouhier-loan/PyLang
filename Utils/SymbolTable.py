from __future__ import annotations

####################
# ! SYMBOL TABLE ! #
####################

class SymbolTable:
    def __init__(self, parent : SymbolTable = None) -> None:
        self.symbols = {}
        self.parent = parent

    def get(self, name : str):
        value = self.symbols.get(name, None)

        if value == None and self.parent:
            return self.parent.get(name)
        return value
    
    def set(self, name : str, value) -> None:
        self.symbols[name] = value
    
    def remove(self, name : str) -> None:
        del self.symbols[name]