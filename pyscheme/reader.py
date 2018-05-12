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
from pyscheme.types import Maybe
import re
import inspect
import io

class Token:
    def __init__(self, token_type, token_value=''):
        self.type = token_type
        self.value = token_value

    def __str__(self) -> str:
        if self.type == self.value:
            return '<' + str(self.type) + '>'
        else:
            return '<' + str(self.type) + ': ' + str(self.value) + '>'

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
        r'"((\\.|[^"])*)"': 'STRING',
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

    def __init__(self, stream: io.StringIO):
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
        self.pushback(token)
        return token

    def pushback(self, token: Token) -> None:
        self._tokens += [token]

    def line_number(self) -> int:
        return self._line_number

    def next_token(self) -> Maybe[Token]:
        if len(self._tokens) > 0:
            return self._tokens.pop()
        else:
            while self._line == '':
                self._line = self._stream.readline()
                if self._line == '':  # EOF
                    return Token('EOF', 'EOF')
                self._line_number += 1
                self._line = self._line.strip()
                self._line = re.sub(r'^//.*', '', self._line, 1)
            for rex in self.regexes.keys():
                match = re.match(rex, self._line)
                if match:
                    self._line = re.sub(rex, '', self._line, 1).strip()
                    self._line = re.sub(r'^//.*', '', self._line, 1)
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
                    self._line = re.sub(r'^//.*', '', self._line, 1)
                    return Token(literal, literal)
            return Token('ERROR', self._line)

    def __str__(self) -> str:
        return "<tokens: " + str(self._tokens) + ' remaining: "' + self._line + '">'

    __repr__ = __str__


