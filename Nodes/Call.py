from Nodes.BinOp import BinOpNode


class CallNode:
    def __init__(self, name_node, args_nodes : dict) -> None:
        self.name_node = name_node
        self.args_nodes = args_nodes

        self.pos_start = name_node.pos_start

        if len(args_nodes) > 0:
            self.pos_end = args_nodes.values()[-1].pos_end
        else:
            self.pos_end = name_node.pos_end
    
    def __repr__(self) -> str:
        return f"{self.name_node}({''.join([str(e) + ', ' if index != len(self.args_nodes) - 1 else str(e) for index ,e in enumerate(self.args_nodes.items())])})"