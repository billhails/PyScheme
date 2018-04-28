from typing import List
import pyscheme.yacc as yacc
import pyscheme.lex as lex
import pyscheme.environment as environment
import pyscheme.expr as expr
import pyscheme.op as op
from typing import Callable


class Repl:
    def __init__(self):
        self.env = environment.Environment().extend({expr.Symbol.make("+"): op.Addition()})

    def trampoline(self, threads: List):
        while len(threads) > 0:
            thunk = threads.pop(0)
            next = thunk()
            if next is not None:
                threads += [next]

    def read(self, ret: Callable):
        try:
            s = input("F♮> ")
        except EOFError:
            return None
        result = yacc.parser.parse(s, lexer=lex.lexer)
        if result is None:
            return None
        return lambda: ret(result)

    def eval(self, expr: expr.Expr, ret: Callable):
        return lambda: expr.eval(self.env, ret)

    def print(self, expr: expr.Expr, ret: Callable):
        print(expr)
        return lambda: ret(expr)

    def repl(self):
        def deferred_eval(read_expr: expr.Expr):
            def deferred_print(evaluated_expr: expr.Expr):
                def deferred_repl(expr):
                    return lambda: self.repl()
                return lambda: self.print(evaluated_expr, deferred_repl)
            return lambda: self.eval(read_expr, deferred_print)
        return lambda: self.read(deferred_eval)

    def run(self):
        self.trampoline([lambda: self.repl()])


if __name__ == "__main__":
    Repl().run()
