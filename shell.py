import PyLang as pl
from Core.Constants import *

while True:
    text = input('PyLang > ')
    if text.strip() == '': continue
    result, error = pl._run('<stdin>', text, global_symbol_table)

    if error: print(error)
    elif result: 
        if len(result.elements) == 1:
            print(repr(result.elements[0]))
        else:
            print(repr(result))
