import pyscheme.expr
from functools import reduce
import pyscheme.list as list
from typing import Callable

class Op:
    def apply(self, args, ret: Callable):
        pass


class Closure(Op):
    def __init__(self, args: list.List, body, env):
        self._args = args
        self._body = body
        self._env = env

    def apply(self, args: list.List, ret: Callable):
        return lambda: self._body.eval(self._env.extend(dict(zip(self._args, args))), ret)


class Primitive(Op):
    pass


class Addition(Primitive):
    def apply(self, args, ret: Callable):
        return lambda: ret(pyscheme.expr.Constant(reduce(lambda x, y: x._value + y._value, args)))