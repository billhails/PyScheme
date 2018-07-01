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
from .inference import TypeEnvironment, EnvironmentType
from .exceptions import PySchemeError
from . import ambivalence
from pyscheme.ir.environment import Environment as CompileTimeEnvironment


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
                    "**": expr.Exponentiation(),      # int -> int -> int
                    "==": expr.Equality(),            # t -> t -> bool
                    "<": expr.LT(),                   # t -> t -> bool
                    ">": expr.GT(),                   # t -> t -> bool
                    "<=": expr.LE(),                  # t -> t -> bool
                    ">=": expr.GE(),                  # t -> t -> bool
                    "!=": expr.NE(),                  # t -> t -> bool
                    "and": expr.And(),                # bool -> bool -> bool
                    "or": expr.Or(),                  # bool -> bool -> bool
                    "not": expr.Not(),                # bool -> bool
                    "xor": expr.Xor(),                # bool -> bool -> bool
                    "@": expr.Cons(),                 # t -> list(t) -> list(t)
                    "@@": expr.Append(),              # list(t) -> list(t) -> list(t)
                    "back": expr.Back(),              # _
                    "then": expr.Then(),              # t -> t -> t
                    "head": expr.Head(),              # list(t) -> t
                    "tail": expr.Tail(),              # list(t) -> list(t)
                    "length": expr.Length(),          # list(t) -> int
                    "print": expr.Print(self.output), # t -> t
                    "here": expr.CallCC(),            # ((t -> _) -> t) -> a ?
                    "exit": expr.Exit(),              # _
                    "spawn": expr.Spawn(),            # bool
                    "error": expr.Error(
                        lambda val, amb:
                            lambda: self.repl(ambivalence.Amb(lambda: None))) # _
                }
        self.env = environment.Environment().extend(
            { expr.Symbol(k): v for k, v in operators.items() }
        )

        globalenv = expr.Symbol("globalenv")
        self.env.non_eval_context_define(globalenv, expr.EnvironmentWrapper(self.env))

        self.type_env = TypeEnvironment().extend()

        for k, v in operators.items():
            if v.static_type():
                self.type_env[expr.Symbol(k)] = v.type()

        self.type_env[globalenv] = EnvironmentType(self.type_env)

        self.compile_time_env = CompileTimeEnvironment().extend({expr.Symbol(k): v for k, v in operators.items()})
        self.compile_time_env.install(globalenv, self.env[globalenv])


    def trampoline(self, threads: List['types.Promise']):
        while len(threads) > 0:
            thunk = threads.pop(0)
            next = thunk()
            if next is not None:
                if type(next) is list:  # spawn returns a list of two threads
                    threads += next
                else:
                    threads += [next]

    def read(self, ret: 'types.Continuation', amb: ambivalence.Amb) -> 'types.Promise':
        result = self.reader.read()
        if result is None:
            return None  # stop the trampoline
        return lambda: ret(result, amb)

    def analyze(self, expr: expr.Expr, ret: 'types.Continuation', amb: ambivalence.Amb) -> 'types.Promise':
        try:
            expr.analyse(self.type_env)
        except PySchemeError as e:
            self.error.write(str(e))
            return None
        return lambda: ret(expr, amb)

    def eval(self, expr: expr.Expr, ret: 'types.Continuation', amb: ambivalence.Amb) -> 'types.Promise':
        return lambda: expr.eval(self.env, ret, amb)

    def print(self, exp: expr.Expr, ret: 'types.Continuation', amb: ambivalence.Amb) -> 'types.Promise':
        if type(exp) is not expr.Nothing:
            self.output.write(str(exp) + "\n")
        return lambda: ret(exp, amb)

    def repl(self, amb: ambivalence.Amb) -> 'types.Promise':
        def print_continuation(expr, amb: ambivalence.Amb) -> 'types.Promise':
            return lambda: self.repl(ambivalence.Amb(lambda: None))

        def eval_continuation(evaluated_expr: expr.Expr, amb: ambivalence.Amb) -> 'types.Promise':
            return lambda: self.print(evaluated_expr, print_continuation, amb)

        def analyze_continuation(analyzed_expr: expr.Expr, amb: ambivalence.Amb) -> 'types.Promise':
            return lambda: self.eval(analyzed_expr, eval_continuation, amb)

        def read_continuation(read_expr: expr.Expr, amb: ambivalence.Amb) -> 'types.Promise':
            return lambda: self.analyze(read_expr, analyze_continuation, amb)

        return lambda: self.read(read_continuation, amb)

    def run(self):
        self.trampoline([lambda: self.repl(ambivalence.Amb(lambda: None))])

