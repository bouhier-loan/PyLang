from __future__ import annotations
import os
import math

from Constants import *
################
# ! POSITION ! #
################

class Position:
    def __init__(self, index : int, line : int, column : int, file_name : str, file_text : str) -> None:
        self.index = index
        self.line = line
        self.column = column
        self.file_name = file_name
        self.file_text = file_text
    
    def advance(self, current_character : str = None) -> Position:
        self.index += 1
        self.column += 1

        if current_character == '\n':
            self.line += 1
            self.column = 0
        
        return self
    
    def copy(self) -> Position:
        return Position(self.index, self.line, self.column, self.file_name, self.file_text)

####################
# ! SYMBOL TABLE ! #
####################

class SymbolTable:
    def __init__(self, parent : SymbolTable = None) -> None:
        self.symbols = {}
        self.parent = parent

    def get(self, name : str):
        value = self.symbols.get(name, None)

        if value == None and self.parent:
            return self.parent.get(name)
        return value
    
    def set(self, name : str, value) -> None:
        self.symbols[name] = value
    
    def remove(self, name : str) -> None:
        del self.symbols[name]


###############
# ! CONTEXT ! #
###############

class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None) -> None:
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table : SymbolTable = None


##############
# ! ERRORS ! #
##############

def arrows_on_strings(text : str, pos_start, pos_end):
    result = ''

    # Calculate indices
    idx_start = max(text.rfind('\n', 0, pos_start.index), 0)
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0: idx_end = len(text)
    
    # Generate each line
    line_count = pos_end.line - pos_start.line + 1
    for i in range(line_count):
        # Calculate line columns
        line = text[idx_start:idx_end]
        col_start = pos_start.column if i == 0 else 0
        col_end = pos_end.column if i == line_count - 1 else len(line) - 1

        # Append to result
        result += line + '\n'
        result += ' ' * col_start + '^' * (col_end - col_start)

        # Re-calculate indices
        idx_start = idx_end
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0: idx_end = len(text)

    return result.replace('\t', '')

class Error:
    def __init__(self, pos_start : Position, pos_end : Position, error_name : str, details : str) -> None:
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def __repr__(self) -> str:
        result  = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.file_name}, line {self.pos_start.line + 1}'
        result += '\n\n' + arrows_on_strings(self.pos_start.file_text, self.pos_start, self.pos_end)
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start : Position, pos_end : Position, details : str) -> None:
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start : Position, pos_end : Position, details : str = '') -> None:
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class ExpectedCharError(Error):
    def __init__(self, pos_start : Position, pos_end : Position, details : str) -> None:
        super().__init__(pos_start, pos_end, 'Expected Character', details)

class RTError(Error):
    def __init__(self, pos_start : Position, pos_end : Position, details : str, context : Context) -> None:
        super().__init__(pos_start, pos_end, 'Runtime Error', details)
        self.context = context
    
    def __repr__(self) -> str:
        result = self.generate_traceback()
        result += f'{self.error_name}: {self.details}\n'
        result += '\n\n' + arrows_on_strings(self.pos_start.file_text, self.pos_start, self.pos_end)
        return result

    def generate_traceback(self) -> str:
        result = ''
        pos = self.pos_start
        context = self.context

        while context:
            result = f'  File {pos.file_name}, line {str(pos.line + 1)}, in {context.display_name}\n' + result
            pos = context.parent_entry_pos
            context = context.parent
        
        return 'Traceback (most recent call last):\n' + result


##############
# ! TOKENS ! #
##############

class Token:
    def __init__(self, type_ : str, value = None, pos_start : Position = None, pos_end : Position = None) -> None:
        self.type = type_
        self.value = value
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        
        if pos_end:
            self.pos_end = pos_end

    def __repr__(self) -> str:
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
    
    def matches(self,  type_ : str, value : str) -> bool:
        return self.type == type_ and self.value == value


#############
# ! LEXER ! #
#############

class Lexer:
    def __init__(self, file_name : str, text : str) -> None:
        self.file_name = file_name
        self.text = text
        self.pos = Position(-1, 0, -1, file_name, text)
        self.current_char = None
        self.advance()
    
    def advance(self) -> None:
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None

    def make_tokens(self) -> tuple[list[Token], Error]:
        tokens = []
        symbols = {
            '+' : TT_PLUS,
            '-' : TT_MINUS,
            '(' : TT_LPAREN, 
            ')' : TT_RPAREN,
            ',' : TT_COMMA,
            ':' : TT_COLON,
            '%' : TT_MOD,
            '[' : TT_LSBRACKET,
            ']' : TT_RSBRACKET,
            }

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in symbols.keys():
                tokens.append(Token(symbols[self.current_char], pos_start=self.pos))
                self.advance()

            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())

            elif self.current_char == '!':
                tokens.append(self.make_not())
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
                tokens.append(self.make_divide())
            elif self.current_char == '"':
                tokens.append(self.make_string())

            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

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
        
        return Token(token_type, pos_start=pos_start, pos_end=self.pos)
    
    def make_divide(self) -> Token:
        token_type = TT_DIV
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '/':
            self.advance()
            token_type = TT_QUO
        
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
    
    def make_string(self) -> Token:
        string = ''
        escape_character = False

        pos_start = self.pos.copy()

        self.advance()
        while self.current_char is not None and (self.current_char != '"' or escape_character):
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
#############
# ! NODES ! #
#############

