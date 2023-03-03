import string

from Values.Number import Number
from Values.Functions.BuiltInFunctions import BuiltInFunction

from Utils.SymbolTable import SymbolTable

#################
# ! CONSTANTS ! #
#################

# GLOBALS

GLOBAL_TESTING  = False


# LETTERS & DIGITS
DIGITS          = '0123456789'
LETTERS         = string.ascii_letters 
LETTERS_DIGITS  = LETTERS + DIGITS

# KEYWORDS & =
TT_IDENTIFIER   = 'IDENTIFIER'
TT_KEYWORD      = 'KEYWORD'
TT_EQ           = 'EQ'

# VALUES TYPE
TT_INT          = 'INT'
TT_FLOAT        = 'FLOAT'
TT_STRING       = 'STRING'

# OPERATORS
TT_PLUS         = 'PLUS'
TT_MINUS        = 'MINUS'
TT_MUL          = 'MUL'
TT_DIV          = 'DIV'
TT_POW          = 'POW'
TT_QUO          = 'QUO'
TT_MOD          = 'MOD'
TT_PLUSEQ       = 'PLUSEQ'
TT_MINUSEQ      = 'MINUSEQ'
TT_MULEQ        = 'MULEQ'
TT_DIVEQ        = 'DIVEQ'
TT_PLUSPLUS     = 'PLUSPLUS'
TT_MINUSMINUS   = 'MINUSMINUS'

# PARENTHESES
TT_LPAREN       = 'LPAREN'
TT_RPAREN       = 'RPAREN'

#BRACKETS
TT_LSBRACKET    = 'LSBRACKET'
TT_RSBRACKET    = 'RSBRACKET'

# SEPARATORS

TT_COMMA        = 'COMMA'
TT_COLON        = 'COLON'
TT_DOT          = 'DOT'

# COMPARISON OPERATORS
TT_EE           = 'EE'
TT_NE           = 'NE'
TT_LT           = 'LT'
TT_GT           = 'GT'
TT_LTE          = 'LTE'
TT_GTE          = 'GTE'

TT_NOT          = 'NOT'
TT_AND          = 'AND'
TT_OR           = 'OR'

# END OF FILE
TT_EOF          = 'EOF'

# TESTING & COMENTS
TT_QMARK        = 'QMARK'

# KEYWORDS LIST

KEYWORDS = [
    'var',
    'if',
    'then',
    'elif',
    'else',
    'for',
    'to',
    'step',
    'while',
    'func',
    'get',
    'append',
    'delete',
]

# Numbers
Number.null = Number(0)
Number.true = Number(1)
Number.false = Number(0)

# Builtin functions
BuiltInFunction.print               = BuiltInFunction("print")
BuiltInFunction.string              = BuiltInFunction("string")
BuiltInFunction.int                 = BuiltInFunction("int")
BuiltInFunction.float               = BuiltInFunction("float")
BuiltInFunction.input               = BuiltInFunction("input")
BuiltInFunction.clear               = BuiltInFunction("clear")
BuiltInFunction.is_int              = BuiltInFunction("is_int")
BuiltInFunction.is_float            = BuiltInFunction("is_float")
BuiltInFunction.is_string           = BuiltInFunction("is_string")
BuiltInFunction.is_list             = BuiltInFunction("is_list")
BuiltInFunction.append              = BuiltInFunction("append")
BuiltInFunction.pop                 = BuiltInFunction("pop")
BuiltInFunction.get                 = BuiltInFunction("get")
BuiltInFunction.extend              = BuiltInFunction("extend")
BuiltInFunction.sqrt                = BuiltInFunction("sqrt")
BuiltInFunction.len                 = BuiltInFunction("len")
BuiltInFunction.sum                 = BuiltInFunction("sum")
BuiltInFunction.run                 = BuiltInFunction("run")
BuiltInFunction.import_module       = BuiltInFunction("import_module")

# Public symbol table
global_symbol_table = SymbolTable()

# * Default values *
global_symbol_table.set("null", Number.null)
global_symbol_table.set("False", Number.false)
global_symbol_table.set("false", Number.false)
global_symbol_table.set("True", Number.true)
global_symbol_table.set("true", Number.true)

# * Built in functions *
global_symbol_table.set("print", BuiltInFunction.print)
global_symbol_table.set("str", BuiltInFunction.string)
global_symbol_table.set("int", BuiltInFunction.int)
global_symbol_table.set("float", BuiltInFunction.float)
global_symbol_table.set("input", BuiltInFunction.input)
global_symbol_table.set("clear", BuiltInFunction.clear)
global_symbol_table.set("cls", BuiltInFunction.clear)
global_symbol_table.set("is_int", BuiltInFunction.is_int)
global_symbol_table.set("is_float", BuiltInFunction.is_float)
global_symbol_table.set("is_list", BuiltInFunction.is_list)
global_symbol_table.set("is_string", BuiltInFunction.is_string)
global_symbol_table.set("append", BuiltInFunction.append)
global_symbol_table.set("pop", BuiltInFunction.pop)
global_symbol_table.set("get_value", BuiltInFunction.get)
global_symbol_table.set("extend", BuiltInFunction.extend)
global_symbol_table.set("sqrt", BuiltInFunction.sqrt)
global_symbol_table.set("len", BuiltInFunction.len)
global_symbol_table.set("sum", BuiltInFunction.sum)
global_symbol_table.set("run", BuiltInFunction.run)
global_symbol_table.set("import", BuiltInFunction.import_module)