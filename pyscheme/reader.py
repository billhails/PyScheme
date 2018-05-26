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

from .exceptions import PySchemeSyntaxError
import pyscheme.expr as expr
from .types import Maybe
import re
import inspect
import io


class Config:
    debugging = False


class Token:
    def __init__(self, line: int, char: int, token_type, token_value=''):
        self.line = line
        self.char = char
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
        'env': 'ENV',
        'typedef': 'TYPEDEF',
        'nothing': 'NOTHING',
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
        '**', '+', '-', '*', '/', '%',
        '{', '}',
        '(', ')',
        ',',
        '[', ']',
        ';',
        '=',
        '.',
        ':',
        '|',
    )

    def __init__(self, stream: io.StringIO):
        self._stream = stream
        self._line_number = 0
        self._character_position = 0
        self._tokens = []
        self._line = ''

    def match(self, name: str) -> Maybe[Token]:
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
                    return self.new_token('EOF', 'EOF')
                self._line_number += 1
                self._character_position = 0

                self._line = self._line.rstrip()
                self._line = re.sub(r'^\s*//.*', '', self._line, 1)
            length = len(self._line)
            self._line = self._line.lstrip()
            self._character_position += length - len(self._line)
            for rex in self.regexes.keys():
                length = len(self._line)
                match = re.match(rex, self._line)
                if match:
                    self._line = re.sub(rex, '', self._line, 1).strip()
                    self._character_position += length - len(self._line)
                    self._line = re.sub(r'^//.*', '', self._line, 1)
                    text = match.group(1)
                    if self.regexes[rex] == 'ID':
                        if text in self.reserved:
                            return self.new_token(self.reserved[text], text)
                        else:
                            return self.new_token('ID', text)
                    else:
                        return self.new_token(self.regexes[rex], text)
            for literal in self.literals:
                if self._line.startswith(literal):
                    self._line = self._line[len(literal):].lstrip()
                    self._line = re.sub(r'^//.*', '', self._line, 1)
                    return self.new_token(literal, literal)
            return self.new_token('ERROR', self._line)

    def new_token(self, name, value=''):
        return Token(self._line_number, self._character_position, name, value)

    def __str__(self) -> str:
        return "<tokens: " + str(self._tokens) + ' remaining: "' + self._line + '">'

    __repr__ = __str__


