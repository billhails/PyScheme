# PyScheme lambda language written in Python
#
# laguage parser
#
# Copyright (C) 2018  Bill Hails
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import ply.yacc as yacc
import pyscheme.expr as expr

from pyscheme.lex import Lexer

tokens = Lexer.tokens

precedence = (
    ('right', 'THEN'),
    ('left', 'LAND', 'LOR', 'LXOR'),
    ('left', 'LNOT'),
    ('left', 'EQ', 'GT', 'LT', 'GE', 'LE', 'NE'),
    ('right', 'CONS', 'APPEND'),
    ('left', '+', '-'),
    ('left', '*', '/', '%'),
    ('left', '('),
)


def p_statement_expr(p):
    "statement : op_funcall ';'"
    p[0] = p[1]


def p_statement_conditional(p):
    "statement : IF '(' op_funcall ')' '{' statements '}' ELSE '{' statements '}'"
    p[0] = expr.Conditional(p[3], p[6], p[10])


def p_statement_fn(p):
    "statement : FN symbol '(' formals ')' '{' statements '}'"
    p[0] = application('define', p[2], expr.Lambda(p[4], p[7]))


def p_statements_multi_statement(p):
    "statements : multi_statement"
    p[0] = expr.Sequence(p[1])


def p_multi_statement_statement(p):
    "multi_statement : inner_statement"
    p[0] = expr.List.list([p[1]])


def p_multi_statement_statements(p):
    "multi_statement : inner_statement multi_statement"
    p[0] = expr.Pair(p[1], p[2])

def p_inner_statement_expr(p):
    "inner_statement : op_funcall ';'"
    p[0] = p[1]


def p_inner_statement_conditional(p):
    "inner_statement : IF '(' op_funcall ')' '{' statements '}' ELSE '{' statements '}'"
    p[0] = expr.Conditional(p[3], p[6], p[10])


def p_inner_statement_fn(p):
    "inner_statement : FN symbol '(' formals ')' '{' statements '}'"
    p[0] = application('define', p[2], expr.Lambda(p[4], p[7]))


def p_expression_id(p):
    'op_funcall : symbol'
    p[0] = p[1]


def p_symbol(p):
    'symbol : ID'
    p[0] = expr.Symbol(p[1])


def p_expression_number(p):
    'op_funcall : number'
    p[0] = p[1]


def p_number(p):
    'number : NUMBER'
    p[0] = expr.Constant(p[1])


def p_expression_string(p):
    'op_funcall : string'
    p[0] = p[1]


def p_string(p):
    'string : STRING'
    p[0] = expr.Constant(p[1])


def p_expression_char(p):
    'op_funcall : char'
    p[0] = p[1]


def p_char(p):
    'char : CHAR'
    p[0] = expr.Char(p[1])


def p_expression_boolean(p):
    'op_funcall : boolean'
    p[0] = p[1]


def p_boolean_true(p):
    'boolean : TRUE'
    p[0] = expr.T()


def p_boolean_false(p):
    'boolean : FALSE'
    p[0] = expr.F()


def p_boolean_unknown(p):
    'boolean : UNKNOWN'
    p[0] = expr.U()


def p_expression_list(p):
    'op_funcall : list'
    p[0] = p[1]


def p_list_literal(p):
    "list : '[' exprs ']'"
    p[0] = expr.List.list(p[2])


def p_expression_lambda(p):
    "op_funcall : FN '(' formals ')' '{' statements '}'"
    p[0] = expr.Lambda(p[3], p[6])


def p_expression_define(p):
    "op_funcall : DEFINE symbol '=' op_funcall"
    p[0] = application('define', p[2], p[4])


def p_expression_application(p):
    "op_funcall : op_funcall '(' actuals ')'"
    p[0] = expr.Application(p[1], p[3])


def p_expression_addition(p):
    "op_funcall : op_funcall '+' op_funcall"
    p[0] = application('+', p[1], p[3])


def p_expression_subtraction(p):
    "op_funcall : op_funcall '-' op_funcall"
    p[0] = application('-', p[1], p[3])


def p_expression_multiplication(p):
    "op_funcall : op_funcall '*' op_funcall"
    p[0] = application('*', p[1], p[3])


def p_expression_division(p):
    "op_funcall : op_funcall '/' op_funcall"
    p[0] = application('/', p[1], p[3])


def p_expression_modulus(p):
    "op_funcall : op_funcall '%' op_funcall"
    p[0] = application('%', p[1], p[3])


def p_expression_eq(p):
    "op_funcall : op_funcall EQ op_funcall"
    p[0] = application('==', p[1], p[3])


def p_expression_ne(p):
    "op_funcall : op_funcall NE op_funcall"
    p[0] = application('!=', p[1], p[3])


def p_expression_gt(p):
    "op_funcall : op_funcall GT op_funcall"
    p[0] = application('>', p[1], p[3])


def p_expression_lt(p):
    "op_funcall : op_funcall LT op_funcall"
    p[0] = application('<', p[1], p[3])


def p_expression_ge(p):
    "op_funcall : op_funcall GE op_funcall"
    p[0] = application('>=', p[1], p[3])


def p_expression_le(p):
    "op_funcall : op_funcall LE op_funcall"
    p[0] = application('<=', p[1], p[3])


def p_expression_and(p):
    "op_funcall : op_funcall LAND op_funcall"
    p[0] = application('and', p[1], p[3])


def p_expression_or(p):
    "op_funcall : op_funcall LOR op_funcall"
    p[0] = application('or', p[1], p[3])


def p_expression_not(p):
    "op_funcall : LNOT op_funcall"
    p[0] = application('not', p[2])


def p_expression_xor(p):
    "op_funcall : op_funcall LXOR op_funcall"
    p[0] = application('xor', p[1], p[3])


def p_expression_cons(p):
    "op_funcall : op_funcall CONS op_funcall"
    p[0] = application('@', p[1], p[3])


def p_expression_append(p):
    "op_funcall : op_funcall APPEND op_funcall"
    p[0] = application('@@', p[1], p[3])

def p_expression_parentheses(p):
    "op_funcall : '(' op_funcall ')'"
    p[0] = p[2]


def p_actuals(p):
    "actuals : exprs"
    p[0] = expr.List.list(p[1])


def p_formals(p):
    "formals : formals"
    p[0] = expr.List.list(p[1])


def p_fargs_empty(p):
    'formals : '
    p[0] = []


def p_fargs_nonempty(p):
    'formals : nfargs'
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
    'nexprs : op_funcall'
    p[0] = [p[1]]


def p_nexprs_comma(p):
    "nexprs : nexprs ',' op_funcall"
    p[0] = p[1] + [p[3]]


def p_expression_then(p):
    "op_funcall : op_funcall THEN op_funcall"
    p[0] = application('binop_then', p[1], p[3])


def p_expression_back(p):
    "op_funcall : BACK"
    p[0] = application('back')


def p_error(p):
    if p is not None:  # EOF
        print("syntax error in lambda input: " + str(p))


def application(name: str, *args):
    return expr.Application(expr.Symbol(name), expr.List.list(args))


# Build the parser
parser = yacc.yacc()