class NumberNode:
    def __init__(self, token : Token) -> None:
        self.token = token

        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end
    
    def __repr__(self) -> str:
        return f'{self.token}'

class StringNode:
    def __init__(self, token : Token) -> None:
        self.token = token

        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end
    
    def __repr__(self) -> str:
        return f'{self.token}'
class BinOpNode:
    def __init__(self, left_node, op_token : Token, right_node) -> None:
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end
    
    def __repr__(self) -> str:
        return f'({self.left_node}, {self.op_token}, {self.right_node})'

class UnaryOpNode:
    def __init__(self, op_token, node) -> None:
        self.op_token = op_token
        self.node = node

        self.pos_start = self.op_token.pos_start
        self.pos_end = node.pos_end
    
    def __repr__(self) -> str:
        return f'({self.op_token}, {self.node})'

class VarAssignNode:
    def __init__(self, var_name_token : Token, value_node : BinOpNode | UnaryOpNode | NumberNode) -> None:
        self.var_name_token = var_name_token
        self.value_node = value_node

        self.pos_start = var_name_token.pos_start
        self.pos_end = value_node.pos_end

class VarAccessNode:
    def __init__(self, var_name_token : Token) -> None:
        self.var_name_token = var_name_token

        self.pos_start = var_name_token.pos_start
        self.pos_end = var_name_token.pos_end
    
class IfNode:
    def __init__(self,cases : tuple[BinOpNode, BinOpNode], else_case : BinOpNode) -> None:
        self.cases = cases
        self.else_case = else_case

        self.pos_start = cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[-1][0]).pos_end

class ForNode:
    def __init__(self, var_name_token : BinOpNode, start_value_node : BinOpNode, end_value_node : BinOpNode, step_value_node : BinOpNode, body_node : BinOpNode) -> None:
        self.var_name_token = var_name_token
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node

        self.pos_start = var_name_token.pos_start
        self.pos_end = body_node.pos_end

class WhileNode:
    def __init__(self, condition_node : BinOpNode, body_node : BinOpNode) -> None:
        self.condition_node = condition_node
        self.body_node = body_node

        self.pos_start = condition_node.pos_start
        self.pos_end = body_node.pos_end

class FuncDefNode:
    def __init__(self, var_name_token : Token, arg_name_tokens : list[Token], body_node : BinOpNode) -> None:
        self.var_name_token = var_name_token
        self.arg_name_tokens = arg_name_tokens
        self.body_node = body_node

        if var_name_token:
            self.pos_start = var_name_token.pos_start
        elif len(arg_name_tokens) > 0:
            self.pos_start = arg_name_tokens[0].pos_start
        else:
            self.pos_start = body_node.pos_start

        self.pos_end = body_node.pos_end

class CallNode:
    def __init__(self, name_node, args_nodes : list[BinOpNode]) -> None:
        self.name_node = name_node
        self.args_nodes = args_nodes

        self.pos_start = name_node.pos_start

        if len(args_nodes) > 0:
            self.pos_end = args_nodes[-1].pos_end
        else:
            self.pos_end = name_node.pos_end

class ListNode:
    def __init__(self, elements_nodes, pos_start, pos_end) -> None:
        self.elements_nodes = elements_nodes

        self.pos_start = pos_start
        self.pos_end = pos_end

#####################
# ! PARSER RESULT ! #
#####################

class ParseResult:
    def __init__(self) -> None:
        self.error = None
        self.node = None
        self.advance_count = 0

    def register_advance(self):
        self.advance_count += 1
    
    def register(self, result) -> ParseResult | BinOpNode | NumberNode:
        self.advance_count += result.advance_count
        if result.error: self.error = result.error
        return result.node

    def success(self, node) -> ParseResult:
        self.node = node
        return self

    def failure(self, error : Error) -> ParseResult:
        if not self.error or self.advance_count == 0:
            self.error = error
        return self


##############
# ! PARSER ! #
##############

class Parser:
    def __init__(self, tokens : list[Token]) -> None:
        self.tokens = tokens
        self.token_index = -1
        self.advance()
    
    def advance(self) -> Token:
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        return self.current_token
    
    def parse(self) -> BinOpNode:
        result = self.expression()
        if not result.error and self.current_token.type != TT_EOF:
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '+', '-', '*', '/', '%', '//', '**', '==', '!=', '<', '>', <=', '>=', '&&' or '||'"
            ))
        return result

