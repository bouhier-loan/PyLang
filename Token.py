from Position import Position
##############
# ! TOKENS ! #
##############

class Token:
    def __init__(self, type_ : str, value = None, pos_start : Position = None, pos_end : Position = None) -> None:
        self.type = type_
        self.value = value
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        
        if pos_end:
            self.pos_end = pos_end

    def __repr__(self) -> str:
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
    
    def matches(self,  type_ : str, value : str) -> bool:
        return self.type == type_ and self.value == value