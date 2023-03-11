from Errors.Error import Error
from Errors.ExpectedCharError import ExpectedCharError
from Errors.IllegalCharError import IllegalCharError

from Core.Constants import *

from Utils.Position import Position
from Utils.Token import Token

#############
# ! LEXER ! #
#############

class Lexer:
    def __init__(self, file_name : str, text : str, testing : bool = False) -> None:
        self.file_name = file_name
        self.text = text
        self.pos = Position(-1, 0, -1, file_name, text)
        self.current_char = None
        self.testing = testing
        self.advance()
    
    def advance(self) -> None:
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None
    
    def skip_one_line_comment(self) -> bool:
        self.advance()

        while self.current_char != '\n' and self.current_char != None:
            self.advance()

        if self.current_char == None:
            return True
        
        self.advance()
        return False
    
    def skip_multiline_comment(self) -> bool:

        last_char = ''

        self.advance()

        while self.current_char != None:
            if self.current_char == '\n':
                self.advance()
                continue

            if last_char + self.current_char == '*/':
                break
            last_char = self.current_char
            self.advance()

        if self.current_char == None:
            return True
        
        self.advance()
        return False
    
    def manage_testing(self) -> bool:
        if self.testing:
            self.advance()
            return False
        else:
            return self.skip_one_line_comment()

    def make_tokens(self) -> tuple[list[Token], Error]:
        tokens = []
        symbols = {
            '(' : TT_LPAREN, 
            ')' : TT_RPAREN,
            ',' : TT_COMMA,
            ':' : TT_COLON,
            '%' : TT_MOD,
            '[' : TT_LSBRACKET,
            ']' : TT_RSBRACKET,
            '{' : TT_LCBRACKET,
            '}' : TT_RCBRACKET,
            ';' : TT_NEWLINE,
            '\n': TT_NEWLINE,
            }

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
                continue
            if self.current_char == '#':
                if self.skip_one_line_comment():
                    continue
            if self.current_char == '?':
                
                if self.manage_testing():
                    continue
            elif self.current_char in symbols.keys():
                tokens.append(Token(symbols[self.current_char], pos_start=self.pos))
                self.advance()

            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS + '_':
                tokens.append(self.make_identifier())

            elif self.current_char == '!':
                tokens.append(self.make_not())
            elif self.current_char == '+':
                tokens.append(self.make_plus())
            elif self.current_char == '-':
                tokens.append(self.make_minus())
            elif self.current_char == '&':
                token, error = self.make_and()
                if error: return [], error
                tokens.append(token)
            elif self.current_char == '|':
                token, error = self.make_or()
                if error: return [], error
                tokens.append(token)
            elif self.current_char == '=':
                tokens.append(self.make_equals())
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
            elif self.current_char == '*':
                tokens.append(self.make_multiply())
            elif self.current_char == '/':
                result = self.make_divide()
                if result: tokens.append(result)
            elif self.current_char in ['"', "'"]:
                tokens.append(self.make_string(self.current_char))
            
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "' - Ascii code: " + str(ord(char)))

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None
    
    def make_number(self) -> Token:
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)
    
    def make_identifier(self) -> Token:
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()
        
        token_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER

        return Token(token_type, id_str, pos_start, self.pos)
    
    def make_not(self) -> Token:
        token_type = TT_NOT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TT_NE
        
        return Token(token_type, pos_start=pos_start, pos_end=self.pos)
    
    def make_equals(self) -> Token:
        token_type = TT_EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TT_EE
        
        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_less_than(self) -> Token:
        token_type = TT_LT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TT_LTE
        
        return Token(token_type, pos_start=pos_start, pos_end=self.pos)
    
    def make_greater_than(self) -> Token:
        token_type = TT_GT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TT_GTE
        
        return Token(token_type, pos_start=pos_start, pos_end=self.pos)
    
    def make_multiply(self) -> Token:
        token_type = TT_MUL
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '*':
            self.advance()
            token_type = TT_POW
        
        if self.current_char == '=':
            self.advance()
            token_type = TT_MULEQ
        
        return Token(token_type, pos_start=pos_start, pos_end=self.pos)
    
    def make_divide(self) -> Token:
        token_type = TT_DIV
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '/':
            self.advance()
            token_type = TT_QUO

        if self.current_char == '=':
            self.advance()
            token_type = TT_DIVEQ
        
        if self.current_char == '*':
            return self.skip_multiline_comment()
        
        return Token(token_type, pos_start=pos_start, pos_end=self.pos)
    
    def make_plus(self) -> Token:
        token_type = TT_PLUS
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TT_PLUSEQ
        elif self.current_char == '+':
            self.advance()
            token_type = TT_PLUSPLUS
        
        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_minus(self) -> Token:
        token_type = TT_MINUS
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            token_type = TT_MINUSEQ
        elif self.current_char == '-':
            self.advance()
            token_type = TT_MINUSMINUS
        
        return Token(token_type, pos_start=pos_start, pos_end=self.pos)

    def make_and(self) -> tuple[Token, Error]:
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '&':
            self.advance()
            return Token(TT_AND, pos_start=pos_start, pos_end=self.pos), None
        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "'&' (after '&')")
    
    def make_or(self) -> tuple[Token, Error]:
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '|':
            self.advance()
            return Token(TT_OR, pos_start=pos_start, pos_end=self.pos), None
        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "'|' (after '|')")
    
    def make_string(self, char : str) -> Token:
        string = ''
        escape_character = False

        pos_start = self.pos.copy()

        self.advance()
        while self.current_char is not None and (self.current_char != char or escape_character):
            if escape_character:
                if self.current_char == 't':
                    string += '\t'
                elif self.current_char == 'n':
                    string += '\n'
                else:
                    string += self.current_char
            else:
                if self.current_char == '\\':
                    escape_character = True
                else:
                    string += self.current_char
            self.advance()
            escape_character = False
        
        self.advance()
    
        return Token(TT_STRING, string, pos_start, self.pos)