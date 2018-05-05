from typing import List
import pyscheme.yacc as yacc
import pyscheme.lex as lex
import pyscheme.environment as environment
import pyscheme.expr as expr
import pyscheme.op as op
from typing import Callable
from pyscheme.stream import Stream


class Repl:
    def __init__(self, input: Stream, output):
        self.input = input
        self.output = output
        self.lexer = lex.Lexer(input)
        self.env = environment.Environment().extend(
            {
                expr.Symbol("+"): op.Addition(),
                expr.Symbol("-"): op.Subtraction(),
                expr.Symbol("*"): op.Multiplication(),
                expr.Symbol("/"): op.Division(),
                expr.Symbol("%"): op.Modulus(),
                expr.Symbol("=="): op.Equality(),
                expr.Symbol("and"): op.And(),
                expr.Symbol("or"): op.Or(),
                expr.Symbol("not"): op.Not(),
                expr.Symbol("xor"): op.Xor(),
                expr.Symbol("@"): op.Cons(),
                expr.Symbol("@@"): op.Append(),
                expr.Symbol("then"): op.Then(),
                expr.Symbol("fail"): op.Fail(),
                expr.Symbol("head"): op.Head(),
                expr.Symbol("tail"): op.Tail(),
                expr.Symbol("define"): op.Define(),
                expr.Symbol("length"): op.Length(),
            }
        )

    def trampoline(self, threads: List):
        while len(threads) > 0:
            thunk = threads.pop(0)
            next = thunk()
            if next is not None:
                threads += [next]

    def read(self, ret: Callable, amb: Callable):
        result = yacc.parser.parse(lexer=self.lexer)
        if result is None:
            return None  # stop the trampoline
        return lambda: ret(result, amb)

    def eval(self, expr: expr.Expr, ret: Callable, amb: Callable):
        return lambda: expr.eval(self.env, ret, amb)

    def print(self, expr: expr.Expr, ret: Callable, amb: Callable):
        self.output.write(str(expr))
        return lambda: ret(expr, amb)

    def repl(self, amb: Callable):
        def deferred_eval(read_expr: expr.Expr, amb: Callable):
            def deferred_print(evaluated_expr: expr.Expr, amb: Callable):
                def deferred_repl(expr, amb: Callable):
                    return lambda: self.repl(lambda: None)
                return lambda: self.print(evaluated_expr, deferred_repl, amb)
            return lambda: self.eval(read_expr, deferred_print, amb)
        return lambda: self.read(deferred_eval, amb)

    def run(self):
        self.trampoline([lambda: self.repl(lambda: None)])


if __name__ == "__main__":
    Repl().run()
