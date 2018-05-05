import ply.yacc as yacc
import pyscheme.expr as expr

from pyscheme.lex import Lexer
tokens = Lexer.tokens

precedence = (
    ('left', 'LAND', 'LOR', 'LXOR'),
    ('left', 'LNOT'),
    ('left', 'EQ'),
    ('right', 'CONS', 'APPEND'),
    ('left', '+', '-'),
    ('left', '*', '/', '%'),
    ('right', 'THEN')
)


def p_statement_expr(p):
    'statement : statements'
    p[0] = expr.Sequence(expr.List.list(p[1]))


def p_statements_nonempty(p):
    'statements : nstatements'
    p[0] = p[1]


def p_nstatements_expr(p):
    'nstatements : expression'
    p[0] = [p[1]]


def p_nstatements_semicolon(p):
    "nstatements : nstatements ';' expression"
    p[0] = p[1] + [p[3]]


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
    "expression : IF '(' expression ')' '{' statement '}' ELSE '{' statement '}'"
    p[0] = expr.Conditional(p[3], p[6], p[10])


def p_expression_lambda(p):
    "expression : FN '(' formals ')' '{' statement '}'"
    p[0] = expr.Lambda(p[3], p[6])


def p_expression_application(p):
    "expression : expression '(' actuals ')'"
    p[0] = expr.Application(p[1], p[3])


def p_expression_addition(p):
    "expression : expression '+' expression"
    p[0] = application('+', p[1], p[3])


def p_expression_subtraction(p):
    "expression : expression '-' expression"
    p[0] = application('-', p[1], p[3])


def p_expression_multiplication(p):
    "expression : expression '*' expression"
    p[0] = application('*', p[1], p[3])


def p_expression_division(p):
    "expression : expression '/' expression"
    p[0] = application('/', p[1], p[3])


def p_expression_modulus(p):
    "expression : expression '%' expression"
    p[0] = application('%', p[1], p[3])


def p_expression_eq(p):
    "expression : expression EQ expression"
    p[0] = application('==', p[1], p[3])


def p_expression_and(p):
    "expression : expression LAND expression"
    p[0] = application('and', p[1], p[3])


def p_expression_or(p):
    "expression : expression LOR expression"
    p[0] = application('or', p[1], p[3])


def p_expression_not(p):
    "expression : LNOT expression"
    p[0] = application('not', p[2])


def p_expression_xor(p):
    "expression : expression LXOR expression"
    p[0] = application('xor', p[1], p[3])


def p_expression_cons(p):
    "expression : expression CONS expression"
    p[0] = application('@', p[1], p[3])


def p_expression_append(p):
    "expression : expression APPEND expression"
    p[0] = application('@@', p[1], p[3])

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
    p[0] = application('then', p[1], p[3])


def p_expression_fail(p):
    "expression : FAIL"
    p[0] = application('fail')


def p_expression_define(p):
    "expression : DEFINE symbol '=' expression"
    p[0] = application('define', p[2], p[4])

def p_error(p):
    if p is not None:  # EOF
        print("syntax error in lambda input: " + str(p))


def application(name: str, *args):
    return expr.Application(expr.Symbol.make(name), expr.List.list(args))


# Build the parser
parser = yacc.yacc()
