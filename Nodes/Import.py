from Utils.Position import Position
from Utils.Token import Token

class ImportNode:
    def __init__(self, module_name_token : Token, pos_start : Position, pos_end : Position) -> None:
        self.module_name_token = module_name_token
        self.pos_start = pos_start
        self.pos_end = pos_end
    
    def __repr__(self) -> str:
        return f'return {self.module_name_token}'