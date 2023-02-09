from Utils.Token import Token

class StringNode:
    def __init__(self, token : Token) -> None:
        self.token = token

        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end
    
    def __repr__(self) -> str:
        return f'{self.token}'