########

    def list_expr(self) -> ParseResult:
        result = ParseResult()
        element_nodes = []

        pos_start = self.current_token.pos_start.copy()

        if not self.current_token.type == TT_LSBRACKET:
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected '['"
            ))
        
        result.register_advance()
        self.advance()

        if self.current_token.type == TT_RSBRACKET:
            result.register_advance()
            self.advance()
        else:
            element_nodes.append(result.register(self.expression()))
            if result.error:
                return result.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ']', 'var', 'if', 'for', 'while', 'func', INT, FLOAT, IDENTIFIER, '+', '-', '(' or '!'"
                ))
            
            while self.current_token.type == TT_COMMA:
                result.register_advance()
                self.advance()

                element_nodes.append(result.register(self.expression()))
                if result.error: return result
            
            if self.current_token.type != TT_RSBRACKET:
                return result.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ',' or ']'"
                ))
            
            result.register_advance()
            self.advance()
            
        return result.success(ListNode(element_nodes, pos_start, self.current_token.pos_end.copy()))  

    def if_expr(self) -> ParseResult:
        result = ParseResult()
        cases = []
        else_case = None

        if not self.current_token.matches(TT_KEYWORD, 'if'):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'if'"
            ))
        
        result.register_advance()
        self.advance()

        condition = result.register(self.expression())
        if result.error: return result

        if not self.current_token.matches(TT_KEYWORD, 'then'):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'then'"
            ))

        result.register_advance()
        self.advance()

        expression = result.register(self.expression())

        if result.error: return result
        cases.append((condition, expression))

        while self.current_token.matches(TT_KEYWORD, 'elif'):
            result.register_advance()
            self.advance()

            condition = result.register(self.expression())
            if result.error: return result

            if not self.current_token.matches(TT_KEYWORD, 'then'):
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected 'then'"
                ))

            result.register_advance()
            self.advance()

            expression = result.register(self.expression())

            if result.error: return result
            cases.append((condition, expression))
        
        if self.current_token.matches(TT_KEYWORD, 'else'):
            result.register_advance()
            self.advance()

            expression = result.register(self.expression())

            if result.error: return result
            else_case = expression
        
        return result.success(IfNode(cases, else_case))

    def for_expr(self) -> ParseResult:
        result = ParseResult()

        if not self.current_token.matches(TT_KEYWORD, 'for'):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'for'"
            ))

        result.register_advance()
        self.advance()

        if not self.current_token.type == TT_IDENTIFIER:
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected IDENTIFIER"
            ))
        
        var_name = self.current_token
        result.register_advance()
        self.advance()

        if not self.current_token.type == TT_EQ:
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected '='"
            ))
        
        result.register_advance()
        self.advance()

        start_value = result.register(self.expression())
        if result.error: return result


        if not self.current_token.matches(TT_KEYWORD, 'to'):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'to'"
            ))
        
        result.register_advance()
        self.advance()

        end_value = result.register(self.expression())
        if result.error: return result


        if self.current_token.matches(TT_KEYWORD, 'step'):
            result.register_advance()
            self.advance()

            step_value = result.register(self.expression())
            if result.error: return result
        else:
            step_value = None
        
        if not self.current_token.matches(TT_KEYWORD, 'then'):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'then'"
            ))
        
        result.register_advance()
        self.advance()

        body = result.register(self.expression())
        if result.error: return result

        return result.success(ForNode(var_name, start_value, end_value, step_value, body))
        
    def while_expr(self) -> ParseResult:
        result = ParseResult()

        if not self.current_token.matches(TT_KEYWORD, 'while'):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'while'"
            ))
        
        result.register_advance()
        self.advance()

        condition_value = result.register(self.expression())
        if result.error: return result

        result.register_advance()
        self.advance()

        if not self.current_token.matches(TT_KEYWORD, 'then'):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'then'"
            ))
        
        result.register_advance()
        self.advance()

        body = result.register(self.expression())
        if result.error: return result

        return result.success(WhileNode(condition_value, body))

    def func_def(self) -> ParseResult:
        result = ParseResult()

        if not self.current_token.matches(TT_KEYWORD, 'func'):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'func'"
            ))
        
        result.register_advance()
        self.advance()

        if self.current_token.type == TT_IDENTIFIER:
            func_name_token = self.current_token
            result.register_advance()
            self.advance()

            if self.current_token.type != TT_LPAREN:
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected '('"
                ))
        else:
            func_name_token = None
            if self.current_token.type != TT_LPAREN:
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected IDENTIFIER or '('"
                ))

        result.register_advance()
        self.advance()
        arg_name_tokens = []

        if self.current_token.type == TT_IDENTIFIER:
            arg_name_tokens.append(self.current_token)
            result.register_advance()
            self.advance()

            while self.current_token.type == TT_COMMA:
                result.register_advance()
                self.advance()

                if self.current_token.type != TT_IDENTIFIER:
                    return result.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        f"Expected IDENTIFIER"
                    ))

                arg_name_tokens.append(self.current_token)
                result.register_advance()
                self.advance()
            
            if self.current_token.type != TT_RPAREN:
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected ',' or ')'"
                ))
        else:
            if self.current_token.type != TT_RPAREN:
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected IDENTIFIER or ')'"
                ))
            
        result.register_advance()
        self.advance()

        if self.current_token.type != TT_COLON:
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected ':'"
            ))
        
        result.register_advance()
        self.advance()
        
        body_node = result.register(self.expression())
        if result.error: return result

        return result.success(FuncDefNode(func_name_token, arg_name_tokens, body_node))

    def call(self) -> ParseResult:
        result = ParseResult()
        atom = result.register(self.atom())
        if result.error: return result

        if self.current_token.type == TT_LPAREN:
            result.register_advance()
            self.advance()

            arg_nodes = []

            if self.current_token.type == TT_RPAREN:
                result.register_advance()
                self.advance()
            else:
                arg_nodes.append(result.register(self.expression()))
                if result.error:
                    return result.failure(InvalidSyntaxError(
						self.current_token.pos_start, self.current_token.pos_end,
						"Expected ')', 'var', 'if', 'for', 'while', 'func', INT, FLOAT, IDENTIFIER, '+', '-', '(' or '!'"
					))
                
                while self.current_token.type == TT_COMMA:
                    result.register_advance()
                    self.advance()

                    arg_nodes.append(result.register(self.expression()))
                    if result.error: return result
                
                if self.current_token.type != TT_RPAREN:
                    return result.failure(InvalidSyntaxError(
						self.current_tok.pos_start, self.current_tok.pos_end,
						"Expected ',' or ')'"
					))
                
                result.register_advance()
                self.advance()
            
            return result.success(CallNode(atom, arg_nodes))
        return result.success(atom)


    def atom(self) -> ParseResult:
        result = ParseResult()
        token = self.current_token

        if token.type in (TT_INT, TT_FLOAT):
            result.register_advance()
            self.advance()
            return result.success(NumberNode(token))
        
        if token.type == TT_STRING:
            result.register_advance()
            self.advance()
            return result.success(StringNode(token))
        
        elif token.type == TT_IDENTIFIER:
            result.register_advance()
            self.advance()
            return result.success(VarAccessNode(token))

        elif token.type == TT_LPAREN:
            result.register_advance()
            self.advance()
            expression = result.register(self.expression())
            if result.error: return result
            if self.current_token.type == TT_RPAREN:
                result.register_advance()
                self.advance()
                return result.success(expression)
            else:
                return result.failure(InvalidSyntaxError(
                    token.pos_start, token.pos_end,
                    "Expected ')'"
                ))
        elif token.type == TT_LSBRACKET:
            list_expr = result.register(self.list_expr())
            if result.error: return result
            return result.success(list_expr)
        
        elif token.matches(TT_KEYWORD, "if"):
            if_expr = result.register(self.if_expr())
            if result.error: return result
            return result.success(if_expr)
    
        elif token.matches(TT_KEYWORD, "for"):
            for_expr = result.register(self.for_expr())
            if result.error: return result
            return result.success(for_expr)
        
        elif token.matches(TT_KEYWORD, "while"):
            while_expr = result.register(self.while_expr())
            if result.error: return result
            return result.success(while_expr)
        
        elif token.matches(TT_KEYWORD, "func"):
            func_def = result.register(self.func_def())
            if result.error: return result
            return result.success(func_def)
        
        return result.failure(InvalidSyntaxError(
            token.pos_start, token.pos_end,
            f"Expected INT, FLOAT, IDENTIFIER, '+', '-' or '('"
        ))
    
    def power(self) -> ParseResult:
        return self.bin_operator(self.call, (TT_POW, ), self.factor)

    def factor(self) -> ParseResult:
        result = ParseResult()
        token = self.current_token

        if token.type in (TT_PLUS, TT_MINUS):
            result.register_advance()
            self.advance()
            factor = result.register(self.factor())
            if result.error: return result
            return result.success(UnaryOpNode(token, factor))

        return self.power()

    def term(self) -> BinOpNode:
        return self.bin_operator(self.factor, (TT_MUL, TT_DIV, TT_MOD, TT_QUO))
    
    def arith_expr(self) -> BinOpNode:
        return self.bin_operator(self.term, (TT_PLUS, TT_MINUS))
    
    def comp_expr(self) -> BinOpNode:
        result = ParseResult()

        if self.current_token.type == TT_NOT:
            op_token = self.current_token
            result.register_advance()
            self.advance()

            node = result.register(self.comp_expr())
            if result.error: return result
            return result.success(UnaryOpNode(op_token, node))
        
        node = result.register(self.bin_operator(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))

        if result.error:
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected INT, FLOAT, IDENTIFIER, '!', '+', '-' or '('"
            ))
        return result.success(node)


    def expression(self) -> BinOpNode:
        result = ParseResult()

        if self.current_token.matches(TT_KEYWORD, 'var'):
            result.register_advance()
            self.advance()

            if self.current_token.type != TT_IDENTIFIER:
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected identifier"
                ))
            
            var_name = self.current_token
            result.register_advance()
            self.advance()

            if self.current_token.type != TT_EQ:
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '='"
                ))
        
            result.register_advance()
            self.advance()

            expression = result.register(self.expression())
            if result.error: return result
            return result.success(VarAssignNode(var_name, expression))

        node = result.register(self.bin_operator(self.comp_expr, (TT_AND, TT_OR)))

        if result.error: 
            return result.failure(InvalidSyntaxError(
            self.current_token.pos_start, self.current_token.pos_end,
            f"Expected 'var', INT, FLOAT, IDENTIFIER, '!', '+', '-' or '('"
        ))

        return result.success(node)

