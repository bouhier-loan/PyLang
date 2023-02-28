class ListNode:
    def __init__(self, elements_nodes, pos_start, pos_end) -> None:
        self.elements_nodes = elements_nodes

        self.pos_start = pos_start
        self.pos_end = pos_end
    
    def __repr__(self) -> str:
        return f"[{''.join([str(e) + ', ' if index != len(self.elements_nodes) - 1 else str(e) for index, e in enumerate(self.elements_nodes)])}]"