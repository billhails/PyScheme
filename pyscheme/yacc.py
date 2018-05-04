import ply.yacc as yacc
import pyscheme.expr as expr

from pyscheme.lex import Lexer
tokens = Lexer.tokens

precedence = (
    ('left', 'LAND', 'LOR', 'LXOR'),
    ('left', 'LNOT'),
    ('left', 'EQ'),
    ('right', 'CONS', 'APPEND'),
    ('left', '+'),
    ('right', 'THEN')
)

def p_expression_id(p):
    'expression : symbol'
    p[0] = p[1]


def p_symbol(p):
    'symbol : ID'
    p[0] = expr.Symbol.make(p[1])


def p_expression_number(p):
    'expression : number'
    p[0] = p[1]


def p_number(p):
    'number : NUMBER'
    p[0] = expr.Constant(p[1])


def p_expression_boolean(p):
    'expression : boolean'
    p[0] = p[1]


def p_boolean_true(p):
    'boolean : TRUE'
    p[0] = expr.Boolean.true()


def p_boolean_false(p):
    'boolean : FALSE'
    p[0] = expr.Boolean.false()


def p_boolean_unknown(p):
    'boolean : UNKNOWN'
    p[0] = expr.Boolean.unknown()


def p_expression_list(p):
    'expression : list'
    p[0] = p[1]


def p_list_literal(p):
    "list : '[' exprs ']'"
    p[0] = expr.List.list(p[2])


def p_expression_conditional(p):
    "expression : IF '(' expression ')' '{' expression '}' ELSE '{' expression '}'"
    p[0] = expr.Conditional(p[3], p[6], p[10])


def p_expression_lambda(p):
    "expression : FN '(' formals ')' '{' expression '}'"
    p[0] = expr.Lambda(p[3], p[6])


def p_expression_application(p):
    "expression : expression '(' actuals ')'"
    p[0] = expr.Application(p[1], p[3])


def p_expression_addition(p):
    "expression : expression '+' expression"
    p[0] = expr.Application(expr.Symbol.make('+'), expr.List.list([p[1], p[3]]))


def p_expression_eq(p):
    "expression : expression EQ expression"
    p[0] = expr.Application(expr.Symbol.make('=='), expr.List.list([p[1], p[3]]))


def p_expression_and(p):
    "expression : expression LAND expression"
    p[0] = expr.Application(expr.Symbol.make('and'), expr.List.list([p[1], p[3]]))


def p_expression_or(p):
    "expression : expression LOR expression"
    p[0] = expr.Application(expr.Symbol.make('or'), expr.List.list([p[1], p[3]]))


def p_expression_not(p):
    "expression : LNOT expression"
    p[0] = expr.Application(expr.Symbol.make('not'), expr.List.list([p[2]]))


def p_expression_xor(p):
    "expression : expression LXOR expression"
    p[0] = expr.Application(expr.Symbol.make('xor'), expr.List.list([p[1], p[3]]))


def p_expression_cons(p):
    "expression : expression CONS expression"
    p[0] = expr.Application(expr.Symbol.make('@'), expr.List.list([p[1], p[3]]))


def p_expression_append(p):
    "expression : expression APPEND expression"
    p[0] = expr.Application(expr.Symbol.make('@@'), expr.List.list([p[1], p[3]]))

def p_expression_parentheses(p):
    "expression : '(' expression ')'"
    p[0] = p[1]


def p_actuals(p):
    "actuals : exprs"
    p[0] = expr.List.list(p[1])


def p_formals(p):
    "formals : fargs"
    p[0] = expr.List.list(p[1])


def p_fargs_empty(p):
    'fargs : '
    p[0] = []


def p_fargs_nonempty(p):
    'fargs : nfargs'
    p[0] = p[1]


def p_nfargs_symbol(p):
    'nfargs : symbol'
    p[0] = [p[1]]


def p_nfargs_comma(p):
    "nfargs : nfargs ',' symbol"
    p[0] = p[1] + [p[3]]


def p_exprs_empty(p):
    'exprs : '
    p[0] = []


def p_exprs_nonempty(p):
    'exprs : nexprs'
    p[0] = p[1]


def p_nexprs_expr(p):
    'nexprs : expression'
    p[0] = [p[1]]


def p_nexprs_comma(p):
    "nexprs : nexprs ',' expression"
    p[0] = p[1] + [p[3]]


def p_expression_then(p):
    "expression : expression THEN expression"
    p[0] = expr.Application(expr.Symbol.make('then'), expr.List.list([p[1], p[3]]))


def p_expression_fail(p):
    "expression : FAIL"
    p[0] = expr.Application(expr.Symbol.make('fail'), expr.List.null())

def p_error(p):
    if p is not None:  # EOF
        print("syntax error in lambda input: " + str(p))


# Build the parser
parser = yacc.yacc()
