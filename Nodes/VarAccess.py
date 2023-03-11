from Utils.Token import Token


class VarAccessNode:
    def __init__(self, var_name_token : Token, slice_or_getter : list = None) -> None:
        self.var_name_token = var_name_token
        self.slice_or_getter = slice_or_getter

        self.pos_start = var_name_token.pos_start
        self.pos_end = var_name_token.pos_end
    
    def __repr__(self) -> str:
        return f'{self.var_name_token.value}'