class Reader:
    """
        top : expression ';'
            | definition ';'
            | construct
            | EOF

        construct : IF '(' expression ')' nest ELSE nest
                  | FN symbol formals body
                  | FN symbol composite_body
                  | typedef
                  | ENV symbol body
                  | nest

        nest : body

        body : '{' statements '}'

        composite_body : '{' sub_functions '}'

        sub_functions : sub_function { sub_function }

        sub_function : sub_function_arguments body

        sub_function_arguments : '(' sub_function_arg_list ')'

        sub_function_arg_list : sub_function_arg [ ',' sub_function_arg_list ]

        sub_function_arg : symbol [ '(' sub_function_arg_list ')' ]
                         | number
                         | string
                         | char
                         | boolean

        statements : expression
                   | expression ';' statements
                   | definition
                   | definition ';' statements
                   | construct
                   | construct statements

        expression : binop_and THEN expression
                   | binop_and

        definition : DEFINE symbol '=' expression

        binop_and : unop_not { AND binop_and }
                  | unop_not { OR binop_and }
                  | unop_not { XOR binop_and }
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

        binop_add : binop_mul { '+' binop_mul }
                  | binop_mul { '-' binop_mul }
                  | binop_mul

        binop_mul : op_funcall { '*' op_funcall }
                  | op_funcall { '/' op_funcall }
                  | op_funcall { '%' op_funcall }
                  | op_funcall

        op_funcall : env_access [ '(' actuals ')' ]
                   | env_access

        env_access : atom { '.' env_access }
                   | atom

        atom : symbol
             | number
             | string
             | char
             | boolean
             | NOTHING
             | lst
             | FN formals body
             | FN composite_body
             | ENV body
             | BACK
             | '(' expression ')'

        formals : '(' fargs ')'

        fargs : empty
              | farg { ',' fargs }

        farg : symbol [ ':' symbol ]

        symbols : empty
                | symbol { ',' symbols }

        typedef : TYPEDEF flat_type '{' type_body '}'

        flat_type : symbol [ '(' symbols ')' ]

        type_body : type_constructor { '|' type_body }

        type_constructor : symbol [ '(' nested_types ')' ]

        nested_types : nested_type { ',' nested_type }

        nested_type : symbol [ '(' nested_types ')' ]

    """

    def __init__(self, tokeniser: Tokeniser, stderr: io.StringIO):
        self.tokeniser = tokeniser
        self.stderr = stderr
        self.depth = 0

    def read(self) -> expr.Expr:
        if Config.debugging:
            self.depth = len(inspect.stack())
        self.debug("*******************************************************")
        result = self.top()
        self.debug("read", result=result)
        return result

    def top(self, fail=True) -> Maybe[expr.Expr]:
        """
            statement : definition ';'
                      | construct
                      | expression ';'
                      | EOF
        """
        self.debug("top", fail=fail)
        if self.swallow('EOF'):
            return None

        definition = self.definition(False)
        if definition is not None:
            self.consume(';')
            return definition

        construct = self.construct(False)
        if construct is not None:
            return construct

        expression = self.expression(fail)
        if expression is not None:
            self.consume(';')
        return expression

    def construct(self, fail=True):
        """
            construct : IF '(' expression ')' nest ELSE nest
                      | FN symbol '(' formals ')' body
                      | FN symbol composite_body
                      | typedef
                      | ENV symbol body
                      | nest
        """
        self.debug("construct", fail=fail)
        if self.swallow('IF'):
            self.consume('(')
            test = self.expression()
            self.consume(')')
            consequent = self.nest()
            self.consume('ELSE')
            alternative = self.nest()
            return expr.Conditional(test, consequent, alternative)

        fn = self.swallow('FN')
        if fn is not None:
            symbol = self.symbol(False)
            if symbol is None:
                self.pushback(fn)
                return None
            else:
                formals = self.formals(False)
                if formals is None:
                    composite_body = self.composite_body()
                    return expr.Definition(symbol, composite_body)
                else:
                    body = self.body()
                    return expr.Definition(symbol, expr.Lambda(formals, body))

        typedef = self.typedef(False)
        if typedef is not None:
            return typedef

        env = self.swallow('ENV')
        if env is not None:
            symbol = self.symbol(False)
            if symbol is None:
                self.pushback(env)
                return None
            else:
                body = self.body()
                return expr.Definition(symbol, expr.Env(body))

        return self.nest(fail)

    def nest(self, fail=True):
        self.debug("nest", fail=fail)
        body = self.body(fail)
        if body is None:
            return None
        return expr.Nest(body)

    def body(self, fail=True):
        """
            body : '{' statements '}'
        """
        self.debug("body", fail=fail)
        if self.swallow('{'):
            statements = self.statements()
            self.consume('}')
            return expr.Sequence(statements)
        else:
            if fail:
                self.error("expected '{'")
            else:
                return None

    def composite_body(self) -> expr.Composite:
        """
        composite_body : '{' sub_functions '}'
        """
        self.consume('{')
        sub_functions = self.sub_functions()
        self.consume('}')
        return expr.Composite(sub_functions)

    def sub_functions(self) -> expr.List:
        """
        sub_functions : sub_function { sub_function }
        """
        sub_function = self.sub_function(False)
        if sub_function is None:
            return expr.Null()
        else:
            return expr.Pair(sub_function, self.sub_functions())

    def sub_function(self, fail=True) -> Maybe[expr.CompositeComponent]:
        """
        sub_function : '(' sub_function_arguments ')' body
        """
        sub_function_arguments = self.sub_function_arguments(fail)
        if sub_function_arguments is None:
            return None
        else:
            body = self.body()
            return expr.CompositeComponent(sub_function_arguments, body)

    def sub_function_arguments(self, fail=True) -> Maybe[expr.List]:
        """
        sub_function_arguments : '(' sub_function_arg_list ')'

        """
        if self.swallow('('):
            sub_function_arg_list = self.sub_function_arg_list()
            self.consume(')')
            return sub_function_arg_list
        else:
            if fail:
                self.error("expected '('")
            else:
                return None

    def sub_function_arg_list(self, fail=True) -> expr.List:
        """
        sub_function_arg_list : sub_function_arg [ ',' sub_function_arg_list ]
        """
        sub_function_arg = self.sub_function_arg(fail)
        if sub_function_arg is None:
            return expr.Null()
        if self.swallow(','):
            return expr.Pair(sub_function_arg, self.sub_function_arg_list())
        else:
            return expr.Pair(sub_function_arg, expr.Null())

    def sub_function_arg(self, fail=True):
        number = self.number(False)
        if number is not None:
            return number

        string = self.string(False)
        if string is not None:
            return string

        char = self.char(False)
        if char is not None:
            return char

        boolean = self.boolean(False)
        if boolean is not None:
            return boolean

        symbol = self.symbol(False)
        if symbol is not None:
            arg_list = self.sub_function_arguments(False)
            if arg_list is None:
                return symbol
            else:
                return expr.CompositeArgument(symbol, arg_list)

        if fail:
            self.error("expecting symbol, constant or type constructor")
        else:
            return None

    def statements(self) -> expr.List:
        """
            statements : expression
                       | expression ';' statements
                       | definition
                       | definition ';' statements
                       | construct
                       | construct statements
        """
        self.debug("statements")
        definition = self.definition(False)
        if definition is not None:
            if self.swallow(';'):
                return expr.Pair(definition, self.statements())
            else:
                return expr.Pair(definition, expr.Null())

        construct = self.construct(False)
        if construct is not None:
            return expr.Pair(construct, self.statements())

        expression = self.expression(False)
        if expression is not None:
            if self.swallow(';'):
                return expr.Pair(expression, self.statements())
            else:
                return expr.Pair(expression, expr.Null())

        return expr.Null()

    def definition(self, fail=True):
        """
            definition : DEFINE symbol '=' expression
        """
        self.debug("definition", fail=fail)
        if self.swallow('DEFINE'):
            symbol = self.symbol()
            self.consume('=')
            expression = self.expression()
            return expr.Definition(symbol, expression)
        else:
            if fail:
                self.error("expected 'define'")
            else:
                return None

    def expression(self, fail=True) -> Maybe[expr.Expr]:
        """
            expression : binop_and THEN expression
                   | binop_and
        """
        self.debug("expression", fail=fail)
        return self.rassoc_binop(self.binop_and, ['THEN'], self.expression, fail)

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
            binop_mul : binop_pow {'*' binop_pow}
                   | binop_pow {'/' binop_pow}
                   | binop_pow {'%' binop_pow}
                   | binop_pow
        """
        self.debug("binop_mul", fail=fail)
        return self.lassoc_binop(self.binop_pow, ['*', '/', '%'], fail)

    def binop_pow(self, fail=True) -> Maybe[expr.Expr]:
        """
            binop_pow : op_funcall '**' binop_pow
                      | op_funcall
        """
        self.debug("binop_pow")
        return self.rassoc_binop(self.op_funcall, ['**'], self.binop_pow, fail)

    def op_funcall(self, fail=True) -> Maybe[expr.Expr]:
        """
            op_funcall : env_access ['(' actuals ')']
                       | env_access
        """
        self.debug("op_funcall", fail=fail)
        env_access = self.env_access(fail)
        if env_access is None:
            return None
        while True:
            if self.swallow('('):
                actuals = self.exprs()
                self.consume(')')
                env_access = expr.Application(env_access, actuals)
            else:
                return env_access

    def env_access(self, fail=True):
        """
             env_access : atom {'.' env_access}
                        | atom
        """
        self.debug("env_access", fail=fail)

        lhs = self.atom(fail)
        if lhs is None:
            return None
        while True:
            op = self.swallow('.')
            if op:
                rhs = self.atom()
                lhs = expr.EnvContext(lhs, rhs)
            else:
                return lhs

    def atom(self, fail=True) -> Maybe[expr.Expr]:
        """
            atom : symbol
                   | number
                   | string
                   | char
                   | boolean
                   | NOTHING
                   | lst
                   | FN formals body
                   | FN composite_body
                   | ENV body
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

        if self.swallow('NOTHING'):
            return expr.Nothing()

        lst = self.lst(False)
        if lst is not None:
            return lst

        if self.swallow('FN'):
            formals = self.formals(False)
            if formals is None:
                return self.composite_body()
            else:
                body = self.body()
                return expr.Lambda(formals, body)

        if self.swallow('ENV'):
            body = self.body()
            return expr.Env(body)

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

    def formals(self, fail=True) -> Maybe[expr.List]:
        self.debug("formals")
        if self.swallow('('):
            symbols = self.fargs()
            self.consume(')')
            return symbols
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
            return expr.Number(int(number.value))
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
            return expr.String(string.value)
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

    def fargs(self) -> expr.List:
        """
            fargs : empty
            fargs : farg [ ',' nfargs ]
        """
        self.debug("fargs")
        farg = self.farg(False)
        if farg is None:
            return expr.Null()
        if self.swallow(','):
            fargs = self.fargs()
            return expr.Pair(farg, fargs)
        else:
            return expr.List.list([farg])

    def farg(self, fail=True):
        """
        farg : symbol [ ':' symbol ]
        """
        self.debug("farg")
        symbol = self.symbol(fail)
        if symbol is None:
            return None
        if self.swallow(':'):
            f_type = self.symbol()
            return expr.TypedSymbol(symbol, f_type)
        else:
            return symbol

    def exprs(self) -> expr.List:
        """
            exprs : empty
                  | expression { ',' exprs }
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

    def symbols(self):
        symbol = self.symbol()
        if self.swallow(','):
            return expr.Pair(symbol, self.symbols())
        else:
            return expr.Pair(symbol, expr.Null())

    def typedef(self, fail=True) -> Maybe[expr.TypeDef]:
        """
        typedef : TYPEDEF flat_type '{' type_body '}'
        """
        if self.swallow('TYPEDEF'):
            flat_type = self.flat_type()
            self.consume('{')
            type_body = self.type_body()
            self.consume('}')
            return expr.TypeDef(flat_type, type_body)
        if fail:
            self.error("expected typedef")
        else:
            return None

    def flat_type(self) -> expr.FlatType:
        """
        flat_type :  symbol [ '(' symbols ')' ]
        """
        symbol = self.symbol()
        if self.swallow('('):
            symbols = self.symbols()
            self.consume(')')
            return expr.FlatType(symbol, symbols)
        else:
            return expr.FlatType(symbol, expr.Null())

    def type_body(self) -> expr.List:
        """
        type_body : type_constructor { '|' type_body }
        """
        type_constructor = self.type_constructor()
        if self.swallow('|'):
            return expr.Pair(type_constructor, self.type_body())
        else:
            return expr.Pair(type_constructor, expr.Null())

    def type_constructor(self) -> expr.TypeConstructor:
        """
        type_constructor :  symbol [ '(' nested_types ')' ]
        """
        symbol = self.symbol()
        if self.swallow('('):
            nested_types = self.nested_types()
            self.swallow(')')
        else:
            nested_types = expr.Null()

        return expr.TypeConstructor(symbol, nested_types)

    def nested_types(self) -> expr.List:
        """
        nested_types : nested_type { ',' nested_types }
        """
        nested_type = self.nested_type()
        if self.swallow(","):
            return expr.Pair(nested_type, self.nested_types())
        else:
            return expr.Pair(nested_type, expr.Null())

    def nested_type(self) -> expr.Type:
        """
        nested_type : symbol [ '(' nested_types ')' ]
        """
        symbol = self.symbol()
        if self.swallow('('):
            result = expr.Type(symbol, self.nested_types())
            self.consume(')')
            return result
        else:
            return expr.Type(symbol, expr.Null())

    # utils

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
        """
        self.debug("swallow", args=args, caller=inspect.stack()[1][3])
        for token_type in args:
            token = self.tokeniser.match(token_type)
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
            if self.tokeniser.match(name) is None:
                self.error("expected " + name)

    def pushback(self, token: Token):
        self.tokeniser.pushback(token)

    def error(self, msg):
        raise PySchemeSyntaxError(
            msg,
            line=self.tokeniser.line_number(),
            next_token=self.tokeniser.peek().value
        )

    def debug(self, *args, **kwargs):
        if Config.debugging:
            depth = len(inspect.stack()) - self.depth
            print('   |' * (depth // 4), end='')
            print(' ' * (depth % 4), end='')
            for arg in args:
                print(arg, end=' ')
            for k in kwargs:
                print(k + '=' + str(kwargs[k]), end=' ')
            print(self.tokeniser)