########

    def bin_operator(self, func_a, ops : tuple[str], func_b = None) -> BinOpNode:
        if func_b == None:
            func_b = func_a
        
        result = ParseResult()
        left = result.register(func_a())
        if result.error: return result

        while self.current_token.type in ops:
            op_token = self.current_token
            result.register_advance()
            self.advance()
            right = result.register(func_b())
            if result.error: return result
            left = BinOpNode(left, op_token, right)
        
        return result.success(left)


######################
# ! RUNTIME RESULT ! #
######################

class RTResult:
    def __init__(self) -> None:
        self.value = None
        self.error : Error = None

    def register(self, result : RTResult):
        if result.error: self.error = result.error
        return result.value
    
    def success(self, value) -> RTResult:
        self.value = value
        return self
    
    def failure(self, error : Error) -> RTResult:
        self.error = error
        return self

##############
# ! VALUES ! #
##############

class Value:
    def __init__(self) -> None:
        self.set_pos()
        self.set_context()
    
    def set_pos(self, pos_start : Position = None, pos_end : Position = None) -> Value:
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def set_context(self, context: Context = None) -> Value:
        self.context = context
        return self
    
    def add(self, other : Number) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def subtract(self, other : Number) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def multiply(self, other : Number) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def divide(self, other : Number) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def modulo(self, other : Number) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def quotient(self, other : Number) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
        
    def power(self, other) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def copy(self) -> Exception:
        raise Exception("No copy method defined")
    
    def get_comparison_eq(self, other) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def get_comparison_ne(self, other) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def get_comparison_lt(self, other) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def get_comparison_gt(self, other) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def get_comparison_lte(self, other) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def get_comparison_gte(self, other) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def get_and(self, other) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
        
    def get_or(self, other) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def not_comp(self) -> tuple[Number, RTError]:
        return None, self.illegal_operation()
    
    def is_true(self) -> bool:
        return False
    
    def illegal_operation(self, other = None) -> RTError:
        if not other: other = self
        return RTError(
            self.pos_start, self.pos_end,
            "Illegal operation",
            self.context
        )

