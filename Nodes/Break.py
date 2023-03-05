from Utils.Token import Token
from Utils.Position import Position


class BreakNode:
    def __init__(self, pos_start : Position, pos_end : Position) -> None:
        self.pos_start = pos_start
        self.pos_end = pos_end
    
    def __repr__(self) -> str:
        return f'break'