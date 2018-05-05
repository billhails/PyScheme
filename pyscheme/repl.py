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
                expr.Symbol.make("+"): op.Addition(),
                expr.Symbol.make("-"): op.Subtraction(),
                expr.Symbol.make("*"): op.Multiplication(),
                expr.Symbol.make("/"): op.Division(),
                expr.Symbol.make("%"): op.Modulus(),
                expr.Symbol.make("=="): op.Equality(),
                expr.Symbol.make("and"): op.And(),
                expr.Symbol.make("or"): op.Or(),
                expr.Symbol.make("not"): op.Not(),
                expr.Symbol.make("xor"): op.Xor(),
                expr.Symbol.make("@"): op.Cons(),
                expr.Symbol.make("@@"): op.Append(),
                expr.Symbol.make("then"): op.Then(),
                expr.Symbol.make("fail"): op.Fail(),
                expr.Symbol.make("head"): op.Head(),
                expr.Symbol.make("tail"): op.Tail(),
                expr.Symbol.make("define"): op.Define(),
                expr.Symbol.make("length"): op.Length(),
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
