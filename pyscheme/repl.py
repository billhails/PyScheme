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
import pyscheme.environment as environment
import pyscheme.expr as expr
import pyscheme.op as op
from typing import Callable
from io import FileIO
import pyscheme.reader as reader

class Repl:
    def __init__(self, input: FileIO, output: FileIO, error: FileIO):
        self.input = input
        self.output = output
        self.tokeniser = reader.Tokeniser(input)
        self.reader = reader.Reader(self.tokeniser, error)
        self.env = environment.Environment().extend(
            {
                expr.Symbol("+"): op.Addition(),
                expr.Symbol("-"): op.Subtraction(),
                expr.Symbol("*"): op.Multiplication(),
                expr.Symbol("/"): op.Division(),
                expr.Symbol("%"): op.Modulus(),
                expr.Symbol("=="): op.Equality(),
                expr.Symbol("<"): op.LT(),
                expr.Symbol(">"): op.GT(),
                expr.Symbol("<="): op.LE(),
                expr.Symbol(">="): op.GE(),
                expr.Symbol("!="): op.NE(),
                expr.Symbol("and"): op.And(),
                expr.Symbol("or"): op.Or(),
                expr.Symbol("not"): op.Not(),
                expr.Symbol("xor"): op.Xor(),
                expr.Symbol("@"): op.Cons(),
                expr.Symbol("@@"): op.Append(),
                expr.Symbol("binop_then"): op.Then(),
                expr.Symbol("back"): op.Back(),
                expr.Symbol("head"): op.Head(),
                expr.Symbol("tail"): op.Tail(),
                expr.Symbol("define"): op.Define(),
                expr.Symbol("length"): op.Length(),
                expr.Symbol("print"): op.Print(self.output),
                expr.Symbol("here"): op.CallCC(),
                expr.Symbol("exit"): op.Exit(),
                expr.Symbol("error"): op.Error(lambda val, amb: lambda: self.repl(lambda: None))
            }
        )

    def trampoline(self, threads: List):
        while len(threads) > 0:
            thunk = threads.pop(0)
            next = thunk()
            if next is not None:
                threads += [next]

    def read(self, ret: Callable, amb: Callable):
        result = self.reader.read()
        if result is None:
            return None  # stop the trampoline
        return lambda: ret(result, amb)

    def eval(self, expr: expr.Expr, ret: Callable, amb: Callable):
        return lambda: expr.eval(self.env, ret, amb)

    def print(self, expr: expr.Expr, ret: Callable, amb: Callable):
        self.output.write(str(expr))
        return lambda: ret(expr, amb)

    def repl(self, amb: Callable):
        def deferred_repl(expr, amb: Callable):
            return lambda: self.repl(lambda: None)

        def deferred_print(evaluated_expr: expr.Expr, amb: Callable):
            return lambda: self.print(evaluated_expr, deferred_repl, amb)

        def deferred_eval(read_expr: expr.Expr, amb: Callable):
            return lambda: self.eval(read_expr, deferred_print, amb)

        return lambda: self.read(deferred_eval, amb)

    def run(self):
        self.trampoline([lambda: self.repl(lambda: None)])


if __name__ == "__main__":
    Repl().run()
