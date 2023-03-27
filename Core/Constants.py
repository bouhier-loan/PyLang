import string

from Values.Boolean import Boolean
from Values.String import String

#################
# ! CONSTANTS ! #
#################

# GLOBALS

GLOBAL_TESTING  = False

# RULES
LOOP_MAX_RECUR  = 10000

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

TT_RCBRACKET    = 'RCBRACKET'
TT_LCBRACKET    = 'LCBRACKET'

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

# NEW LINE & END OF FILE
TT_NEWLINE     = 'NEW_LINE'
TT_EOF          = 'EOF'

# KEYWORDS LIST

KEYWORDS = [
    'var',
    'if',
    'elif',
    'else',
    'for',
    'to',
    'step',
    'while',
    'func',
    'append',
    'delete',
    'return',
    'break',
    'continue',
    'in',
    'import',
]

# Numbers
Boolean.null = Boolean(None)
Boolean.true = Boolean(True)
Boolean.false = Boolean(False)

String.int = String('int')
String.float = String('float')
String.string = String('str')
String.boolean = String('boolean')
String.function = String('function')
String.list = String('list')
String.boolean = String('bool')
