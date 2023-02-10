from Errors.Error import Error, arrows_on_strings

from Utils.Position import Position
from Utils.Context import Context

class RTError(Error):
    def __init__(self, pos_start : Position, pos_end : Position, details : str, context : Context) -> None:
        super().__init__(pos_start, pos_end, 'Runtime Error', details)
        self.context = context
    
    def __repr__(self) -> str:
        result = self.generate_traceback()
        result += f'{self.error_name}: {self.details}\n'
        result += '\n\n' + arrows_on_strings(self.pos_start.file_text, self.pos_start, self.pos_end)
        return result

    def generate_traceback(self) -> str:
        result = ''
        pos = self.pos_start
        context = self.context

        while context:
            result = f'  File {pos.file_name}, line {str(pos.line + 1)}, in {context.display_name}\n' + result
            pos = context.parent_entry_pos
            context = context.parent
        
        return 'Traceback (most recent call last):\n' + result