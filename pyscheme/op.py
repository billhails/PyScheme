from functools import reduce
from typing import Callable

class Op:
    def apply(self, args, ret: Callable):
        pass


class Closure(Op):
    def __init__(self, args, body, env):
        self._args = args
        self._body = body
        self._env = env

    def apply(self, args, ret: Callable):
        return lambda: self._body.eval(self._env.extend(dict(zip(self._args, args))), ret)


class Primitive(Op):
    pass


class Addition(Primitive):
    def apply(self, args, ret: Callable):
        import pyscheme.expr as expr
        return lambda: ret(expr.Constant(reduce(lambda x, y: x.value() + y.value(), args)))


class Equality(Primitive):
    def apply(self, args, ret: Callable):
        return lambda: ret(args.car().eq(args.cdr().car()))
