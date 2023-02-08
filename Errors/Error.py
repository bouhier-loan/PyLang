from Position import Position
##############
# ! ERRORS ! #
##############

def arrows_on_strings(text : str, pos_start : Position, pos_end : Position) -> str:
    result = ''

    # Calculate indices
    idx_start = max(text.rfind('\n', 0, pos_start.index), 0)
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0: idx_end = len(text)
    
    # Generate each line
    line_count = pos_end.line - pos_start.line + 1
    for i in range(line_count):
        # Calculate line columns
        line = text[idx_start:idx_end]
        col_start = pos_start.column if i == 0 else 0
        col_end = pos_end.column if i == line_count - 1 else len(line) - 1

        # Append to result
        result += line + '\n'
        result += ' ' * col_start + '^' * (col_end - col_start)

        # Re-calculate indices
        idx_start = idx_end
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0: idx_end = len(text)

    return result.replace('\t', '')

class Error:
    def __init__(self, pos_start : Position, pos_end : Position, error_name : str, details : str) -> None:
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def __repr__(self) -> str:
        result  = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.file_name}, line {self.pos_start.line + 1}'
        result += '\n\n' + arrows_on_strings(self.pos_start.file_text, self.pos_start, self.pos_end)
        return result
