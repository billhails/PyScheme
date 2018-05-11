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
from pyscheme import types
import pyscheme.environment as environment
import pyscheme.expr as expr
from io import StringIO
import pyscheme.reader as reader

class Repl:
    def __init__(self, input: StringIO, output: StringIO, error: StringIO):
        self.input = input
        self.output = output
        self.tokeniser = reader.Tokeniser(input)
        self.reader = reader.Reader(self.tokeniser, error)
        self.env = environment.Environment().extend(
            { expr.Symbol(k): v for k, v in
                {
                    "+": expr.Addition(),
                    "-": expr.Subtraction(),
                    "*": expr.Multiplication(),
                    "/": expr.Division(),
                    "%": expr.Modulus(),
                    "==": expr.Equality(),
                    "<": expr.LT(),
                    ">": expr.GT(),
                    "<=": expr.LE(),
                    ">=": expr.GE(),
                    "!=": expr.NE(),
                    "and": expr.And(),
                    "or": expr.Or(),
                    "not": expr.Not(),
                    "xor": expr.Xor(),
                    "@": expr.Cons(),
                    "@@": expr.Append(),
                    "binop_then": expr.Then(),
                    "back": expr.Back(),
                    "then": expr.Then(),
                    "head": expr.Head(),
                    "tail": expr.Tail(),
                    "define": expr.Define(),
                    "length": expr.Length(),
                    "print": expr.Print(self.output),
                    "here": expr.CallCC(),
                    "exit": expr.Exit(),
                    "error": expr.Error(lambda val, amb: lambda: self.repl(lambda: None))
                }.items()
            }
        )

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

