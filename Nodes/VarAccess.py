from Token import Token

class VarAccessNode:
    def __init__(self, var_name_token : Token) -> None:
        self.var_name_token = var_name_token

        self.pos_start = var_name_token.pos_start
        self.pos_end = var_name_token.pos_end