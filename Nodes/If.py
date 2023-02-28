from Nodes.BinOp import BinOpNode


class IfNode:
    def __init__(self,cases : tuple[BinOpNode, BinOpNode], else_case : BinOpNode) -> None:
        self.cases = cases
        self.else_case = else_case

        self.pos_start = cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[-1][0]).pos_end
    

    def __repr__(self) -> str:
        return f"if {''.join([str(case[0]) + ' {' + str(case[1]) + '} ' for case in self.cases])} {'else {' + str(self.else_case) + '}' if self.else_case else ''}"
    
        
        