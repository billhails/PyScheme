# PyScheme lambda language written in Python
#
# Expressions (created by the parser) for evaluation
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

from . import environment
from .exceptions import NonBooleanExpressionError
from .singleton import Singleton, FlyWeight
from . import types


class Expr:
    def eval(self, env: 'environment.Environment', ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        pass

    def is_true(self) -> bool:
        raise NonBooleanExpressionError()

    def is_false(self) -> bool:
        raise NonBooleanExpressionError()

    def is_unknown(self) -> bool:
        raise NonBooleanExpressionError()

    def value(self):
        pass

    def __eq__(self, other: 'Expr') -> bool:
        return id(self) == id(other)

    def eq(self, other: 'Expr') -> 'Boolean':
        if self == other:
            return T()
        else:
            return F()

    def gt(self, other: 'Expr') -> 'Boolean':
        if self > other:
            return T()
        else:
            return F()

    def lt(self, other: 'Expr') -> 'Boolean':
        if self < other:
            return T()
        else:
            return F()

    def ge(self, other: 'Expr') -> 'Boolean':
        if self >= other:
            return T()
        else:
            return F()

    def le(self, other: 'Expr') -> 'Boolean':
        if self <= other:
            return T()
        else:
            return F()

    def ne(self, other: 'Expr') -> 'Boolean':
        if self != other:
            return T()
        else:
            return F()

    def is_null(self) -> bool:
        return False


class Constant(Expr):
    def __init__(self, value):
        self._value = value

    def eval(self, env: 'environment.Environment', ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: ret(self, amb)

    def value(self):
        return self._value

    def __eq__(self, other: Expr) -> bool:
        if type(other) is Constant:
            return self._value == other.value()
        else:
            return False

    def __gt__(self, other: Expr) -> bool:
        if type(other) is Constant:
            return self._value > other.value()
        else:
            return False

    def __lt__(self, other: Expr) -> bool:
        if type(other) is Constant:
            return self._value < other.value()
        else:
            return False

    def __ge__(self, other: Expr) -> bool:
        if type(other) is Constant:
            return self._value >= other.value()
        else:
            return False

    def __le__(self, other: Expr) -> bool:
        if type(other) is Constant:
            return self._value <= other.value()
        else:
            return False

    def __ne__(self, other: Expr) -> bool:
        if type(other) is Constant:
            return self._value != other.value()
        else:
            return False

    def __add__(self, other: Expr):
        return Constant(self._value + other.value())

    def __sub__(self, other: Expr):
        return Constant(self._value - other.value())

    def __mul__(self, other: Expr):
        return Constant(self._value * other.value())

    def __floordiv__(self, other: Expr):
        return Constant(self._value // other.value())

    def __mod__(self, other: Expr):
        return Constant(self._value % other.value())

    def __str__(self) -> str:
        return str(self._value)

    __repr__ = __str__


class Boolean(Constant):

    def __and__(self, other: 'Boolean') -> 'Boolean':
        pass

    def __or__(self, other: 'Boolean') -> 'Boolean':
        pass

    def __invert__(self) -> 'Boolean':
        pass

    def __xor__(self, other: 'Boolean') -> 'Boolean':
        return (self & ~other) | (other & ~self)

    def __eq__(self, other: 'Boolean') -> bool:
        return id(self) == id(other)

    def is_true(self) -> bool:
        return False

    def is_false(self) -> bool:
        return False

    def is_unknown(self) -> bool:
        return False


class T(Boolean, metaclass=Singleton):
    def __init__(self):
        super(T, self).__init__('true')

    def __and__(self, other: Boolean) -> Boolean:
        return other

    def __or__(self, other: Boolean) -> Boolean:
        return self

    def __invert__(self) -> Boolean:
        return F()

    def __str__(self) -> str:
        return "true"

    def eq(self, other: Boolean) -> Boolean:
        if self == other:
            return self
        else:
            return other

    def is_true(self) -> bool:
        return True

    __repr__ = __str__


class F(Boolean, metaclass=Singleton):
    def __init__(self):
        super(F, self).__init__('false')

    def __and__(self, other: Boolean) -> Boolean:
        return self

    def __or__(self, other: Boolean) -> Boolean:
        return other

    def __invert__(self) -> Boolean:
        return T()

    def __str__(self) -> str:
        return "false"

    def eq(self, other: Boolean) -> Boolean:
        if self == other:
            return T()
        elif other == U():
            return other
        else:
            return self

    def is_false(self) -> bool:
        return True

    __repr__ = __str__


class U(Boolean, metaclass=Singleton):
    def __init__(self):
        super(U, self).__init__('unknown')

    def __and__(self, other: Boolean) -> Boolean:
        if other == F():
            return other
        else:
            return self

    def __or__(self, other: Boolean) -> Boolean:
        if other == T():
            return other
        else:
            return self

    def __invert__(self) -> Boolean:
        return self

    def eq(self, other: Boolean) -> Boolean:
        return self

    def __str__(self) -> str:
        return "unknown"

    def is_unknown(self) -> bool:
        return True

    __repr__ = __str__


class Symbol(Expr, metaclass=FlyWeight):
    def __init__(self, name):
        self._name = name

    def eval(self, env: 'environment.Environment', ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: env.lookup(self, ret, amb)

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other) -> bool:
        return id(self) == id(other)

    def __str__(self) -> str:
        return str(self._name)

    __repr__ = __str__


class List(Expr):
    @classmethod
    def list(cls, args, index=0) -> 'List':
        if index == len(args):
            return Null()
        else:
            return Pair(args[index], cls.list(args, index=index + 1))

    def is_null(self) -> bool:
        return False

    def car(self) -> Expr:
        pass

    def cdr(self) -> 'List':
        pass

    def __len__(self) -> int:
        pass

    def __str__(self) -> str:
        return self.qualified_str('[', ', ', ']')

    __repr__ = __str__

    def __getitem__(self, item) -> Expr:
        pass

    def qualified_str(self, start: str, sep: str, end: str) -> str:
        pass

    def trailing_str(self, sep: str, end: str) -> str:
        pass

    def append(self, other: 'List') -> 'List':
        pass

    def last(self: Expr) -> Expr:
        pass

    def __iter__(self) -> 'ListIterator':
        return ListIterator(self)


class Pair(List):
    def __init__(self, car: Expr, cdr: List):
        self._car = car
        self._cdr = cdr
        self._len = 1 + len(cdr)

    def car(self) -> Expr:
        return self._car

    def cdr(self) -> List:
        return self._cdr

    def eval(self, env: 'environment.Environment', ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        def car_continuation(evaluated_car: Expr, amb: 'types.Amb') -> 'types.Promise':
            def cdr_continuation(evaluated_cdr: List, amb: 'types.Amb') -> 'types.Promise':
                return lambda: ret(Pair(evaluated_car, evaluated_cdr), amb)
            return lambda: self._cdr.eval(env, cdr_continuation, amb)
        return self._car.eval(env, car_continuation, amb)

    def last(self) -> Expr:
        if self._len == 1:
            return self._car
        else:
            return self._cdr.last()

    def __len__(self) -> int:
        return self._len

    def qualified_str(self, start: str, sep: str, end: str) -> str:
        return start + str(self._car) + self._cdr.trailing_str(sep, end)

    def trailing_str(self, sep: str, end: str) -> str:
        return sep + str(self._car) + self._cdr.trailing_str(sep, end)

    def append(self, other: List) -> List:
        return Pair(self._car, self._cdr.append(other))

    def __eq__(self, other: List) -> bool:
        if type(other) is Pair:
            return self._car == other.car() and self._cdr == other.cdr()
        else:
            return False

    def __getitem__(self, item) -> Expr:
        if type(item) is not int:
            raise TypeError
        if item < 0:
            raise KeyError
        val = self
        while item > 0:
            val = val.cdr()
            item -= 1
        if val.is_null():
            raise KeyError
        return val.car()


class Null(List, metaclass=Singleton):
    def is_null(self) -> bool:
        return True

    def car(self) -> Expr:
        return self

    def cdr(self) -> List:
        return self

    def eval(self, env: 'environment.Environment', ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return ret(self, amb)

    def last(self) -> Expr:
        return self

    def __len__(self) -> int:
        return 0

    def qualified_str(self, start: str, sep: str, end: str) -> str:
        return start + end

    def trailing_str(self, sep: str, end: str) -> str:
        return end

    def append(self, other: List) -> List:
        return other

    def __eq__(self, other: Expr) -> bool:
        return other.is_null()

    def __getitem__(self, item: int):
        if type(item) is not int:
            raise TypeError
        raise KeyError


class ListIterator:
    def __init__(self, lst: List):
        self._lst = lst

    def __next__(self) -> Expr:
        if self._lst.is_null():
            raise StopIteration
        else:
            val = self._lst.car()
            self._lst = self._lst.cdr()
            return val


class Char(Expr, metaclass=FlyWeight):
    def __init__(self, value: str):
        self._value = value

    def __str__(self) -> str:
        return "'" + str(self._value) + "'"


class Conditional(Expr):
    def __init__(self, test: Expr, consequent: Expr, alternative: Expr):
        self._test = test
        self._consequent = consequent
        self._alternative = alternative

    def eval(self, env: 'environment.Environment', ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        def test_continuation(result: Expr, amb: 'types.Amb') -> 'types.Promise':
            if result.is_true():
                return lambda: self._consequent.eval(env, ret, amb)
            else:
                return lambda: self._alternative.eval(env, ret, amb)
        return self._test.eval(env, test_continuation, amb)

    def __str__(self) -> str:
        return "if (" + str(self._test) + \
               ") {" + str(self._consequent) + \
               "} else {" + str(self._alternative) + "}"

    __repr__ = __str__


class Lambda(Expr):
    def __init__(self, args: List, body: Expr):
        self._args = args
        self._body = body

    def eval(self, env: 'environment.Environment', ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: ret(Closure(self._args, self._body, env), amb)

    def __str__(self) -> str:
        return "Lambda " + str(self._args) + ": { " + str(self._body) + " }"

    __repr__ = __str__


class Application(Expr):
    def __init__(self, operation: Expr, operands: List):
        self._operation = operation
        self._operands = operands

    def eval(self, env: 'environment.Environment', ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':

        def evaluated_op_continuation(evaluated_op: 'Op', amb: 'types.Amb') -> 'types.Promise':
            return lambda: evaluated_op.apply(self._operands, env, ret, amb)

        return self._operation.eval(env, evaluated_op_continuation, amb)

    def __str__(self) -> str:
        return str(self._operation) + str(self._operands)


class Sequence(Expr):
    def __init__(self, exprs: List):
        self._exprs = exprs

    def eval(self, env: 'environment.Environment', ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        def take_last_continuation(expr: List, amb: 'types.Amb') -> 'types.Promise':
            return lambda: ret(expr.last(), amb)
        return self._exprs.eval(env, take_last_continuation, amb)

    def __str__(self) -> str:
        return self._exprs.qualified_str('', ' ; ', '')


class Nest(Expr):
    def __init__(self, body: Sequence):
        self._body = body

    def eval(self, env: 'environment.Environment', ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        """Evaluate the body in an extended environment
        """
        return self._body.eval(env.extend(), ret, amb)

    def __str__(self):
        return str(self._body)


class EnvironmentWrapper(Expr):
    """Wrapper for Environments to make them Exprs
    """
    def __init__(self, env: 'environment.Environment'):
        self._env = env

    def env(self):
        return self._env


class Env(Expr):
    """Implements the 'env' construct
    """
    def __init__(self, body: Sequence):
        self._body = body

    def eval(self, env: 'environment.Environment', ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        """evaluate the body in an extended env then return the extended env as the result
        """
        new_env = env.extend()

        def eval_continuation(val: Expr, amb: 'types.Amb') -> 'types.Promise':
            return ret(EnvironmentWrapper(new_env), amb)

        return self._body.eval(new_env, eval_continuation, amb)


class Op(Expr):
    def apply(self, args: List, env: 'environment.Environment', ret: 'types.Continuation', amb: 'types.Amb'):
        pass


class Primitive(Op):
    def apply(self, args: List, env: 'environment.Environment', ret: 'types.Continuation', amb: 'types.Amb'):
        def deferred_apply(evaluated_args: List, amb: 'types.Amb') -> 'types.Promise':
            return lambda: self.apply_evaluated_args(evaluated_args, ret, amb)
        return args.eval(env, deferred_apply, amb)

    def apply_evaluated_args(self, args, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        pass


class SpecialForm(Op):
    pass


class Closure(Primitive):
    def __init__(self, args: List, body: Expr, env: 'environment.Environment'):
        self._args = args
        self._body = body
        self._env = env

    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        formal_args = self._args
        actual_args = args
        dictionary = {}
        while type(formal_args) is not Null and type(actual_args) is not Null:
            dictionary[formal_args.car()] = actual_args.car()
            formal_args = formal_args.cdr()
            actual_args = actual_args.cdr()
        if type(formal_args) is not Null:  # currying
            return lambda: ret(Closure(formal_args, self._body, self._env.extend(dictionary)), amb)
        elif type(actual_args) is not Null:  # over-complete function application

            def re_apply_continuation(closure: Closure, amb: 'types.Amb') -> 'types.Promise':
                return lambda: closure.apply_evaluated_args(actual_args, ret, amb)

            return lambda: self._body.eval(self._env.extend(dictionary), re_apply_continuation, amb)
        else:  # formal and actual args match
            return lambda: self._body.eval(self._env.extend(dictionary), ret, amb)

    def __str__(self) -> str:
        return "Closure(" + str(self._args) + ": " + str(self._body) + ")"


class Addition(Primitive, metaclass=Singleton):
    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb'):
        return lambda: ret(args[0] + args[1], amb)


class Subtraction(Primitive, metaclass=Singleton):
    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: ret(args[0] - args[1], amb)


class Multiplication(Primitive, metaclass=Singleton):
    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: ret(args[0] * args[1], amb)


class Division(Primitive, metaclass=Singleton):
    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: ret(args[0] // args[1], amb)


class Modulus(Primitive, metaclass=Singleton):
    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: ret(args[0] % args[1], amb)


class Equality(Primitive, metaclass=Singleton):
    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: ret(args[0].eq(args[1]), amb)


class GT(Primitive, metaclass=Singleton):
    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: ret(args[0].gt(args[1]), amb)


class LT(Primitive, metaclass=Singleton):
    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: ret(args[0].lt(args[1]), amb)


class GE(Primitive, metaclass=Singleton):
    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: ret(args[0].ge(args[1]), amb)


class LE(Primitive, metaclass=Singleton):
    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: ret(args[0].le(args[1]), amb)


class NE(Primitive, metaclass=Singleton):
    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: ret(args[0].ne(args[1]), amb)


class And(SpecialForm, metaclass=Singleton):
    def apply(self, args: List,
              env: 'environment.Environment',
              ret: 'types.Continuation',
              amb: 'types.Amb') -> 'types.Promise':

        def cont(lhs: Expr, amb: 'types.Amb') -> 'types.Promise':
            if lhs.is_true():
                return lambda: args[1].eval(env, ret, amb)
            elif lhs.is_false():
                return lambda: ret(lhs, amb)
            else:
                def cont2(rhs: Expr, amb: 'types.Continuation') -> 'types.Promise':
                    if rhs.is_false():
                        return lambda: ret(rhs, amb)
                    else:
                        return lambda: ret(lhs, amb)

                return lambda: args[1].eval(env, cont2, amb)

        return lambda: args[0].eval(env, cont, amb)


class Or(SpecialForm, metaclass=Singleton):
    def apply(self, args: List,
              env: 'environment.Environment',
              ret: 'types.Continuation',
              amb: 'types.Amb') -> 'types.Promise':

        def cont(lhs: Expr, amb: 'types.Amb') -> 'types.Promise':
            if lhs.is_true():
                return lambda: ret(lhs, amb)
            elif lhs.is_false():
                return lambda: args[1].eval(env, ret, amb)
            else:
                def cont2(rhs: Expr, amb: 'types.Continuation') -> 'types.Promise':
                    if rhs.is_true():
                        return lambda: ret(rhs, amb)
                    else:
                        return lambda: ret(lhs, amb)

                return lambda: args[1].eval(env, cont2, amb)

        return lambda: args[0].eval(env, cont, amb)


class Then(SpecialForm, metaclass=Singleton):
    def apply(self, args: List,
              env: 'environment.Environment',
              ret: 'types.Continuation',
              amb: 'types.Amb') -> 'types.Promise':

        def amb2() -> 'types.Promise':
            return lambda: args[1].eval(env, ret, amb)

        return lambda: args[0].eval(env, ret, amb2)


class Back(SpecialForm, metaclass=Singleton):
    def apply(self, args: List,
              env: 'environment.Environment',
              ret: 'types.Continuation',
              amb: 'types.Amb') -> 'types.Promise':
        return lambda: amb()


class Not(Primitive, metaclass=Singleton):
    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: ret(~(args[0]), amb)


class Xor(Primitive, metaclass=Singleton):
    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: ret(args[0] ^ args[1], amb)


class Cons(Primitive, metaclass=Singleton):
    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: ret(Pair(args[0], args[1]), amb)


class Append(Primitive, metaclass=Singleton):
    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: ret(args[0].append(args[1]), amb)


class Head(Primitive, metaclass=Singleton):
    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: ret(args[0].car(), amb)


class Tail(Primitive, metaclass=Singleton):
    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: ret(args[0].cdr(), amb)


class Define(SpecialForm, metaclass=Singleton):
    def apply(self,
              args: List,
              env: 'environment.Environment',
              ret: 'types.Continuation',
              amb: 'types.Amb') -> 'types.Promise':

        def define_continuation(value: Expr, amb: 'types.Amb') -> 'types.Promise':

            def ret_none(value: Expr, amb: 'types.Amb') -> 'types.Promise':
                return lambda: ret(None, amb)

            return lambda: env.define(args[0], value, ret_none, amb)

        return lambda: args[1].eval(env, define_continuation, amb)


class Length(Primitive, metaclass=Singleton):
    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: ret(Constant(len(args[0])), amb)


class Print(Primitive):
    def __init__(self, output):
        self._output = output

    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        for arg in args:
            self._output.write(str(arg))
        self._output.write("\n")
        return lambda: ret(args, amb)


class Cont(Primitive):
    def __init__(self, ret: callable):
        self._ret = ret

    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: self._ret(args[0], amb)

    def eval(self, env: 'environment.Environment', ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return lambda: ret(self, amb)


class CallCC(SpecialForm, metaclass=Singleton):
    def apply(self,
              args: List,
              env: 'environment.Environment',
              ret: 'types.Continuation',
              amb: 'types.Amb') -> 'types.Promise':

        def do_apply(closure: Closure, amb: 'types.Amb') -> 'types.Promise':
            return lambda: closure.apply(List.list([Cont(ret)]), env, ret, amb)

        return args[0].eval(env, do_apply, amb)


class Exit(Primitive):
    def apply_evaluated_args(self, args: List, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        return None


class Error(SpecialForm):
    def __init__(self, cont):
        self.cont = cont

    def apply(self,
              args: List,
              env: 'environment.Environment',
              ret: 'types.Continuation',
              amb: 'types.Amb') -> 'types.Promise':

        def print_continuation(printer: Print, amb: 'types.Amb') -> 'types.Promise':
            return lambda: printer.apply(args, env, self.cont, amb)

        return env.lookup(Symbol("print"), print_continuation, amb)


class EvaluateInEnv(SpecialForm):
    def apply(self,
              args: List,
              env: 'environment.Environment',
              ret: 'types.Continuation',
              amb: 'types.Amb') -> 'types.Promise':

        def env_continuation(new_env: EnvironmentWrapper, amb: 'types.Amb') -> 'types.Promise':
            return lambda: args[1].eval(new_env.env(), ret, amb)

        return args[0].eval(env, env_continuation, amb)