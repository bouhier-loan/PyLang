from BinOp import BinOpNode

class CallNode:
    def __init__(self, name_node, args_nodes : list[BinOpNode]) -> None:
        self.name_node = name_node
        self.args_nodes = args_nodes

        self.pos_start = name_node.pos_start

        if len(args_nodes) > 0:
            self.pos_end = args_nodes[-1].pos_end
        else:
            self.pos_end = name_node.pos_end