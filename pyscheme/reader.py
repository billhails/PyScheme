# PyScheme lambda language written in Python
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

from pyscheme.exceptions import SyntaxError
import pyscheme.expr as expr
from typing import TypeVar, Union
import regex

S = TypeVar('S')
Maybe = Union[S, None]


class Token:
    def __init__(self, token_type, token_value=''):
        self.type = token_type
        self.value = token_value

    def __str__(self):
        return '<' + self.type + ': ' + self.value + '>'

    __repr__ = __str__


class Tokeniser:
    reserved = {
        'if': 'IF',
        'else': 'ELSE',
        'fn': 'FN',
        'true': 'TRUE',
        'false': 'FALSE',
        'unknown': 'UNKNOWN',
        'and': 'AND',
        'or': 'OR',
        'not': 'NOT',
        'xor': 'XOR',
        'then': 'THEN',
        'back': 'BACK',
        'define': 'DEFINE',
    }

    regexes = {
        r'([a-zA-Z_][a-zA-Z_0-9]*)': 'ID',
        r'(\d+)': 'NUMBER',
        r'"(\\.|[^"])*"': 'STRING',
        r"'(\\.|[^'])'": 'CHAR',
    }

    literals = (
        '@@', '@',
        '==', '>=', '<=', '>', '<', '!=',
        '+', '-', '*', '/', '%',
        '{', '}',
        '(', ')',
        ',',
        '[', ']',
        ';',
        '=',
    )

    def __init__(self, stream):
        self._stream = stream
        self._line_number = 0
        self._tokens = []
        self._line = ''

    def swallow(self, name: str) -> Maybe[Token]:
        token = self.next_token()
        if token.type == name:
            return token
        else:
            self._tokens += [token]
            return None

    def peek(self) -> Maybe[Token]:
        token = self.next_token()
        self._tokens += [token]
        return token

    def line_number(self):
        return self._line_number

    def next_token(self) -> Maybe[Token]:
        if len(self._tokens) > 0:
            return self._tokens.pop()
        else:
            while self._line == '':
                self._line = self._stream.readline()
                if self._line == '':  # EOF
                    return Token('EOF')
                self._line_number += 1
                self._line = self._line.lstrip()
                self._line = regex.sub(r'^//.*', '', self._line, 1)
            for rex in self.regexes.keys():
                match = regex.match(rex, self._line)
                if match:
                    self._line = regex.sub(rex, '', self._line, 1).lstrip()
                    self._line = regex.sub(r'^//.*', '', self._line, 1)
                    text = match.group(1)
                    if self.regexes[rex] == 'ID':
                        if text in self.reserved:
                            return Token(self.reserved[text], text)
                        else:
                            return Token('ID', text)
                    else:
                        return Token(self.regexes[rex], text)
            for literal in self.literals:
                if self._line.startswith(literal):
                    self._line = self._line[len(literal):].lstrip()
                    self._line = regex.sub(r'^//.*', '', self._line, 1)
                    return Token(literal, literal)
            return Token('ERROR', self._line)




