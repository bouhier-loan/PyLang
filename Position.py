################
# ! POSITION ! #
################

class Position:
    def __init__(self, index : int, line : int, column : int, file_name : str, file_text : str) -> None:
        self.index = index
        self.line = line
        self.column = column
        self.file_name = file_name
        self.file_text = file_text
    
    def advance(self, current_character : str = None) -> Position:
        self.index += 1
        self.column += 1

        if current_character == '\n':
            self.line += 1
            self.column = 0
        
        return self
    
    def copy(self) -> Position:
        return Position(self.index, self.line, self.column, self.file_name, self.file_text)