class List(Value):
    def __init__(self, elements : list) -> None:
        super().__init__()
        self.elements = elements
        self.value = []
    
    def multiply(self, other : Number) -> tuple[List, RTError]:
        if isinstance(other, Number):
            new_list = self.copy()
            new_list.elements *= other.value
            return new_list, None
        return None, Value.illegal_operation(self, other)
    
    def add(self, other : List) -> tuple[List, RTError]:
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        return None, Value.illegal_operation(self, other)
    
    def copy(self) -> List:
        copy = List(self.elements[:])
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __repr__(self) -> str:
        return f'[{", ".join([str(element) for element in self.elements])}]'

class String(Value):
    def __init__(self, value : str) -> None:
        super().__init__()
        self.value = value

    def add(self, other : String) -> tuple[String, RTError]:
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        return None, Value.illegal_operation(self, other)
    
    def multiply(self, other : Number) -> tuple[String, RTError]:
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        return None, Value.illegal_operation(self, other)
    
    def is_true(self) -> bool:
        return len(self.value) > 0
    
    def copy(self) -> String:
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __str__(self) -> str:
        return f"{self.value}"
    
    def __repr__(self) -> str:
        return f'"{self.value}"'
class Number(Value):
    def __init__(self, value : int | float) -> None:
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start : Position = None, pos_end : Position = None) -> Number:
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def set_context(self, context : Context = None) -> Context:
        self.context = context
        return self

    def add(self, other : Number) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def subtract(self, other : Number) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def multiply(self, other : Number) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def divide(self, other : Number) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    "Division by zero",
                    self.context
                )
            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def modulo(self, other : Number) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    "Division by zero",
                    self.context
                )
            return Number(self.value % other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def quotient(self, other : Number) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    "Division by zero",
                    self.context
                )
            return Number(self.value // other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
        
    def power(self, other) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def copy(self) -> Number:
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def get_comparison_eq(self, other) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def get_comparison_ne(self, other) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def get_comparison_lt(self, other) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def get_comparison_gt(self, other) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def get_comparison_lte(self, other) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def get_comparison_gte(self, other) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def get_and(self, other) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
        
    def get_or(self, other) -> tuple[Number, RTError]:
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def not_comp(self) -> tuple[Number, RTError]:
        return Number(1 if self.value == 0 else 0).set_context(self.context), None
    
    def is_true(self) -> bool:
        return self.value != 0
    
    def __repr__(self) -> str:
        return f'{self.value}'

Number.null = Number(0)
Number.true = Number(1)
Number.false = Number(0)

class BaseFunction(Value):
    def __init__(self, name : str) -> None:
        super().__init__()
        self.name = name or "<anonymous>"
                 
    def generate_new_context(self) -> Context:
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context
    
    def check_args(self, arg_names : list[Value], args : list[Value]) -> RTResult:
        result = RTResult()
        
        if len(args) > len(arg_names):
            return result.failure(RTError(
                self.pos_start, self.pos_end,
                f"Too many args passed into '{self.name}'!\nNeeded {len(arg_names)}, given {len(args)}",
                self.context
            ))
        elif len(args) < len(arg_names):
            return result.failure(RTError(
                self.pos_start, self.pos_end,
                f"Too few args passed into '{self.name}'!\nNeeded {len(arg_names)}, given {len(args)}",
                self.context
            ))
        return result.success(None)
    
    def populate_args(self, arg_names : list[Value], args : list[Value], execution_context : Context):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(execution_context)
            execution_context.symbol_table.set(arg_name, arg_value)
    
    def check_populate_args(self, arg_names : list[Token], args : list[Token], execution_context : Context) -> RTResult:
        result = RTResult()
        result.register(self.check_args(arg_names, args))
        if result.error: return result
        self.populate_args(arg_names, args, execution_context)
        return result.success(None)


class Function(BaseFunction):
    def __init__(self, name : Token, body_node : BinOpNode, arg_names : list[Token]) -> None:
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names

    def execute(self, args : list[Value]) -> RTResult:
        result = RTResult()
        interpreter = Interpreter()
        exec_context = self.generate_new_context()

        result.register(self.check_populate_args(self.arg_names, args, exec_context))
        if result.error: return result
        
        value = result.register(interpreter.visit(self.body_node, exec_context))
        if result.error: return result

        return result.success(value)
    
    def copy(self) -> Function:
        copy = Function(self.name, self.body_node, self.arg_names)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    
    def __repr__(self) -> str:
        return f'<function {self.name}>'

class BuiltInFunction(BaseFunction):
    def __init__(self, name : Token) -> None:
        super().__init__(name)

    def execute(self, args : list[Token]) -> RTResult:
        result = RTResult()
        exec_context = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        result.register(self.check_populate_args(method.arg_names, args, exec_context))
        if result.error: return result

        return_value = result.register(method(exec_context))
        if result.error: return result

        return result.success(return_value)

    def no_visit_method(self) -> Exception:
        raise Exception(f'No execute_{self.name} method defined')
    
    def copy(self) -> BuiltInFunction:
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
    
    def __repr__(self) -> str:
        return f'<built-in function {self.name}> '
    
    ########################

    def execute_print(self, exec_context : Context) -> RTResult:
        print(str(exec_context.symbol_table.get('value')))
        return RTResult().success(Number.null)
    execute_print.arg_names = ["value"]

    def execute_string(self, exec_context : Context) -> RTResult:
        try:
            text = str(exec_context.symbol_table.get('value').value)
        except ValueError:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                f"Cannot convert {exec_context.symbol_table.get('value').type} to STR",
                exec_context
            ))
        return RTResult().success(String(text))
    execute_string.arg_names = ["value"]

    def execute_int(self, exec_context : Context) -> RTResult:
        try:
            number = int(exec_context.symbol_table.get('value').value)
        except ValueError:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                f"Cannot convert {exec_context.symbol_table.get('value').type} to INT",
                exec_context
            ))
        return RTResult().success(Number(number))
    execute_int.arg_names = ["value"]

    def execute_float(self, exec_context : Context) -> RTResult:
        try:
            number = float(exec_context.symbol_table.get('value').value)
        except ValueError:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                f"Cannot convert {exec_context.symbol_table.get('value').type} to FLOAT",
                exec_context
            ))
        return RTResult().success(Number(number))
    execute_float.arg_names = ["value"]

    def execute_input(self, exec_context : Context) -> RTResult:
        text = input(exec_context.symbol_table.get('value'))
        return RTResult().success(String(text))
    execute_input.arg_names = ["value"]

    def execute_clear(self, exec_context : Context) -> RTResult:
        os.system('cls' if os.name == 'nt' else 'clear')
        return RTResult().success(Number.null)
    execute_clear.arg_names = []

    def execute_is_int(self, exec_context : Context) -> RTResult:
        is_int = type(exec_context.symbol_table.get('value').value) == int
        return RTResult().success(Number.true if is_int else Number.false)
    execute_is_int.arg_names = ["value"]

    def execute_is_float(self, exec_context : Context) -> RTResult:
        is_float = type(exec_context.symbol_table.get('value').value) == float
        return RTResult().success(Number.true if is_float else Number.false)
    execute_is_float.arg_names = ["value"]

    def execute_is_string(self, exec_context : Context) -> RTResult:
        is_string = type(exec_context.symbol_table.get('value').value) == string
        return RTResult().success(Number.true if is_string else Number.false)
    execute_is_string.arg_names = ["value"]

    def execute_is_list(self, exec_context : Context) -> RTResult:
        is_list = type(exec_context.symbol_table.get('value').value) == list
        return RTResult().success(Number.true if is_list else Number.false)
    execute_is_list.arg_names = ["value"]

    def execute_append(self, exec_context : Context) -> RTResult:
        list = exec_context.symbol_table.get('list')
        value = exec_context.symbol_table.get('value')

        if not isinstance(list, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be a LIST",
                exec_context
            ))
        
        list.elements.append(value)

        return RTResult().success(Number.null)
    execute_append.arg_names = ["list", "value"]

    def execute_pop(self, exec_context : Context) -> RTResult:
        list = exec_context.symbol_table.get('list')
        value = exec_context.symbol_table.get('value')

        if not isinstance(list, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be LIST",
                exec_context
            ))
        
        if not isinstance(value, Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be INT",
                exec_context
            ))
        
        try:
            return_value = list.elements.pop(value.value)
        except:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Element at this index could not be removed from list because index is out of range",
                exec_context
            ))

        return RTResult().success(return_value)
    execute_pop.arg_names = ["list", "value"]

    def execute_get(self, exec_context : Context) -> RTResult:
        list = exec_context.symbol_table.get('list')
        value = exec_context.symbol_table.get('value')

        if not isinstance(list, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be LIST",
                exec_context
            ))
        
        if not isinstance(value, Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be INT",
                exec_context
            ))
        try:
            return_value = list.elements[value.value]
        except:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Element at this index could not be removed from list because index is out of range",
                exec_context
            ))
        
        return RTResult().success(return_value)
    execute_get.arg_names = ["list", "value"]

    def execute_extend(self, exec_context : Context) -> RTResult:
        list1 = exec_context.symbol_table.get('list1')
        list2 = exec_context.symbol_table.get('list2')

        if not isinstance(list1, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be LIST",
                exec_context
            ))
        
        if not isinstance(list2, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be LIST",
                exec_context
            ))

        list1.elements.extend(list2.elements)

        return RTResult().success(Number.null)
    execute_extend.arg_names = ["list1", "list2"]

    def execute_sqrt(self, exec_context : Context) -> RTResult:
        value = exec_context.symbol_table.get('value')

        if not isinstance(value, Number):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be INT or FLOAT",
                exec_context
            ))

        try:
            return_value = math.sqrt(value.value)
        except:
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Math domain error: positive number expected",
                exec_context
            ))
        
        return RTResult().success(Number(return_value))
    execute_sqrt.arg_names = ["value"]

    def execute_len(self, exec_context : Context) -> RTResult:
        value = exec_context.symbol_table.get('value')

        if isinstance(value, List):
            return_value = len(value.elements)
            return RTResult().success(Number(return_value))

        
        elif isinstance(value, String):
            return_value = len(value.value)
            return RTResult().success(Number(return_value))
    
        return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be LIST or STRING",
                exec_context
            ))
    execute_len.arg_names = ["value"]

    def execute_sum(self, exec_context : Context) -> RTResult:
        list = exec_context.symbol_table.get('list')

        if not isinstance(list, List):
            return RTResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be LIST",
                exec_context
            ))
        return_value = 0
        for element in list.elements:
            if not isinstance(element, Number):
                return RTResult().failure(RTError(
                    self.pos_start, self.pos_end,
                    "Elements of list must be INT or FLOAT",
                    exec_context
                ))
            return_value += element.value
        return RTResult().success(Number(return_value))
    execute_sum.arg_names = ["list"]


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


