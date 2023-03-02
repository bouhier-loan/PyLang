from Errors.Error import Error

from Core.Constants import *
from Core.Interpreter import Interpreter
from Core.Lexer import Lexer
from Core.Parser import Parser

from Utils.Context import Context
from Utils.Token import Token
from Utils.SymbolTable import SymbolTable

from Values.RunFileValue import RunFileValue
from Values.ImportModule import ImportModule

from sys import argv
from os import path
from os import getcwd

###########
# ! RUN ! #
###########

def _run(file_name : str, text : str, symbol_table : SymbolTable) -> tuple[Token, Error]:
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
    context.symbol_table = symbol_table
    result = interpreter.visit(ast.node, context)


    return result.value, result.error

def runFile(file_name : str, return_symbol_table : bool = False) -> (SymbolTable or None):
    try:
        fileText = open(file_name).read().split('\n')
        current_file_dir = path.dirname(path.abspath(file_name))
        
    except FileNotFoundError:
            print('File not found')
            exit(1)
    file_symbol_table = SymbolTable(global_symbol_table)
    for line in fileText:
        if line == '':
            continue
        result, error = _run(file_name, line, file_symbol_table)
        if error: print(error)
        if isinstance(result, RunFileValue):
            #?print("> RUN FILE: " + path.abspath(path.relpath(result.value.value, current_file_dir)))
            runFile(path.abspath(path.relpath(result.value.value, current_file_dir)))
        elif isinstance(result, ImportModule):
            #?print("> IMPORT MODULE: " + path.abspath(path.relpath(result.value.value, current_file_dir)))
            st = runFile(path.abspath(path.relpath(result.value.value, current_file_dir)), True)
            file_symbol_table = SymbolTable(st)
    if return_symbol_table:
        return file_symbol_table
        

if __name__ == '__main__':
    args = argv
    if len(args) == 1:
        exec(open("~/reseau/Perso/Cours/ProjetsPersos/PyLang/shell.py").read())
    elif len(args) <= 3:
        if '-test' in args:
            args.remove('-test')
            GLOBAL_TESTING = True
        runFile(args[1])
