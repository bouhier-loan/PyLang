from Errors.Error import Error

from Core.Constants import *
from Core.Interpreter import Interpreter
from Core.Lexer import Lexer
from Core.Parser import Parser

from Utils.Context import Context
from Utils.Token import Token

from Values.RunFileValue import RunFileValue

from sys import argv

###########
# ! RUN ! #
###########

def _run(file_name : str, text : str) -> tuple[Token, Error]:
    # * Generate tokens *
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    if tokens[0].type == TT_QMARK:
        if GLOBAL_TESTING:
            tokens = tokens[1:]
        else:
            return None, None

    #?print(tokens)

    # * Generate AST *
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error

    #?print('> ' + str(ast.node))

    # * Run program *
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)


    return result.value, result.error

def runFile(file_name : str) -> tuple[Token, Error]:
    try:
        fileText = open(file_name).read().split('\n')
    except FileNotFoundError:
            print('File not found')
            exit(1)
    for line in fileText:
        if line == '':
            continue
        result, error = _run(file_name, line)
        if error: print(error)
        if isinstance(result, RunFileValue):
            runFile(result.value.value)

if __name__ == '__main__':
    args = argv
    if len(args) == 1:
        exec(open("shell.py").read())
    elif len(args) <= 3:
        if '-test' in args:
            args.remove('-test')
            GLOBAL_TESTING = True
        runFile(args[1])
