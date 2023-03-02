import PyLang as pl
from Core.Constants import *

while True:
    text = input('PyLang > ')
    if text == '': break
    result, error = pl._run('<stdin>', text, global_symbol_table)

    if error: print(error)
    elif result: print(repr(result))
