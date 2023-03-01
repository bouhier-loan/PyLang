from Errors.Error import Error

from Core.Constants import *
from Core.Interpreter import Interpreter
from Core.Lexer import Lexer
from Core.Parser import Parser

from Utils.Context import Context
from Utils.Token import Token

from sys import argv

###########
# ! RUN ! #
###########

def run(file_name : str, text : str, testing : bool = False) -> tuple[Token, Error]:
    # * Generate tokens *
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    if tokens[0].type == TT_QMARK:
        if testing:
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

def runFile(file_name : str, testing : bool = False) -> tuple[Token, Error]:
    try:
        fileText = open(file_name).read().split('\n')
    except FileNotFoundError:
            print('File not found')
            exit(1)
    for line in fileText:
        if line == '':
            continue
        _, error = run(file_name, line, testing)
        if error: print(error)

if __name__ == '__main__':
    args = argv
    if len(args) == 1:
        exec(open("shell.py").read())
    elif len(args) <= 3:
        testing = False
        if '-test' in args:
            args.remove('-test')
            testing = True
        runFile(args[1], testing)