class Reader:
    """
        statement : expression ';'
                  | IF '(' expression ')' '{' statements '}' ELSE '{' statements '}'
                  | FN symbol '(' formals ')' '{' statements '}'

        statements : multi_statement

        multi_statement : statement
                        | statement multi_statement

        expression : binop_then

        binop_then : binop_and THEN binop_then
               | binop_and

        binop_and : unop_not {AND unop_not}
               | unop_not {OR unop_not}
               | unop_not {XOR unop_not}
               | unop_not

        unop_not : NOT unop_not
               | binop_compare

        binop_compare : binop_cons EQ binop_cons
               | binop_cons NE binop_cons
               | binop_cons GT binop_cons
               | binop_cons LT binop_cons
               | binop_cons GE binop_cons
               | binop_cons LE binop_cons
               | binop_cons

        binop_cons : binop_add CONS binop_cons
               | binop_add APPEND binop_cons
               | binop_add

        binop_add : binop_mul {'+' binop_mul}
               | binop_mul {'-' binop_mul}
               | binop_mul

        binop_mul : op_funcall {'*' op_funcall}
               | op_funcall {'/' op_funcall}
               | op_funcall {'%' op_funcall}
               | op_funcall

        op_funcall : atom {'(' actuals ')'}
                   | atom

        atom : symbol
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

    debugging = False

    def __init__(self, tokeniser: Tokeniser, stderr: io.StringIO):
        self.tokeniser = tokeniser
        self.stderr = stderr
        self.depth = 0

    def read(self) -> expr.Expr:
        if self.debugging:
            self.depth=len(inspect.stack())
        self.debug("*******************************************************")
        result = self.statement()
        self.debug("read", result=result)
        return result

    def statement(self, fail=True) -> expr.Expr:
        """
            statement : expression ';'
                      | IF '(' expression ')' '{' statements '}' ELSE '{' statements '}'
                      | FN symbol '(' formals ')' '{' statements '}'
                      | EOF
        """
        self.debug("statement", fail=fail)
        if self.swallow('EOF'):
            return None

        if self.swallow('IF'):
            self.consume('(')
            test = self.expression()
            self.consume(')', '{')
            consequent = self.statements()
            self.consume('}', 'ELSE', '{')
            alternative = self.statements()
            self.consume('}')
            return expr.Conditional(test, consequent, alternative)

        fn = self.swallow('FN')
        if fn is not None:
            symbol = self.symbol(False)
            if symbol is None:
                self.pushback(fn)
            else:
                self.consume('(')
                formals = self.formals()
                self.consume(')', '{')
                body = self.statements()
                self.consume('}')
                return self.apply_string('define', symbol, expr.Lambda(formals, body))

        expression = self.expression(fail)
        if expression is not None:
            self.consume(';')
        return expression



    def statements(self) -> expr.Sequence:
        """
            statements : multi_statement
        """
        self.debug("statements")
        return expr.Sequence(self.multi_statement())

    def multi_statement(self, fail=True) -> expr.List:
        """
            multi_statement : statement
                            | statement multi_statement
        """
        self.debug("multi_statement", fail=fail)
        statement = self.statement(fail)
        if statement is None:
            return expr.Null()
        else:
            multi_statement = self.multi_statement(False)  # may return empty list
            return expr.Pair(statement, multi_statement)

    def expression(self, fail=True):
        """
            expression : binop_then
        """
        return self.binop_then(fail)

    def binop_then(self, fail=True) -> Maybe[expr.Expr]:
        """
            binop_then : binop_and THEN binop_then
                   | binop_and
        """
        self.debug("binop_then", fail=fail)
        return self.rassoc_binop(self.binop_and, ['THEN'], self.binop_then, fail)

    def binop_and(self, fail=True) -> Maybe[expr.Expr]:
        """
            binop_and : unop_not {AND unop_not}
                   | unop_not {OR unop_not}
                   | unop_not {XOR unop_not}
                   | unop_not
        """
        self.debug("binop_and", fail=fail)
        return self.lassoc_binop(self.unop_not, ['AND', 'OR', 'XOR'], fail)

    def unop_not(self, fail=True) -> Maybe[expr.Expr]:
        """
            unop_not : NOT unop_not
                   | binop_compare
        """
        self.debug("unop_not", fail=fail)
        token = self.swallow('NOT')
        if token:
            return self.apply_token(token, self.unop_not())
        else:
            return self.binop_compare(fail)

    def binop_compare(self, fail=True) -> Maybe[expr.Expr]:
        """
            binop_compare : binop_cons EQ binop_cons
                   | binop_cons NE binop_cons
                   | binop_cons GT binop_cons
                   | binop_cons LT binop_cons
                   | binop_cons GE binop_cons
                   | binop_cons LE binop_cons
                   | binop_cons
        """
        self.debug("binop_compare", fail=fail)
        return self.rassoc_binop(self.binop_cons, ['==', '!=', '>', '<', '>=', '<='], self.binop_cons, fail)

    def binop_cons(self, fail=True) -> Maybe[expr.Expr]:
        """
            binop_cons : binop_add CONS binop_cons
                   | binop_add APPEND binop_cons
                   | binop_add
        """
        self.debug("binop_cons", fail=fail)
        return self.rassoc_binop(self.binop_add, ['@', '@@'], self.binop_cons, fail)

    def binop_add(self, fail=True) -> Maybe[expr.Expr]:
        """
            binop_add : binop_mul '+' binop_add
                   | binop_mul '-' binop_add
                   | binop_mul
        """
        self.debug("binop_add", fail=fail)
        return self.lassoc_binop(self.binop_mul, ['+', '-'], fail)

    def binop_mul(self, fail=True) -> Maybe[expr.Expr]:
        """
            binop_mul : op_funcall {'*' op_funcall}
                   | op_funcall {'/' op_funcall}
                   | op_funcall {'%' op_funcall}
                   | op_funcall
        """
        self.debug("binop_mul", fail=fail)
        return self.lassoc_binop(self.op_funcall, ['*', '/', '%'], fail)

    def op_funcall(self, fail=True) -> Maybe[expr.Expr]:
        """
            op_funcall : atom {'(' actuals ')'}
                       | atom
        """
        self.debug("op_funcall", fail=fail)
        atom = self.atom(fail)
        if atom is None:
            return None
        while True:
            if self.swallow('('):
                actuals = self.exprs()
                self.consume(')')
                atom = expr.Application(atom, actuals)
            else:
                return atom

    def atom(self, fail=True) -> Maybe[expr.Expr]:
        """
            atom : symbol
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
        self.debug("atom", fail=fail)
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
        if lst is not None:
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

        token = self.swallow('BACK')
        if token:
            return self.apply_token(token)

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
        self.debug("symbol", fail=fail)
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
        self.debug("number", fail=fail)
        number = self.swallow('NUMBER')
        if number:
            return expr.Constant(int(number.value))
        elif fail:
            self.error("expected number")
        else:
            return None

    def string(self, fail=True) -> Maybe[expr.Constant]:
        """
            string : STRING
        """
        self.debug("string", fail=fail)
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
        self.debug("char", fail=fail)
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
        self.debug("boolean", fail=fail)
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
        self.debug("lst", fail=fail)
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
        self.debug("formals")
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
        self.debug("exprs")
        expression = self.expression(False)
        if expression is None:
            return expr.Null()
        if self.swallow(','):
            exprs = self.exprs()
            return expr.Pair(expression, exprs)
        else:
            return expr.List.list([expression])

    def rassoc_binop(self, m_lhs, ops, m_rhs, fail) -> Maybe[expr.Expr]:
        lhs = m_lhs(fail)
        if lhs is None:
            return None
        op = self.swallow(*ops)
        if op:
            rhs = m_rhs()
            return self.apply_token(op, lhs, rhs)
        else:
            return lhs

    def lassoc_binop(self, method, ops, fail):
        lhs = method(fail)
        if lhs is None:
            return None
        while True:
            op = self.swallow(*ops)
            if op:
                rhs = method()
                lhs = self.apply_token(op, lhs, rhs)
            else:
                return lhs

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
        self.debug("swallow", args=args, caller=inspect.stack()[1][3])
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
        self.debug("consume", args=args, caller=inspect.stack()[1][3])
        for name in args:
            if self.tokeniser.swallow(name) is None:
                self.error("expected " + name)

    def pushback(self, token: Token):
        self.tokeniser.pushback(token)

    def error(self, msg):
        self.stderr.write(msg + "\n")
        raise SyntaxError(
            msg,
            line=self.tokeniser.line_number(),
            next=self.tokeniser.peek().value
        )

    def debug(self, *args, **kwargs):
        if self.debugging:
            depth = len(inspect.stack()) - self.depth
            print('   |' * (depth // 4), end='')
            print(' ' * (depth % 4), end='')
            for arg in args:
                print(arg, end=' ')
            for k in kwargs:
                print(k + '=' + str(kwargs[k]), end=' ')
            print(self.tokeniser)
