import ply.yacc as yacc

import pyscheme.expr as expr
import pyscheme.list as list

from pyscheme.lex import tokens

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
    p[0] = expr.Application(expr.Symbol.make('+'), list.List.list(p[1], p[3]))


def p_expression_parentheses(p):
    "expression : '(' expression ')'"
    p[0] = p[1]


def p_actuals(p):
    "actuals : aargs"
    p[0] = list.List.list(*(p[1]))


def p_formals(p):
    "formals : fargs"
    p[0] = list.List.list(*(p[1]))


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


def p_aargs_empty(p):
    'aargs : '
    p[0] = []


def p_aargs_nonempty(p):
    'aargs : naargs'
    p[0] = p[1]


def p_naargs_expr(p):
    'naargs : expression'
    p[0] = [p[1]]


def p_naargs_comma(p):
    "naargs : naargs ',' expression"
    p[0] = p[1]+ [p[3]]


def p_error(p):
    print("syntax error in lambda input")


# Build the parser
parser = yacc.yacc()