###################
# ! INTERPRETER ! #
###################

class Interpreter:
    def visit(self, node : BinOpNode | UnaryOpNode | NumberNode, context : Context) -> RTResult:
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)
    
    def no_visit_method(self, node, context : Context) -> Exception:
        raise Exception(f'No visit_{type(node).__name__} method defined')
    
    ######

    def visit_NumberNode(self, node : NumberNode, context : Context) -> RTResult:
        return RTResult().success(
            Number(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_StringNode(self, node : StringNode, context : Context) -> RTResult:
        return RTResult().success(
            String(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_ListNode(self, node : ListNode, context : Context) -> RTResult:
        result = RTResult()
        elements = []

        for element_node in node.elements_nodes:
            elements.append(result.register(self.visit(element_node, context)))
            if result.error: return result
        
        return result.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    def visit_BinOpNode(self, node : BinOpNode, context : Context) -> RTResult:
        result = RTResult()
        left = result.register(self.visit(node.left_node, context))
        if result.error: return result
        right = result.register(self.visit(node.right_node, context))
        if result.error: return result

        methods = {
            TT_PLUS     : left.add, 
            TT_MINUS    : left.subtract, 
            TT_MUL      : left.multiply, 
            TT_DIV      : left.divide, 
            TT_POW      : left.power,
            TT_MOD      : left.modulo,
            TT_QUO      : left.quotient,
            TT_EE       : left.get_comparison_eq,
            TT_NE       : left.get_comparison_ne,
            TT_LT       : left.get_comparison_lt,
            TT_GT       : left.get_comparison_gt,
            TT_LTE      : left.get_comparison_lte,
            TT_GTE      : left.get_comparison_gte,
            TT_AND      : left.get_and,
            TT_OR       : left.get_or,
            }

        method_result, error = methods[node.op_token.type](right)

        if error: return result.failure(error)
        else : return result.success(method_result.set_pos(node.pos_start, node.pos_end))
    
    def visit_UnaryOpNode(self, node : UnaryOpNode, context : Context) -> RTResult:
        result = RTResult()
        number : Number = result.register(self.visit(node.node, context))
        if result.error: return result

        error = None

        if node.op_token.type == TT_MINUS:
            number, error = number.multiply(Number(-1))
        elif node.op_token.type == TT_NOT:
            number, error = number.not_comp()

        if error: return result.failure(error)
        else: return result.success(number.set_pos(node.pos_start, node.pos_end))
    
    def visit_VarAccessNode(self, node : VarAccessNode, context : Context) -> RTResult:
        result = RTResult()
        var_name = node.var_name_token.value
        value = context.symbol_table.get(var_name)
        if not value:
            return result.failure(RTError(
                node.pos_start, node.pos_end,
                f"'{var_name}' is not defined",
                context
            ))
        
        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return result.success(value)

    def visit_VarAssignNode(self, node : VarAssignNode, context : Context) -> RTResult:
        result = RTResult()
        var_name = node.var_name_token.value
        value = result.register(self.visit(node.value_node, context))
        if result.error: return result

        context.symbol_table.set(var_name, value)
        return result.success(value)

    def visit_IfNode(self, node : IfNode, context : Context) -> RTResult:
        result = RTResult()

        for condition, expression in node.cases:
            condition_value = result.register(self.visit(condition, context))
            if result.error: return result

            if condition_value.is_true():
                expr_value = result.register(self.visit(expression, context))
                if result.error: return result
                return result.success(expr_value)
        
        if node.else_case:
            else_value = result.register(self.visit(node.else_case, context))
            if result.error: return result
            return result.success(else_value)
        return result.success(None)
    
    def visit_ForNode(self, node : ForNode, context : Context) -> RTResult:
        result = RTResult()
        elements = []

        start_value = result.register(self.visit(node.start_value_node, context))
        if result.error: return result

        end_value = result.register(self.visit(node.end_value_node, context))
        if result.error: return result

        if node.step_value_node:
            step_value = result.register(self.visit(node.step_value_node, context))
            if result.error: return result
        else:
            step_value = Number(1 if start_value.value < end_value.value else -1)
        
        i = start_value.value

        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value
        
        while condition():
            context.symbol_table.set(node.var_name_token.value, Number(i))
            i += step_value.value

            elements.append(result.register(self.visit(node.body_node, context)))
            if result.error: return result
        
        return result.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_WhileNode(self, node : WhileNode, context : Context) -> RTResult:
        result = RTResult()
        elements = []

        while True:
            condition = result.register(self.visit(node.condition_node, context))
            if result.error: return result

            if not condition.is_true(): break

            elements.append(result.register(self.visit(node.body_node, context)))
            if result.error: return result

        return result.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_FuncDefNode(self, node : FuncDefNode, context : Context) -> RTResult:
        result = RTResult()

        func_name = node.var_name_token.value if node.var_name_token else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_tokens]

        func_value = Function(func_name, body_node, arg_names).set_context(context).set_pos(node.pos_start, node.pos_end)

        if node.var_name_token:
            context.symbol_table.set(func_name, func_value)

        return result.success(func_value)

    def visit_CallNode(self, node : CallNode, context : Context) -> RTResult:
        result = RTResult()
        args = []

        value_to_call : Function = result.register(self.visit(node.name_node, context))
        if result.error: return result

        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.args_nodes:
            args.append(result.register(self.visit(arg_node, context)))
            if result.error: return result
        
        return_value = result.register(value_to_call.execute(args))
        if result.error: return result

        return result.success(return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context))


###########
# ! RUN ! #
###########

global_symbol_table = SymbolTable()

# * Default values *
global_symbol_table.set("null", Number.null)
global_symbol_table.set("False", Number.false)
global_symbol_table.set("false", Number.false)
global_symbol_table.set("True", Number.true)
global_symbol_table.set("true", Number.true)

# * Built in functions *
global_symbol_table.set("print", BuiltInFunction.print)
global_symbol_table.set("string", BuiltInFunction.string)
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


    # * Run program *
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)


    return result.value, result.error