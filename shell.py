import PyLang as pl

while True:
    text = input('PyLang > ')
    if text == '': break
    result, error = pl._run('<stdin>', text)

    if error: print(error)
    elif result: print(repr(result))
