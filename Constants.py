import string
from Values.Number import Number

#################
# ! CONSTANTS ! #
#################

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