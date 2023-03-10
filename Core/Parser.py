from Utils.Token import Token
from Utils.ParseResult import ParseResult

from Core.Constants import *

from Errors.InvalidSyntaxError import InvalidSyntaxError

from Nodes.BinOp import BinOpNode
from Nodes.List import ListNode
from Nodes.If import IfNode
from Nodes.For import ForNode
from Nodes.While import WhileNode
from Nodes.FuncDef import FuncDefNode
from Nodes.Call import CallNode
from Nodes.Number import NumberNode
from Nodes.String import StringNode
from Nodes.UnaryOp import UnaryOpNode
from Nodes.VarAccess import VarAccessNode
from Nodes.VarAssign import VarAssignNode
from Nodes.Return import ReturnNode
from Nodes.Continue import ContinueNode
from Nodes.Break import BreakNode


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
        self.update_current_token()
        return self.current_token

    def reverse(self, amount : int = 1) -> Token:
        self.token_index -= amount
        self.update_current_token()
        return self.current_token
    
    def update_current_token(self) -> Token:
        if self.token_index >= 0 and self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
    
    def parse(self) -> ParseResult:
        result = self.statements()
        if not result.error and self.current_token.type != TT_EOF:
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '+', '-', '*', '/', '%', '//', '**', '==', '!=', '<', '>', <=', '>=', '&&' or '||'"
            ))
        return result 

########
    def statements(self) -> ParseResult:
        res = ParseResult()
        statements = []
        pos_start = self.current_token.pos_start.copy()

        while self.current_token.type == TT_NEWLINE:
            res.register_advance()
            self.advance()
        
        statement = res.register(self.statement())
        if res.error: return res
        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            while self.current_token.type == TT_NEWLINE:
                res.register_advance()
                self.advance()
                newline_count += 1
            
            if newline_count == 0:
                more_statements = False
            
            if not more_statements: break
        
            statement = res.try_register(self.statement())
            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)
        
        return res.success(ListNode(
            statements,
            pos_start,
            self.current_token.pos_end.copy()
        ))

    def statement(self) -> ParseResult:
        res = ParseResult()
        pos_start = self.current_token.pos_start.copy()

        if self.current_token.matches(TT_KEYWORD, 'return'):
            res.register_advance()
            self.advance()

            expr = res.try_register(self.expression())
            if not expr:
                self.reverse(res.to_reverse_count)
            return res.success(ReturnNode(expr, pos_start, self.current_token.pos_end.copy()))
        
        if self.current_token.matches(TT_KEYWORD, 'continue'):
            res.register_advance()
            self.advance()
            return res.success(ContinueNode(pos_start, self.current_token.pos_end.copy()))
        
        if self.current_token.matches(TT_KEYWORD, 'break'):
            res.register_advance()
            self.advance()
            return res.success(BreakNode(pos_start, self.current_token.pos_end.copy()))

        expr = res.register(self.expression())
        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected 'return', 'continue', 'break', 'var', 'if', 'for', 'while', 'func', INT, FLOAT, IDENTIFIER, '+', '-', '(' or '!'"
            ))
        return res.success(expr)

#* LIST EXPRESSIONS

    def list_expr(self) -> ParseResult:
        result = ParseResult()
        element_nodes = []

        pos_start = self.current_token.pos_start.copy()

        if not self.current_token.type == TT_LSBRACKET: # LIST
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