class Reader:
    def __init__(self, tokeniser: Tokeniser, stderr):
        self.tokeniser = tokeniser
        self.stderr = stderr

    def read(self) -> expr.Expr:
        return self.statement()

    def statement(self, fail=True) -> expr.Expr:
        """
            statement : expression ';'
                      | IF '(' expression ')' '{' statements '}' ELSE '{' statements '}'
                      | FN symbol '(' formals ')' '{' statements '}'
        """
        if self.swallow('IF'):
            self.consume('(')
            test = self.expression()
            self.consume(')', '{')
            consequent = self.statements()
            self.consume('}', 'ELSE', '{')
            alternative = self.statements()
            self.consume('}')
            return expr.Conditional(test, consequent, alternative)
        elif self.swallow('FN'):
            symbol = self.symbol()
            self.consume('(')
            formals = self.formals()
            self.consume(')', '{')
            body = self.statements()
            self.consume('}')
            return self.apply_string('define', symbol, expr.Lambda(formals, body))
        else:
            expression = self.expression(fail)
            self.consume(';')
            return expression

    def statements(self) -> expr.Sequence:
        """
            statements : multi_statement
        """
        return expr.Sequence(self.multi_statement())

    def multi_statement(self, fail=True) -> expr.List:
        """
            multi_statement : statement
                            | statement multi_statement
        """
        statement = self.statement(fail)
        if statement is None:
            return expr.Null()
        else:
            multi_statement = self.multi_statement(False)  # may return empty list
            return expr.Pair(statement, multi_statement)

    def expression(self, fail=True) -> Maybe[expr.Expr]:
        """
            expression : prec_1 '(' actuals ')'
                       | prec_1
        """
        prec_1 = self.prec_1(fail)
        if prec_1 is None:
            return None
        if self.swallow('('):
            actuals = self.exprs()
            self.consume(')')
            return expr.Application(prec_1, actuals)

    def binop(self, m_lhs, ops, m_rhs, fail) -> Maybe[expr.Expr]:
        lhs = m_lhs(fail)
        if lhs is None:
            return None
        op = self.swallow(*ops)
        if op:
            rhs = m_rhs()
            return self.apply_token(op, lhs, rhs)
        else:
            return lhs

    def prec_1(self, fail=True) -> Maybe[expr.Expr]:
        """
            prec_1 : prec_2 '*' prec_1
                   | prec_2 '/' prec_1
                   | prec_2 '%' prec_1
                   | prec_2
        """
        return self.binop(self.prec_2, ['*', '/', '%'], self.prec_1, fail)

    def prec_2(self, fail=True) -> Maybe[expr.Expr]:
        """
            prec_2 : prec_3 '+' prec_2
                   | prec_3 '-' prec_2
                   | prec_3
        """
        return self.binop(self.prec_3, ['+', '-'], self.prec_2, fail)

    def prec_3(self, fail=True) -> Maybe[expr.Expr]:
        """
            prec_3 : prec_4 CONS prec_3
                   | prec_4 APPEND prec_3
                   | prec_4
        """
        return self.binop(self.prec_4, ['@', '@@'], self.prec_3, fail)

    def prec_4(self, fail=True) -> Maybe[expr.Expr]:
        """
            prec_4 : prec_5 EQ prec_4
                   | prec_5 NE prec_4
                   | prec_5 GT prec_4
                   | prec_5 LT prec_4
                   | prec_5 GE prec_4
                   | prec_5 LE prec_4
                   | prec_5
        """
        return self.binop(self.prec_5, ['==', '!=', '>', '<', '>=', '<='], self.prec_4, fail)

    def prec_5(self, fail=True) -> Maybe[expr.Expr]:
        """
            prec_5 : LNOT prec_6
                   | prec_6
        """
        token = self.swallow('NOT')
        if token:
            return self.apply_token(token, self.prec_6())
        else:
            return self.prec_6(fail)

    def prec_6(self, fail=True) -> Maybe[expr.Expr]:
        """
            prec_6 : prec_7 LAND prec_6
                   | prec_7 LOR prec_6
                   | prec_7 LXOR prec_6
                   | prec_7
        """
        return self.binop(self.prec_7, ['AND', 'OR', 'XOR'], self.prec_6, fail)

    def prec_7(self, fail=True) -> Maybe[expr.Expr]:
        """
            prec_7 : prec_8 THEN prec_7
                   | prec_8
        """
        return self.binop(self.prec_8, ['THEN'], self.prec_7, fail)

    def prec_8(self, fail=True) -> Maybe[expr.Expr]:
        """
            prec_8 : symbol
                   | number
                   | string
                   | char
                   | boolean
                   | lst
                   | FN '(' formals ')' '{' statements '}'
                   | DEFINE symbol '=' expression
                   | BACK
                   | '(' expression ')'
        """
        symbol = self.symbol(False)
        if symbol:
            return symbol

        number = self.number(False)
        if number:
            return number

        string = self.string(False)
        if string:
            return string

        char = self.char(False)
        if char:
            return char

        boolean = self.boolean(False)
        if boolean is not None:
            return boolean

        lst = self.lst(False)
        if lst:
            return lst

        if self.swallow('FN'):
            self.consume('(')
            formals = self.formals()
            self.consume(')', '{')
            statements = self.statements()
            self.consume('}')
            return expr.Lambda(formals, statements)

        token = self.swallow('DEFINE')
        if token:
            symbol = self.symbol()
            self.consume('=')
            expression = self.expression()
            return self.apply_token(token, symbol, expression)

        if self.swallow('('):
            expression = self.expression()
            self.consume(')')
            return expression
        elif fail:
            self.error("expected '('")
        else:
            return None

    def symbol(self, fail=True) -> Maybe[expr.Symbol]:
        """
            symbol : ID
        """
        identifier = self.swallow('ID')
        if identifier:
            return expr.Symbol(identifier.value)
        elif fail:
            self.error("expected id")
        else:
            return None

    def number(self, fail=True) -> Maybe[expr.Constant]:
        """
            number : NUMBER
        """
        number = self.swallow('NUMBER')
        if number:
            return expr.Constant(number.value)
        elif fail:
            self.error("expected number")
        else:
            return None

    def string(self, fail=True) -> Maybe[expr.Constant]:
        """
            string : STRING
        """
        string = self.swallow('STRING')
        if string:
            return expr.Constant(string.value)
        elif fail:
            self.error("expected string")
        else:
            return None

    def char(self, fail=True) -> Maybe[expr.Char]:
        """
            char : CHAR
        """
        char = self.swallow('CHAR')
        if char:
            return expr.Char(char.value)
        elif fail:
            self.error("expected char")
        else:
            return None

    def boolean(self, fail=True) -> Maybe[expr.Boolean]:
        """
            boolean : TRUE
                    | FALSE
                    | UNKNOWN
        """
        token = self.swallow('TRUE')
        if token:
            return expr.T()

        token = self.swallow('FALSE')
        if token:
            return expr.F()

        token = self.swallow('UNKNOWN')
        if token:
            return expr.U()

        if fail:
            self.error("expected boolean")
        else:
            return None

    def lst(self, fail=True) -> Maybe[expr.List]:
        """
            list : '[' exprs ']'
        """
        if self.swallow('['):
            exprs = self.exprs()
            self.consume(']')
            return exprs
        elif fail:
            self.error("expected '['")
        else:
            return None

    def formals(self) -> expr.List:
        """
            formals : empty
            formals : symbol
            formals : symbol ',' nfargs
        """
        symbol = self.symbol(False)
        if symbol is None:
            return expr.Null()
        if self.swallow(','):
            fargs = self.formals()
            return expr.Pair(symbol, fargs)
        else:
            return expr.List.list([symbol])

    def exprs(self) -> expr.List:
        """
            exprs : empty
            exprs : expression
            exprs : expression ',' exprs
        """
        expression = self.symbol(False)
        if expression is None:
            return expr.Null()
        if self.swallow(','):
            exprs = self.exprs()
            return expr.Pair(expression, exprs)
        else:
            return expr.List.list([expression])

    def apply_token(self, token: Token, *args):
        return self.apply_string(token.value, *args)

    @classmethod
    def apply_string(cls, name: str, *args):
        return expr.Application(expr.Symbol(name), expr.List.list(args))

    def swallow(self, *args) -> Maybe[Token]:
        """
        if the next token in the input matches one of the argument types, consume it and return the token
        otherwise leave it in the input stream and return None
        :param args: array
        :return: bool
        """
        for token_type in args:
            token = self.tokeniser.swallow(token_type)
            if token is not None:
                return token
        return None

    def consume(self, *args):
        """
        for each argument, read the next token and check that it matches, throw an error if not
        :param args:
        :return: void
        """
        for name in args:
            if self.tokeniser.swallow(name) is None:
                self.error("expected " + name)

    def error(self, msg):
        self.stderr.write(msg + "\n")
        raise SyntaxError(
            msg,
            line=self.tokeniser.line_number(),
            next=self.tokeniser.peek().value
        )
