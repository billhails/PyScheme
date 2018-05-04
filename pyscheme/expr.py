import pyscheme.op as op
import pyscheme.environment as environment
from typing import Callable
from pyscheme.exceptions import NonBooleanExpressionError


class Expr:
    def eval(self, env: environment.Environment, ret: Callable):
        pass

    def is_true(self):
        raise NonBooleanExpressionError()

    def is_false(self):
        raise NonBooleanExpressionError()

    def is_unknown(self):
        raise NonBooleanExpressionError()

    def __eq__(self, other):
        return id(self) == id(other)

    def eq(self, other):
        if self == other:
            return Boolean.true()
        else:
            return Boolean.false()

    def is_null(self):
        return False


class List(Expr):
    pass


class Constant(Expr):
    def __init__(self, value):
        self._value = value

    def eval(self, env: environment.Environment, ret: Callable):
        return lambda: ret(self)

    def value(self):
        return self._value

    def __eq__(self, other: Expr):
        if other.__class__ == Constant:
            return self._value == other.value()
        else:
            return False

    def __str__(self):
        return str(self._value)

    __repr__ = __str__


class Boolean(Constant):
    _true = None
    _false = None
    _unknown = None

    def __init__(self):
        pass

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

    def __eq__(self, other):
        return id(self) == id(other)

    def is_true(self):
        return False

    def is_true(self):
        return False

    def is_false(self):
        return False

    def is_unknown(self):
        return False


class T(Boolean):
    def __and__(self, other: Boolean):
        return other

    def __or__(self, other: Boolean):
        return self

    def __invert__(self):
        return Boolean.false()

    def __str__(self):
        return "true"

    def eq(self, other):
        if self == other:
            return self
        else:
            return other

    def is_true(self):
        return True

    __repr__ = __str__


class F(Boolean):
    def __and__(self, other: Boolean):
        return self

    def __or__(self, other: Boolean):
        return other

    def __invert__(self):
        return Boolean.true()

    def __str__(self):
        return "false"

    def eq(self, other):
        if self == other:
            return Boolean.true()
        elif other == Boolean.unknown():
            return other
        else:
            return self

    def is_false(self):
        return True

    __repr__ = __str__


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

    def eq(self, other):
        return self

    def __str__(self):
        return "unknown"

    def is_unknown(self):
        return True

    __repr__ = __str__


class Symbol(Expr):
    symbols = {}

    @classmethod
    def make(cls, name) -> Expr:
        if name not in cls.symbols.keys():
            cls.symbols[name] = cls(name)
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
        return str(self._name)

    __repr__ = __str__


class List(Expr):
    _null_instance = None

    """
    we need some sort of builder here that defers evaluation
    until runtime, otherwise literal lists will be constants
    """

    @classmethod
    def null(cls):
        """singleton factory method for Null"""
        if cls._null_instance is None:
            cls._null_instance = Null()
        return cls._null_instance

    @classmethod
    def list(cls, args, index=0):
        if index == len(args):
            return cls.null()
        else:
            return Pair(args[index], cls.list(args, index=index + 1))

    def is_null(self):
        return False

    def car(self):
        pass

    def cdr(self):
        pass

    def __len__(self):
        pass

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def trailing_string(self) -> str:
        pass

    def append(self, other) -> List:
        pass

    def __iter__(self):
        return ListIterator(self)


class Pair(List):
    def __init__(self, car, cdr: List):
        self._car = car
        self._cdr = cdr
        self._len = 1 + len(cdr)

    def car(self):
        return self._car

    def cdr(self):
        return self._cdr

    def eval(self, env: environment.Environment, ret: Callable):
        def car_continuation(evaluated_car):
            def cdr_continuation(evaluated_cdr):
                return lambda: ret(Pair(evaluated_car, evaluated_cdr))
            return lambda: self._cdr.eval(env, cdr_continuation)
        return self._car.eval(env, car_continuation)

    def __len__(self):
        return self._len

    def __str__(self):
        return '[' + str(self._car) + self._cdr.trailing_string()

    __repr__ = __str__

    def trailing_string(self) -> str:
        return ', ' + str(self._car) + self._cdr.trailing_string()

    def append(self, other: List):
        return Pair(self._car, self._cdr.append(other))

    def __eq__(self, other: List):
        if other.__class__ == Pair:
            return self._car == other.car() and self._cdr == other.cdr()
        else:
            return False


class Null(List):
    def is_null(self):
        return True

    def car(self):
        return self

    def cdr(self):
        return self

    def eval(self, env: environment.Environment, ret: Callable):
        return ret(self)

    def __len__(self):
        return 0

    def __str__(self):
        return '[]'

    __repr__ = __str__

    def trailing_string(self) -> str:
        return ']'

    def append(self, other):
        return other

    def __eq__(self, other: Expr):
        return other.is_null()


class ListIterator:
    def __init__(self, lst: List):
        self._lst = lst

    def __next__(self):
        if self._lst.is_null():
            raise StopIteration
        else:
            val = self._lst.car()
            self._lst = self._lst.cdr()
            return val


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
        return "if (" + str(self._test) + \
               ") {" + str(self._consequent) + \
               "} else {" + str(self._alternative) + "}"

    __repr__ = __str__


class Lambda(Expr):
    def __init__(self, args: List, body: Expr):
        self._args = args
        self._body = body

    def eval(self, env: environment.Environment, ret: Callable):
        return lambda: ret(op.Closure(self._args, self._body, env))

    def __str__(self):
        return "Lambda(" + str(self._args) + "{" + str(self._body) + "})"

    __repr__ = __str__


class Application(Expr):
    def __init__(self, operation: Expr, operands: List):
        self._operation = operation
        self._operands = operands

    def eval(self, env: environment.Environment, ret: Callable):
        def deferred_op(evaluated_op):
            return lambda: evaluated_op.apply(self._operands, env, ret)
        return self._operation.eval(env, deferred_op)

    def __str__(self):
        return "Application(" + str(self._operation) + ": " + str(self._operands) + ")"


