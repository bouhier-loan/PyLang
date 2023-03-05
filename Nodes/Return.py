from Utils.Token import Token
from Utils.Position import Position


class ReturnNode:
    def __init__(self, return_node, pos_start : Position, pos_end : Position) -> None:
        self.return_node = return_node
        self.pos_start = pos_start
        self.pos_end = pos_end
    
    def __repr__(self) -> str:
        return f'return {self.return_node}'