#* IF EXPRESSIONS

    def if_expr(self) -> ParseResult:
        result = ParseResult()
        #?print("> if_expr")

        all_cases = result.register(self.if_expr_cases('if'))
        if result.error: return result

        cases, else_case = all_cases
        return result.success(IfNode(cases, else_case))
    
    def if_expr_cases(self, case_keyword) -> ParseResult:
        #?print("> if_expr_cases (case_keyword = " + case_keyword + ")")
        result = ParseResult()
        cases = []
        else_case = None

        #?print("> 0 - current_token = " + str(self.current_token))
        if not self.current_token.matches(TT_KEYWORD, case_keyword):
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected '{case_keyword}'"
            ))
        
        result.register_advance()
        self.advance()

        condition = result.register(self.expression())
        if result.error: return result

        #?print("> 1 - current_token = " + str(self.current_token))
        if not self.current_token.type == TT_LCBRACKET:
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '{'"
            ))
        
        result.register_advance()
        self.advance()

        #?print("> 2 - current_token = " + str(self.current_token))
        if self.current_token.type == TT_NEWLINE:
            #?print('> Retour à la ligne')
            result.register_advance()
            self.advance()

            statements = result.register(self.statements())
            #?print('> statements = ' + str(statements))
            if result.error: return result
            cases.append((condition, statements))

            #?print("> 3 - current_token = " + str(self.current_token))
            if self.current_token.type == TT_RCBRACKET:
                result.register_advance()
                self.advance()

                all_cases = result.register(self.if_expr_bc())
                if result.error: return result
                new_cases, else_case = all_cases
                cases.extend(new_cases)
            else:
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '}'"
                ))
        else:
            #?print('> Pas de retour à la ligne')
            expr = result.register(self.statement())
            #?print('> expr = ' + str(expr))
            if result.error: return result
            cases.append((condition, expr))

            #?print("> 4 - current_token = " + str(self.current_token))
            if not self.current_token.type == TT_RCBRACKET:
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '}'"
                ))
            
            result.register_advance()
            self.advance()

            all_cases = result.register(self.if_expr_bc())
            if result.error: return result
            new_cases, else_case = all_cases
            cases.extend(new_cases)
            
        return result.success((cases, else_case))
    
    def if_expr_b(self) -> ParseResult:
        #?print("> if_expr_b")
        return self.if_expr_cases('elif')
    
    def if_expr_c(self) -> ParseResult:
        #?print("> if_expr_c")
        res = ParseResult()
        else_case = None

        #?print('> 6 - current_token = ' + str(self.current_token))
        if self.current_token.matches(TT_KEYWORD, 'else'):
            res.register_advance()
            self.advance()

            #?print('> 7 - current_token = ' + str(self.current_token))
            if self.current_token.type == TT_LCBRACKET:
                res.register_advance()
                self.advance()

                #?print('> 8 - current_token = ' + str(self.current_token))
                if self.current_token.type == TT_NEWLINE:
                    #?print('> Retour à la ligne')
                    res.register_advance()
                    self.advance()

                    statements = res.register(self.statements())
                    if res.error: return res
                    else_case = statements
                    #?print('> else_case = ' + str(else_case))

                    #?print('> 9 - current_token = ' + str(self.current_token))
                    if self.current_token.type == TT_RCBRACKET:
                        res.register_advance()
                        self.advance()
                    else:
                        res.failure(InvalidSyntaxError(
                            self.current_token.pos_start, self.current_token.pos_end,
                            "Expected '}'"
                        ))
                else:
                    #?print('> Pas de retour à la ligne')
                    expr = res.register(self.statement())
                    if res.error: return res
                    else_case = expr
                    #?print('> else_case = ' + str(else_case))
                    #?print('> 10 - current_token = ' + str(self.current_token))
                    if self.current_token.type != TT_RCBRACKET:
                        res.failure(InvalidSyntaxError(
                            self.current_token.pos_start, self.current_token.pos_end,
                            "Expected '}'"
                        ))
                    res.register_advance()
                    self.advance()
            else:
                res.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '{'"
                ))
        return res.success(else_case)
    
    def if_expr_bc(self) -> ParseResult:
        #?print("> if_expr_bc")
        result = ParseResult()
        cases, else_case = [], None

        #?print("> 5 - current_token = " + str(self.current_token))
        if self.current_token.matches(TT_KEYWORD, 'elif'):
            all_cases = result.register(self.if_expr_b())
            if result.error: return result
            cases, else_case = all_cases
        else:
            else_case = result.register(self.if_expr_c())
            if result.error: return result
        
        return result.success((cases, else_case))
    
#* FOR EXPRESSIONS

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
        
        if not self.current_token.type == TT_LCBRACKET:
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '{'"
            ))
        
        result.register_advance()
        self.advance()

        if self.current_token.type == TT_NEWLINE:
            result.register_advance()
            self.advance()

            body = result.register(self.statements())
            if result.error: return result

            if not self.current_token.type == TT_RCBRACKET:
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '}'"
                ))
            
            result.register_advance()
            self.advance()
        else:
            body = result.register(self.expression())
            if result.error: return result

            if not self.current_token.type == TT_RCBRACKET:
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '}'"
                ))
            
            result.register_advance()
            self.advance()

        return result.success(ForNode(var_name, start_value, end_value, step_value, body))

