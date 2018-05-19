# PyScheme lambda language written in Python
#
# The Read-Eval-Print-Loop
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

from typing import List
from . import types
import pyscheme.environment as environment
import pyscheme.expr as expr
from io import StringIO
import pyscheme.reader as reader
from .inference import TypeEnvironment
from .exceptions import PySchemeError

class Repl:
    def __init__(self, input: StringIO, output: StringIO, error: StringIO):
        self.input = input
        self.output = output
        self.error = error
        self.tokeniser = reader.Tokeniser(input)
        self.reader = reader.Reader(self.tokeniser, error)
        operators = {
                    "+": expr.Addition(),             # int -> int -> int
                    "-": expr.Subtraction(),          # int -> int -> int
                    "*": expr.Multiplication(),       # int -> int -> int
                    "/": expr.Division(),             # int -> int -> int
                    "%": expr.Modulus(),              # int -> int -> int
                    "==": expr.Equality(),            # a -> a -> bool
                    "<": expr.LT(),                   # a -> a -> bool
                    ">": expr.GT(),                   # a -> a -> bool
                    "<=": expr.LE(),                  # a -> a -> bool
                    ">=": expr.GE(),                  # a -> a -> bool
                    "!=": expr.NE(),                  # a -> a -> bool
                    "and": expr.And(),                # bool -> bool -> bool
                    "or": expr.Or(),                  # bool -> bool -> bool
                    "not": expr.Not(),                # bool -> bool
                    "xor": expr.Xor(),                # bool -> bool -> bool
                    "@": expr.Cons(),                 # a -> list(a) -> list(a)
                    "@@": expr.Append(),              # list(a) -> list(a) -> list(a)
                    "back": expr.Back(),              # _
                    "then": expr.Then(),              # a -> a -> a
                    "head": expr.Head(),              # list(a) -> a
                    "tail": expr.Tail(),              # list(a) -> list(a)
                    "length": expr.Length(),          # list(a) -> int
                    "print": expr.Print(self.output), # a -> a
                    "here": expr.CallCC(),            # ((a -> _) -> a) -> a ?
                    "exit": expr.Exit(),              # _
                    "error": expr.Error(
                        lambda val, amb:
                        lambda: self.repl(lambda:
                                          None))      # _
                }
        self.env = environment.Environment().extend(
            { expr.Symbol(k): v for k, v in operators.items() }
        )

        self.type_env = TypeEnvironment().extend()

        for k, v in operators.items():
            if v.static_type():
                self.type_env[expr.Symbol(k)] = v.type()

    def trampoline(self, threads: List['types.Promise']):
        while len(threads) > 0:
            thunk = threads.pop(0)
            next = thunk()
            if next is not None:
                threads += [next]

    def read(self, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        result = self.reader.read()
        if result is None:
            return None  # stop the trampoline
        try:
            result.analyse(self.type_env)
        except PySchemeError as e:
            self.error.write(' '.join(e.args))
            return None
        return lambda: ret(result, amb)

    def eval(self, expr: expr.Expr, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: expr.eval(self.env, ret, amb)

    def print(self, expr: expr.Expr, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        if expr is not None:
            self.output.write(str(expr) + "\n")
        return lambda: ret(expr, amb)

    def repl(self, amb: 'types.Amb') -> 'types.Promise':
        def print_continuation(expr, amb: 'types.Amb') -> 'types.Promise':
            return lambda: self.repl(lambda: None)

        def eval_continuation(evaluated_expr: expr.Expr, amb: 'types.Amb') -> 'types.Promise':
            return lambda: self.print(evaluated_expr, print_continuation, amb)

        def read_continuation(read_expr: expr.Expr, amb: 'types.Amb') -> 'types.Promise':
            return lambda: self.eval(read_expr, eval_continuation, amb)

        return lambda: self.read(read_continuation, amb)

    def run(self):
        self.trampoline([lambda: self.repl(lambda: None)])

