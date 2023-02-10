from Errors.Error import Error

from Utils.Position import Position

class InvalidSyntaxError(Error):
    def __init__(self, pos_start : Position, pos_end : Position, details : str = '') -> None:
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)