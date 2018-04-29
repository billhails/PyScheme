import pyscheme.op
import pyscheme.environment as environment
import pyscheme.list as list
from typing import Callable
from pyscheme.exceptions import NonBooleanExpressionError

class Expr:
    def eval(self, env: environment.Environment, ret: Callable):
        pass

    def is_true(self):
        raise NonBooleanExpressionError()


class Constant(Expr):
    def __init__(self, value):
        self._value = value

    def eval(self, env: environment.Environment, ret: Callable):
        return lambda: ret(self)

    def __str__(self):
        return "Constant(" + str(self._value) + ")"

    __repr__ = __str__


class Boolean(Expr):
    _true = None
    _false = None
    _unknown = None

    @classmethod
    def true(cls):
        if cls._true is None:
            cls._true = T()
        return cls._true

    @classmethod
    def false(cls):
        if cls._false is None:
            cls._false = F()
        return cls._false

    @classmethod
    def unknown(cls):
        if cls._unknown is None:
            cls._unknown = U()
        return cls._unknown

    def __and__(self, other):
        pass

    def __or__(self, other):
        pass

    def __invert__(self):
        pass

    def __xor__(self, other):
        return (self & ~other) | (other & ~self)

    def is_true(self):
        return self == Boolean.true()


class T(Boolean):
    def __and__(self, other: Boolean):
        return other

    def __or__(self, other: Boolean):
        return self

    def __invert__(self):
        return Boolean.false()


class F(Boolean):
    def __and__(self, other: Boolean):
        return self

    def __or__(self, other: Boolean):
        return other

    def __invert__(self):
        return Boolean.true()


class U(Boolean):
    def __and__(self, other):
        if other == Boolean.false():
            return other
        else:
            return self

    def __or__(self, other):
        if other == Boolean.true():
            return other
        else:
            return self

    def __invert__(self):
        return self


class Symbol(Expr):
    symbols = {}

    @classmethod
    def make(cls, name) -> Expr:
        if name not in cls.symbols.keys():
            cls.symbols[name] = Symbol(name)
        return cls.symbols[name]

    def __init__(self, name):
        self._name = name

    def eval(self, env: environment.Environment, ret: Callable):
        return lambda: env.lookup(self, ret)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return id(self) == id(other)

    def __str__(self):
        return "Symbol(" + str(self._name) + ")"

    __repr__ = __str__


class Conditional(Expr):
    def __init__(self, test: Expr, consequent: Expr, alternative: Expr):
        self._test = test
        self._consequent = consequent
        self._alternative = alternative

    def eval(self, env: environment.Environment, ret: Callable):
        def deferred(result: Expr):
            if result.is_true():
                return lambda: self._consequent.eval(env, ret)
            else:
                return lambda: self._consequent.eval(env, ret)
        return lambda: self._test.eval(env, deferred)

    def __str__(self):
        return "Conditional(if (" + str(self._test) + \
               ") {" + str(self._consequent) + \
               "} else {" + str(self._alternative) + "})"

    __repr__ = __str__


class Lambda(Expr):
    def __init__(self, args: list.List, body: Expr):
        self._args = args
        self._body = body

    def eval(self, env: environment.Environment, ret: Callable):
        return lambda: ret(pyscheme.op.Closure(self._args, self._body, env))

    def __str__(self):
        return "Lambda(" + str(self._args) + "{" + str(self._body) + "})"

    __repr__ = __str__


class Application(Expr):
    def __init__(self, operation: Expr, operands: list.List):
        self._operation = operation
        self._operands = operands

    def eval(self, env: environment.Environment, ret: Callable):
        def deferred_op(evaluated_op):
            def deferred_args(evaluated_args):
                return lambda: evaluated_op.apply(evaluated_args, ret)
            return lambda: self._operands.map_eval(env, deferred_args)
        return self._operation.eval(env, deferred_op)

    def __str__(self):
        return "Application(" + str(self._operation) + ": " + str(self._operands) + ")"
