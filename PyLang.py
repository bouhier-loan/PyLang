from Errors.Error import Error

from Main.Constants import *
from Main.Interpreter import Interpreter
from Main.Lexer import Lexer
from Main.Parser import Parser

from Utils.Context import Context
from Utils.Token import Token

###########
# ! RUN ! #
###########

def run(file_name : str, text : str) -> tuple[Token, Error]:
    # * Generate tokens *
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    #?print(tokens)

    # * Generate AST *
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error

    #?print(ast.node)

    # * Run program *
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)


    return result.value, result.error