#* WHILE EXPRESSIONS

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

        if not self.current_token.type == TT_LCBRACKET:
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '{'"
            ))
        
        result.register_advance()
        self.advance()

        if self.current_token.type == TT_NEWLINE:
            result.register_advance()
            self.advance()

            body = result.register(self.statements())
            if result.error: return result

            if not self.current_token.type == TT_RCBRACKET:
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '}'"
                ))
            
            result.register_advance()
            self.advance()
        else:
            body = result.register(self.expression())
            if result.error: return result

            if not self.current_token.type == TT_RCBRACKET:
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '}'"
                ))
            
            result.register_advance()
            self.advance()

        return result.success(WhileNode(condition_value, body))

#* FUNCTION EXPRESSIONS

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

        if self.current_token.type != TT_LCBRACKET:
            return result.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '{'"
            ))
        
        result.register_advance()
        self.advance()
        
        if self.current_token.type == TT_NEWLINE:
            result.register_advance()
            self.advance()

            body_node = result.register(self.statements())
            if result.error: return result

            if not self.current_token.type == TT_RCBRACKET:
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '}'"
                ))
            
            result.register_advance()
            self.advance()
            return result.success(FuncDefNode(func_name_token, arg_name_tokens, body_node, False))
        else:
            body_node = result.register(self.expression())
            if result.error: return result

            if not self.current_token.type == TT_RCBRACKET:
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '}'"
                ))
            
            result.register_advance()
            self.advance()
            return result.success(FuncDefNode(func_name_token, arg_name_tokens, body_node, True))
        

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
						self.current_token.pos_start, self.current_token.pos_end,
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
            var_expr = result.register(self.var_expr())
            if result.error: return result
            return result.success(var_expr)

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

    def var_expr(self) -> ParseResult:
        result = ParseResult()
        token = self.current_token
        slice_or_getter = []

        if token.type != TT_IDENTIFIER:
            return result.failure(InvalidSyntaxError(
                token.pos_start, token.pos_end,
                f"Expected IDENTIFIER"
            ))

        result.register_advance()
        self.advance()

        
        if self.current_token.type == TT_LSBRACKET:
            result.register_advance()
            self.advance()

            if self.current_token.type == TT_COLON:
                slice_or_getter.append(None)
                result.register_advance()
                self.advance()
                slice_or_getter.append(result.register(self.expression()))
                if result.error: return result
            else:
                slice_or_getter.append(result.register(self.expression()))
                if result.error: return result
                if self.current_token.type == TT_COLON:
                    result.register_advance()
                    self.advance()

                    if self.current_token.type == TT_RSBRACKET:
                        slice_or_getter.append(None)

                    else:
                        slice_or_getter.append(result.register(self.expression()))
                        if result.error: return result

            if self.current_token.type == TT_RSBRACKET:
                result.register_advance()
                self.advance()
            else:
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected ']'"
                ))
        return result.success(VarAccessNode(token, slice_or_getter))
    
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

    def expression(self) -> ParseResult:
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
            operator_value = self.current_token

            if self.current_token.type not in (TT_EQ, TT_MINUSEQ, TT_PLUSEQ, TT_DIVEQ, TT_MULEQ, TT_MINUSMINUS, TT_PLUSPLUS):
                return result.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '=' or operators"
                ))
            
            if operator_value.type in (TT_PLUSPLUS, TT_MINUSMINUS):
                current_var_node = VarAccessNode(var_name)
                token_attr = {
                    TT_PLUSPLUS     : TT_PLUS,
                    TT_MINUSMINUS   : TT_MINUS,
                }
                operator_token = token_attr[operator_value.type]
                operator_token = Token(operator_token, pos_start=operator_value.pos_start, pos_end=operator_value.pos_end)
                expression = BinOpNode(current_var_node, operator_token, NumberNode(Token(TT_INT, 1, operator_value.pos_start, operator_value.pos_end)))
                result.register_advance()
                self.advance()
                return result.success(VarAssignNode(var_name, expression))
        
            result.register_advance()
            self.advance()

            expression = result.register(self.expression())
            if result.error: return result
            if operator_value.type in (TT_PLUSEQ, TT_MINUSEQ, TT_MULEQ, TT_DIVEQ):
                current_var_node = VarAccessNode(var_name)
                token_attr = {
                    TT_PLUSEQ       : TT_PLUS,
                    TT_MINUSEQ      : TT_MINUS,
                    TT_MULEQ        : TT_MUL,
                    TT_DIVEQ        : TT_DIV,
                }
                operator_token = token_attr[operator_value.type]
                operator_token = Token(operator_token, pos_start=operator_value.pos_start, pos_end=operator_value.pos_end)
                expression = BinOpNode(current_var_node, operator_token, expression)
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