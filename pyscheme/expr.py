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
from .exceptions import NonBooleanExpressionError, PySchemeInternalError, MissingPrototypeError,\
    PySchemeInferenceError, PySchemeRunTimeError
from .trace import trace
from .singleton import Singleton, FlyWeight
from . import types
from . import inference
from . import ambivalence
from pathlib import Path
from typing import Union
import inspect
import os
import sys


def debug(*args, **kwargs):
    if Config.debug:
        print(*args, **kwargs)

def hlDebug(*args, **kwargs):
    if Config.hlDebug:
        print(*args, **kwargs)

class Config:
    debug = False
    hlDebug = False

def verify(amb: ambivalence.Amb):
    assert isinstance(amb, ambivalence.Amb)

class Expr:
    current_analysis = None

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        return lambda: ret(self, amb)

    def apply(self,
              args: 'LinkedList',
              env: 'environment.Environment',
              ret: types.Continuation,
              amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        if len(args) == 0:
            return lambda: ret(self, amb)
        else:
            raise PySchemeInternalError("non-op " + str(type(self)) + " called with arguments")

    def type(self):
        raise PySchemeInferenceError("cannot determine type of " + str(type(self)) + ' ' + str(self))

    def is_true(self) -> bool:
        raise NonBooleanExpressionError()

    def is_false(self) -> bool:
        raise NonBooleanExpressionError()

    def is_unknown(self) -> bool:
        raise NonBooleanExpressionError()

    def is_constant(self) -> bool:
        """
        used by analyse_internal to avoid putting the expression in a type environment
        """
        return False

    def value(self):
        pass

    def match(self, other: 'Expr', env: 'environment.Environment', ret: types.Continuation,
              amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        raise PySchemeInferenceError("cannot match " + str(type(self)))

    def prepare_analysis(self, env: inference.TypeEnvironment):
        pass

    def analyse_farg(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        raise PySchemeInferenceError(str(type(self)) + " cannot be used as a formal argument")

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

    def analyse(self, env: inference.TypeEnvironment, non_generic=None) -> inference.Type:
        if non_generic is None:
            non_generic = set()
        self.prepare_analysis(env)
        return self.analyse_internal(env, non_generic)

    @trace
    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        return self.type()

    def static_type(self) -> bool:
        return False

    def looks_like_binop(self):
        return False

    def __cmp__(self, other):
        if id(self) == id(other):
            return 0
        elif id(self) < id(other):
            return -1
        else:
            return 1

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __le__(self, other):
        return self.__cmp__(other) <= 0

    def __ge__(self, other):
        return self.__cmp__(other) >= 0

    def __ne__(self, other):
        return self.__cmp__(other) != 0

    def compile(self):
        pass

    def cursory_type(self):
        """
        an interrim type for prepare_analysis
        """
        return inference.TypeVariable()


class Nothing(Expr, metaclass=Singleton):
    """
    analogous to Python's 'None'
    """
    def __init__(self):
        pass

    @classmethod
    def type(cls):
        return inference.TypeOperator("nothing")

    def static_type(self) -> bool:
        return True

    def is_constant(self):
        return True

    def __str__(self):
        return "nothing"

    def __cmp__(self, other):
        return 0  # only type-checked option here is another "Nothing"


class Constant(Expr):
    def __init__(self, value):
        self._value = value

    def value(self):
        return self._value

    def static_type(self) -> bool:
        return True

    def analyse_farg(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        return self.type()

    def match(self, other: 'Expr', env: 'environment.Environment', ret: types.Continuation,
              amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        if self == other:
            return lambda: ret(self, amb)
        else:
            return amb

    def __cmp__(self, other: 'Constant'):
        if self._value < other.value():
            return -1
        elif self._value == other.value():
            return 0
        else:
            return 1

    def __str__(self) -> str:
        return str(self._value)

    __repr__ = __str__


class Char(Constant):
    @classmethod
    def type(cls):
        return inference.TypeOperator('char')


class Number(Constant):
    @classmethod
    def type(cls):
        return inference.TypeOperator("int")

    def __add__(self, other: Expr):
        return Number(self._value + other.value())

    def __sub__(self, other: Expr):
        return Number(self._value - other.value())

    def __mul__(self, other: Expr):
        return Number(self._value * other.value())

    def __floordiv__(self, other: Expr):
        return Number(self._value // other.value())

    def __mod__(self, other: Expr):
        return Number(self._value % other.value())

    def __pow__(self, power: Expr, modulo=None):
        return Number(self._value ** power.value())


class Wildcard(Constant, metaclass=Singleton):
    def __init__(self):
        super(Wildcard, self).__init__('_')

    @classmethod
    def type(cls):
        return inference.TypeVariable()

    def match(self, other: 'Expr', env: 'environment.Environment', ret: types.Continuation,
              amb: ambivalence.Amb) -> types.Promise:
        """
        always match
        """
        verify(amb)
        return lambda: ret(self, amb)

    def __len__(self):
        return 1

    def trailing_str(self, _, end: str):
        return " . " + str(self) + end

    def trailing_repr(self, _, end: str):
        return " . " + repr(self) + end

class Boolean(Constant):
    @classmethod
    def type(cls):
        return inference.TypeOperator("bool")

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

    def eq(self, other: Boolean) -> Boolean:
        if self == other:
            return self
        else:
            return F()

    def is_true(self) -> bool:
        return True

    def __cmp__(self, other):
        if isinstance(other, T):
            return 0
        else:
            return 1


class F(Boolean, metaclass=Singleton):
    def __init__(self):
        super(F, self).__init__('false')

    def __and__(self, other: Boolean) -> Boolean:
        return self

    def __or__(self, other: Boolean) -> Boolean:
        return other

    def __invert__(self) -> Boolean:
        return T()

    def eq(self, other: Boolean) -> Boolean:
        if self == other:
            return T()
        else:
            return self

    def is_false(self) -> bool:
        return True

    def __cmp__(self, other):
        if isinstance(other, F):
            return 0
        else:
            return -1


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
        if self == other:
            return T()
        else:
            return F()

    def is_unknown(self) -> bool:
        return True

    def __cmp__(self, other):
        if isinstance(other, U):
            return 0
        elif isinstance(other, T):
            return -1
        else:
            return 1


class Symbol(Constant, metaclass=FlyWeight):
    counter = 0

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        return lambda: env.lookup(self, ret, amb)

    def match(self, other: 'Expr', env: 'environment.Environment', ret: types.Continuation,
              amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        if env.contains(self) and type(env[self]) is NamedTuple:
            return lambda: env[self].match(other, env, ret, amb)
        else:
            return lambda: env.define(self, other, ret, amb)

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other) -> bool:
        return id(self) == id(other)

    def __len__(self):
        return 1

    def trailing_str(self, _: str, end: str) -> str:
        return ' . ' + str(self) + end

    def trailing_repr(self, _: str, end: str) -> str:
        return ' . ' + repr(self) + end

    @trace
    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        return self.get_type(env, non_generic)

    def get_type(self, env: inference.TypeEnvironment, non_generic: set):
        return env[self].fresh(non_generic)

    def analyse_farg(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        if env.noted_type_constructor(self):
            return_type = env[self]
        else:
            return_type = inference.TypeVariable()
            env[self] = return_type
            non_generic.add(return_type)
        return return_type

    def looks_like_binop(self):
        return self._value == 'then' or not self._value.isalnum()

    @classmethod
    def generate(cls):
        name = ''
        if cls.counter == 0:
            name = 'a'
        else:
            counter = cls.counter
            while counter > 0:
                remainder = counter % 26
                name += chr(ord('a') + remainder)
                counter = counter // 26

        cls.counter += 1
        return Symbol('#' + name)

    @classmethod
    def reset(cls):
        """
        for testing
        """
        cls.counter = 0


class TypedSymbol(Expr):
    def __init__(self, symbol: Symbol, type_symbol: Symbol):
        self._symbol = symbol
        self._type_symbol = type_symbol

    def symbol(self):
        return self._symbol

    def type_symbol(self):
        return self._type_symbol

    def __str__(self):
        return str(self._symbol) + ':' + str(self._type_symbol)

    def analyse_farg(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        arg_type = env[self.type_symbol()]
        env[self.symbol()] = arg_type
        non_generic.add(arg_type)
        return arg_type

    def match(self, other: 'Expr', env: 'environment.Environment', ret: types.Continuation,
              amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        return lambda: env.define(self.symbol(), other, ret, amb)

    __repr__ = __str__


class As(Expr):
    def __init__(self, symbol: Symbol, definition: Expr):
        self._symbol = symbol
        self._definition = definition

    def __str__(self):
        return str(self._symbol) + ' = ' + str(self._definition)

    __repr__ = __str__

    def analyse_farg(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        arg_type = self._definition.analyse_farg(env, non_generic)
        env[self._symbol] = arg_type
        non_generic.add(arg_type)
        return arg_type

    def match(self, other: 'Expr', env: 'environment.Environment', ret: types.Continuation,
              amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        def match_continuation(_: Expr, amb: ambivalence.Amb) -> types.Promise:
            verify(amb)
            return lambda: env.define(self._symbol, other, ret, amb)
        return self._definition.match(other, env, match_continuation, amb)


class LinkedList(Expr):
    @classmethod
    def type(cls, content=None):
        if content is None:
            content = inference.TypeVariable()
        return inference.TypeOperator('list', content)

    @classmethod
    def list(cls, args, index=0) -> 'LinkedList':
        if index == len(args):
            return Null()
        else:
            return Pair(args[index], cls.list(args, index=index + 1))

    def is_null(self) -> bool:
        return False

    def car(self) -> Expr:
        pass

    def cdr(self) -> 'LinkedList':
        pass

    def is_string(self):
        return False

    def __len__(self) -> int:
        pass

    def __str__(self) -> str:
        if self.is_string():
            return self.qualified_str('', '', '')
        else:
            return self.qualified_str('[', ', ', ']')

    def __repr__(self):
        if self.is_string():
            return self.qualified_repr('"', '', '"')
        else:
            return self.qualified_repr('[', ', ', ']')

    def __getitem__(self, item) -> Expr:
        pass

    def qualified_str(self, start: str, sep: str, end: str) -> str:
        pass

    def qualified_repr(self, start: str, sep: str, end: str) -> str:
        pass

    def trailing_str(self, sep: str, end: str) -> str:
        pass

    def trailing_repr(self, sep: str, end: str) -> str:
        pass

    def append(self, other: 'LinkedList') -> 'LinkedList':
        pass

    def last(self: Expr) -> Expr:
        pass

    def map(self, fn: callable) -> 'LinkedList':
        pass

    def __iter__(self) -> 'ListIterator':
        return ListIterator(self)

    def __cmp__(self, other: 'LinkedList'):
        pass


class Pair(LinkedList):
    def __init__(self, car: Expr, cdr: LinkedList):
        self._car = car
        self._cdr = cdr
        self._len = 1 + len(cdr)

    def car(self) -> Expr:
        return self._car

    def cdr(self) -> LinkedList:
        return self._cdr

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        # noinspection PyShadowingNames
        def car_continuation(evaluated_car: Expr, amb: ambivalence.Amb) -> types.Promise:
            verify(amb)
            # noinspection PyShadowingNames
            def cdr_continuation(evaluated_cdr: LinkedList, amb: ambivalence.Amb) -> types.Promise:
                verify(amb)
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

    def is_string(self):
        return type(self._car) is Char

    def qualified_str(self, start: str, sep: str, end: str) -> str:
        return start + str(self._car) + self._cdr.trailing_str(sep, end)

    def qualified_repr(self, start: str, sep: str, end: str) -> str:
        return start + repr(self._car) + self._cdr.trailing_repr(sep, end)

    def trailing_str(self, sep: str, end: str) -> str:
        return sep + str(self._car) + self._cdr.trailing_str(sep, end)

    def trailing_repr(self, sep: str, end: str) -> str:
        return sep + repr(self._car) + self._cdr.trailing_repr(sep, end)

    def append(self, other: LinkedList) -> LinkedList:
        return Pair(self._car, self._cdr.append(other))

    def match(self, other: 'LinkedList', env: 'environment.Environment', ret: types.Continuation,
              amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        # noinspection PyShadowingNames
        def car_continuation(_, amb) -> types.Promise:
            verify(amb)
            return lambda: self.cdr().match(other.cdr(), env, ret, amb)

        return lambda: self.car().match(other.car(), env, car_continuation, amb)

    @trace
    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        self_type = inference.TypeOperator('list', self._car.analyse_internal(env, non_generic))
        rest_type = self.cdr().analyse_internal(env, non_generic)
        self_type.unify(rest_type)
        return self_type

    def prepare_analysis(self, env: inference.TypeEnvironment):
        self.car().prepare_analysis(env)
        self.cdr().prepare_analysis(env)

    def map(self, fn: callable) -> LinkedList:
        return Pair(fn(self._car), self._cdr.map(fn))

    def analyse_farg(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        """
        We have to return a result type
        We have to populate the environment with variables
        """

        type_so_far = inference.TypeVariable()

        def analyse_recursive(pair: LinkedList) -> inference.Type:
            if isinstance(pair, Null):
                result_type = Pair.type(type_so_far)
                result_type.unify(Null.type())
                return result_type  # list of something
            elif isinstance(pair, Symbol):
                result_type = Pair.type(type_so_far)
                env[pair] = result_type
                return result_type
            elif isinstance(pair, Wildcard):
                return Pair.type(type_so_far)
            elif isinstance(pair, Pair):
                arg_type = pair.car().analyse_farg(env, non_generic)
                type_so_far.unify(arg_type)
                return analyse_recursive(pair.cdr())

        return analyse_recursive(self)

    def __eq__(self, other: LinkedList) -> bool:
        if type(other) is Pair:
            return self._car == other.car() and self._cdr == other.cdr()
        else:
            return False

    def __getitem__(self, item) -> Expr:
        if type(item) is not int:
            raise TypeError
        if item < 0:
            raise KeyError
        if item >= self._len:
            raise KeyError
        val = self
        while item > 0:
            val = val.cdr()
            item -= 1
        if val.is_null():
            raise KeyError
        return val.car()

    def __cmp__(self, other: LinkedList):
        if isinstance(other, Null):
            return 1
        if self.car() == (other.car()):
            return self.cdr().__cmp__(other.cdr())
        else:
            return -1 if self.car() < other.car() else 1


class Null(LinkedList, metaclass=Singleton):
    def analyse_farg(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        return self.type()

    def is_null(self) -> bool:
        return True

    def car(self) -> Expr:
        raise PySchemeRunTimeError("cannot take the car of null")

    def cdr(self) -> LinkedList:
        raise PySchemeRunTimeError("cannot take the cdr of null")

    def last(self) -> Expr:
        return self

    def qualified_str(self, start: str, sep: str, end: str) -> str:
        return start + end

    def qualified_repr(self, start: str, sep: str, end: str) -> str:
        return start + end

    def trailing_str(self, sep: str, end: str) -> str:
        return end

    def trailing_repr(self, sep: str, end: str) -> str:
        return end

    def append(self, other: LinkedList) -> LinkedList:
        return other

    def map(self, fn: callable) -> LinkedList:
        return self

    def is_constant(self):
        return True

    def match(self, other: 'Expr', env: 'environment.Environment', ret: types.Continuation,
              amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        if self == other:
            return lambda: ret(self, amb)
        else:
            return lambda: amb()

    def __len__(self) -> int:
        return 0

    def __eq__(self, other: Expr) -> bool:
        return other.is_null()

    def __getitem__(self, item: int):
        if type(item) is not int:
            raise TypeError
        raise KeyError

    def static_type(self) -> bool:
        return True

    def __cmp__(self, other: LinkedList):
        if isinstance(other, Null):
            return 0
        else:
            return -1


class ListIterator:
    def __init__(self, lst: LinkedList):
        self._lst = lst

    def __next__(self) -> Expr:
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

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        # noinspection PyShadowingNames
        verify(amb)
        def test_continuation(result: Expr, amb: ambivalence.Amb) -> types.Promise:
            verify(amb)
            if result.is_true():
                return lambda: self._consequent.eval(env, ret, amb)
            else:
                return lambda: self._alternative.eval(env, ret, amb)

        return self._test.eval(env, test_continuation, amb)

    @trace
    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        boolean_type = Boolean.type()
        test_type = self._test.analyse_internal(env, non_generic)
        boolean_type.unify(test_type)
        consequent_type = self._consequent.analyse_internal(env, non_generic)
        consequent_type.unify(self._alternative.analyse_internal(env, non_generic))
        return consequent_type

    def __str__(self) -> str:
        return "if (" + str(self._test) + \
               ") {" + str(self._consequent) + \
               "} else {" + str(self._alternative) + "}"

    __repr__ = __str__


class Lambda(Expr):
    def __init__(self, args: LinkedList, body: Expr):
        self._args = args
        self._body = body
        self.name = "lambda"

    def num_args(self):
        return len(self._args)

    def set_name(self, name: str):
        self.name = name

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        if len(self._args) == 0:
            return lambda: self._body.eval(env, ret, amb)  # conform to type-checker's expectations
        else:
            closure = self.closure(self._args, self._body, env)
            closure.set_name(self.name)
            return lambda: ret(closure, amb)

    def closure(self, args: LinkedList, body: Expr, env: 'environment.Environment') -> 'Closure':
        """
        intended to be overridden by i.e. ComponentLambda
        """
        return Closure(args, body, env)

    @trace
    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set):
        new_env = env.extend()
        new_non_generic = non_generic.copy()

        def analyse_recursive(args: LinkedList) -> inference.Type:
            if isinstance(args, Null):
                self._body.prepare_analysis(new_env)
                return self._body.analyse_internal(new_env, new_non_generic)
            else:
                arg_type = args.car().analyse_farg(new_env, new_non_generic)
                result_type = analyse_recursive(args.cdr())
                return inference.Function(arg_type, result_type)

        return analyse_recursive(self._args)

    def __str__(self) -> str:
        return self.__class__.__name__ + " " + str(self._args) + ": { " + str(self._body) + " }"

    __repr__ = __str__


class Application(Expr):
    def __init__(self, operation: Expr, operands: LinkedList):
        self._operation = operation
        self._operands = operands

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:

        # noinspection PyShadowingNames
        verify(amb)
        def evaluated_op_continuation(evaluated_op: 'Op', amb: ambivalence.Amb) -> types.Promise:
            verify(amb)
            return lambda: evaluated_op.apply(self._operands, env, ret, amb)

        return self._operation.eval(env, evaluated_op_continuation, amb)

    @trace
    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        result_type = inference.TypeVariable()

        def analyse_recursive(operands: LinkedList) -> inference.Type:
            if type(operands) is Null:
                return result_type
            else:
                return inference.Function(
                    operands.car().analyse_internal(env, non_generic),
                    analyse_recursive(operands.cdr())
                )

        analyse_recursive(self._operands).unify(self._operation.analyse_internal(env, non_generic))
        return result_type

    def __str__(self) -> str:
        if self._operation.looks_like_binop() and len(self._operands) == 2:
            return '(' + str(self._operands[0]) + ' ' + str(self._operation) + ' ' + str(self._operands[1]) + ')'
        return str(self._operation) + str(self._operands)

    __repr__ = __str__


class Sequence(Expr):
    def __init__(self, exprs: LinkedList):
        self._exprs = self.hoist_loads(exprs)

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        if len(self._exprs) > 0:
            # noinspection PyShadowingNames
            def take_last_continuation(expr: LinkedList, amb: ambivalence.Amb) -> types.Promise:
                verify(amb)
                return lambda: ret(expr.last(), amb)

            return self._exprs.eval(env, take_last_continuation, amb)
        else:
            return lambda: ret(Nothing(), amb)

    @trace
    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        if len(self._exprs) > 0:
            self._exprs.prepare_analysis(env)
            these_types = self._exprs.map(lambda expr: expr.analyse_internal(env, non_generic))
            return these_types.last()
        else:
            return Nothing.type()

    @classmethod
    def hoist_loads(cls, exprs: LinkedList) -> LinkedList:
        """
        merges all load statements at this level into one
        load statement at the front of the list
        """
        load = [None]

        def hoist_recursive(lst: LinkedList, loaded: list) -> LinkedList:
            if isinstance(lst, Null):
                return lst
            elif isinstance(lst.car(), Load):
                if loaded[0] is None:
                    loaded[0] = lst.car()
                else:
                    loaded[0].merge(lst.car())
                return hoist_recursive(lst.cdr(), loaded)
            else:
                return Pair(lst.car(), hoist_recursive(lst.cdr(), loaded))

        new_list = hoist_recursive(exprs, load)
        if load[0] is None:
            return new_list
        else:
            return Pair(load[0], new_list)

    def get_exprs(self):
        return self._exprs

    def __str__(self) -> str:
        return self._exprs.qualified_str('{ ', ' ; ', ' }')


class Nest(Expr):
    def __init__(self, body: Sequence):
        self._body = body

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        """Evaluate the body in an extended environment
        """
        verify(amb)
        return self._body.eval(env.extend(), ret, amb)

    @trace
    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        new_env = env.extend()
        self._body.prepare_analysis(new_env)
        result = self._body.analyse_internal(new_env, non_generic.copy())
        if Config.hlDebug: new_env.dump()
        return result

    def __str__(self):
        return str(self._body)


class EnvironmentWrapper(Expr):
    """Wrapper for Environments to make them Exprs
    """

    def __init__(self, env: 'environment.Environment'):
        self._env = env

    def env(self):
        return self._env

    @trace
    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        return inference.EnvironmentType(env)


class Env(Expr):
    """Implements the 'env' construct

    1. extend the current or specified environment.
    2. evaluate the body in the new environment.
    3. return the new environment in an EnvironmentWrapper expression
    """

    def __init__(self, body: Sequence, package: LinkedList):
        self._body = body
        self._package = package

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        """evaluate the body in an extended env then return the extended env as the result
        """
        verify(amb)
        new_env = None

        def lookup_package(
                package: LinkedList,
                env: 'environment.Environment',
                ret: types.Continuation,
                amb: ambivalence.Amb
        ) -> types.Promise:
            verify(amb)
            if isinstance(package, Null):
                return lambda: ret(env, amb)
            else:
                def next_step(env: EnvironmentWrapper, amb: ambivalence.Amb) -> types.Promise:
                    verify(amb)
                    return lookup_package(package.cdr(), env.env(), ret, amb)
                return lambda: env.lookup(package.car(), next_step, amb)

        def after_eval(_: Expr, amb: ambivalence.Amb) -> types.Promise:
            verify(amb)
            nonlocal new_env
            return ret(EnvironmentWrapper(new_env), amb)

        def after_lookup(env: 'environment.Environment', amb: ambivalence.Amb) -> types.Promise:
            verify(amb)
            nonlocal new_env
            new_env = env.extend()
            return self._body.eval(new_env, after_eval, amb)

        return lookup_package(self._package, env, after_lookup, amb)

    @trace
    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        def lookup_env(package: LinkedList, env: inference.TypeEnvironment) -> inference.TypeEnvironment:
            if isinstance(package, Null):
                return env
            else:
                new_env = env[(package.car())].prune().env()
                if not isinstance(new_env, inference.TypeEnvironment):
                    raise PySchemeInferenceError(
                        str(package.car())
                        + " is not an environment, it is "
                        + str(type(new_env)))
                return lookup_env(package.cdr(), new_env)

        new_env = lookup_env(self._package, env).extend()
        self._body.analyse_internal(new_env, non_generic.copy())
        return inference.EnvironmentType(new_env)


class Definition(Expr):
    """
    The `define` statement
    """

    def __init__(self, symbol: Symbol, value: Expr):
        self._symbol = symbol
        self._value = value

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        def define_continuation(value: Expr, amb: ambivalence.Amb) -> types.Promise:
            verify(amb)
            def ret_nothing(_: Expr, amb: ambivalence.Amb) -> types.Promise:
                verify(amb)
                return lambda: ret(Nothing(), amb)

            return lambda: env.define(self._symbol, value, ret_nothing, amb, True)

        return lambda: self._value.eval(env, define_continuation, amb)

    def prepare_analysis(self, env: inference.TypeEnvironment):
        if env.noted_type_constructor(self._symbol):
            raise PySchemeInferenceError("attempt to override type constructor " + str(self._symbol))
        debug("pre-installing", self._symbol, "in", env)
        env.set_or_error(self._symbol, self._value.cursory_type())

    @trace
    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        defn_type = self._value.analyse_internal(env, non_generic)
        debug("unifying", self._symbol, "in", env)
        env[self._symbol].unify(defn_type)
        return Nothing.type()

    def __str__(self):
        return "define " + str(self._symbol) + " = " + str(self._value)


class EnvContext(Expr):
    """
    the '.' operator
    """

    def __init__(self, env: Expr, expr: Expr):
        self._env = env
        self._expr = expr

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        def env_continuation(new_env: EnvironmentWrapper, amb: ambivalence.Amb) -> types.Promise:
            verify(amb)
            return lambda: self._expr.eval(new_env.env(), ret, amb)

        return self._env.eval(env, env_continuation, amb)

    @trace
    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        lhs = self._env.analyse_internal(env, non_generic)
        if type(lhs) is inference.TypeVariable:
            raise MissingPrototypeError(self._env)
        return self._expr.analyse_internal(lhs.prune().env(), non_generic)

    def __str__(self):
        return str(self._env) + '.' + str(self._expr)

    __repr__ = __str__


class Op(Expr):
    """base class for operators
    """

    def apply(self, args: LinkedList, env: 'environment.Environment', ret: types.Continuation,
              amb: ambivalence.Amb) -> types.Promise:
        pass


class Primitive(Op):
    """primitive operators can have their arguments evaluated for them
    """

    def apply(self, args: LinkedList, env: 'environment.Environment', ret: types.Continuation,
              amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        def deferred_apply(evaluated_args: LinkedList, amb: ambivalence.Amb) -> types.Promise:
            verify(amb)
            return lambda: self.apply_evaluated_args(evaluated_args, ret, amb)

        return args.eval(env, deferred_apply, amb)

    def apply_evaluated_args(self, args, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        pass


class SpecialForm(Op):
    """special forms evaluate their own arguments
    """
    pass


class Closure(Primitive):
    """closures are created by evaluating a lambda (fn)
    """

    def __init__(self, args: LinkedList, body: Expr, env: 'environment.Environment'):
        self._args = args
        self._body = body
        self._env = env
        self.name = 'lambda'

    def set_name(self, name: str):
        self.name = name

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        hlDebug(self.name, args)
        formal_args = self._args
        actual_args = args
        dictionary = {}
        while type(formal_args) is not Null and type(actual_args) is not Null:
            farg = formal_args.car()
            if isinstance(farg, TypedSymbol):
                farg = farg.symbol()
            if not isinstance(farg, Wildcard):
                dictionary[farg] = actual_args.car()
            formal_args = formal_args.cdr()
            actual_args = actual_args.cdr()
        if type(formal_args) is not Null:  # currying
            return lambda: ret(Closure(formal_args, self._body, self._env.extend(dictionary)), amb)
        elif type(actual_args) is not Null:  # over-complete function application

            def re_apply_continuation(closure: Closure, amb: ambivalence.Amb) -> types.Promise:
                verify(amb)
                return lambda: closure.apply_evaluated_args(actual_args, ret, amb)

            return lambda: self._body.eval(self._env.extend(dictionary), re_apply_continuation, amb)
        else:  # formal and actual args match
            return lambda: self._body.eval(self._env.extend(dictionary), ret, amb)

    def num_args(self):
        return len(self._args)

    def __str__(self) -> str:
        return self.__class__.__name__ + "(" + str(self._args) + ": " + str(self._body) + ")"


class BinaryArithmetic(Primitive):
    """common base class for binary arithmetic operators.
    type is always `int -> int -> int`
    """

    @classmethod
    def type(cls):
        return inference.Function(
            Number.type(),
            inference.Function(Number.type(), Number.type())
        )

    def static_type(self) -> bool:
        return True


class Addition(BinaryArithmetic, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb):
        verify(amb)
        return lambda: ret(args[0] + args[1], amb)


class Subtraction(BinaryArithmetic, metaclass=Singleton):

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        # noinspection PyUnresolvedReferences
        return lambda: ret(args[0] - args[1], amb)


class Multiplication(BinaryArithmetic, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        # noinspection PyUnresolvedReferences
        verify(amb)
        return lambda: ret(args[0] * args[1], amb)


class Division(BinaryArithmetic, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        # noinspection PyUnresolvedReferences
        verify(amb)
        return lambda: ret(args[0] // args[1], amb)


class Modulus(BinaryArithmetic, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        # noinspection PyUnresolvedReferences
        verify(amb)
        return lambda: ret(args[0] % args[1], amb)


class Exponentiation(BinaryArithmetic, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        # noinspection PyUnresolvedReferences
        verify(amb)
        return lambda: ret(args[0] ** args[1], amb)


class BinaryComparison(Primitive):
    """base class for binary comparison operators.
    type is always `t -> t -> bool`
    """

    @classmethod
    def type(self):
        typeVar = inference.TypeVariable()
        return inference.Function(
            typeVar,
            inference.Function(typeVar, Boolean.type())
        )

    def static_type(self) -> bool:
        return True


class Equality(BinaryComparison, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        return lambda: ret(args[0].eq(args[1]), amb)


class GT(BinaryComparison, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        return lambda: ret(args[0].gt(args[1]), amb)


class LT(BinaryComparison, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        return lambda: ret(args[0].lt(args[1]), amb)


class GE(BinaryComparison, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        return lambda: ret(args[0].ge(args[1]), amb)


class LE(BinaryComparison, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        return lambda: ret(args[0].le(args[1]), amb)


class NE(BinaryComparison, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        return lambda: ret(args[0].ne(args[1]), amb)


class BinaryLogic(SpecialForm):
    """base class for binary boolean operators.
    type is always `bool -> bool -> bool`
    """

    @classmethod
    def type(cls):
        return inference.Function(
            Boolean.type(),
            inference.Function(Boolean.type(), Boolean.type())
        )

    def static_type(self) -> bool:
        return True


class And(BinaryLogic, metaclass=Singleton):

    def apply(self, args: LinkedList,
              env: 'environment.Environment',
              ret: types.Continuation,
              amb: ambivalence.Amb) -> types.Promise:
        verify(amb)

        def cont(lhs: Expr, amb: ambivalence.Amb) -> types.Promise:
            verify(amb)
            if lhs.is_true():
                return lambda: args[1].eval(env, ret, amb)
            elif lhs.is_false():
                return lambda: ret(lhs, amb)
            else:
                def cont2(rhs: Expr, amb: types.Continuation) -> types.Promise:
                    verify(amb)
                    if rhs.is_false():
                        return lambda: ret(rhs, amb)
                    else:
                        return lambda: ret(lhs, amb)

                return lambda: args[1].eval(env, cont2, amb)

        return lambda: args[0].eval(env, cont, amb)


class Or(BinaryLogic, metaclass=Singleton):

    def apply(self, args: LinkedList,
              env: 'environment.Environment',
              ret: types.Continuation,
              amb: ambivalence.Amb) -> types.Promise:
        verify(amb)

        def cont(lhs: Expr, amb: ambivalence.Amb) -> types.Promise:
            verify(amb)
            if lhs.is_true():
                return lambda: ret(lhs, amb)
            elif lhs.is_false():
                return lambda: args[1].eval(env, ret, amb)
            else:
                def cont2(rhs: Expr, amb: types.Continuation) -> types.Promise:
                    verify(amb)
                    if rhs.is_true():
                        return lambda: ret(rhs, amb)
                    else:
                        return lambda: ret(lhs, amb)

                return lambda: args[1].eval(env, cont2, amb)

        return lambda: args[0].eval(env, cont, amb)


class Xor(Primitive, metaclass=Singleton):
    @classmethod
    def type(cls):
        return BinaryLogic.type()

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        return lambda: ret(args[0] ^ args[1], amb)

    def static_type(self):
        return True


class Not(Primitive, metaclass=Singleton):
    @classmethod
    def type(cls):
        return inference.Function(Boolean.type(), Boolean.type())

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        return lambda: ret(~(args[0]), amb)

    def static_type(self) -> bool:
        return True


class Then(SpecialForm, metaclass=Singleton):
    """the `then` operator
    """

    @classmethod
    def type(cls):
        typevar = inference.TypeVariable()
        return inference.Function(
            typevar,
            inference.Function(typevar, typevar)
        )

    def apply(self, args: LinkedList,
              env: 'environment.Environment',
              ret: types.Continuation,
              amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        def amb2() -> types.Promise:
            return lambda: args[1].eval(env, ret, amb)

        return lambda: args[0].eval(env, ret, ambivalence.Amb(amb2, amb.cut()))

    def static_type(self) -> bool:
        return True


class Back(SpecialForm, metaclass=Singleton):
    """the `back` statement
    """

    @classmethod
    def type(cls):
        return inference.TypeVariable()

    def apply(self,
              args: LinkedList,
              env: 'environment.Environment',
              ret: types.Continuation,
              amb: ambivalence.Amb
    ) -> types.Promise:
        verify(amb)
        return amb

    def static_type(self) -> bool:
        return True


class Cons(Primitive, metaclass=Singleton):
    @classmethod
    def type(cls):
        '#t -> list(#t) -> list(#t)'
        t = inference.TypeVariable()
        list_t = inference.TypeOperator('list', t)
        return inference.Function(t, inference.Function(list_t, list_t))

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        return lambda: ret(Pair(args[0], args[1]), amb)

    def static_type(self) -> bool:
        return True


class Append(Primitive, metaclass=Singleton):
    @classmethod
    def type(cls):
        'list(#t) -> list(#t) -> list(#t)'
        list_t = Null.type()
        return inference.Function(list_t, inference.Function(list_t, list_t))

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        return lambda: ret(args[0].append(args[1]), amb)

    def static_type(self) -> bool:
        return True


class Head(Primitive, metaclass=Singleton):
    @classmethod
    def type(cls):
        'list(#t) -> #t'
        t = inference.TypeVariable()
        list_t = inference.TypeOperator('list', t)
        return inference.Function(list_t, t)

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        return lambda: ret(args[0].car(), amb)

    def static_type(self) -> bool:
        return True


class Tail(Primitive, metaclass=Singleton):
    @classmethod
    def type(cls):
        'list(#t) -> list(#t)'
        list_t = Null.type()
        return inference.Function(list_t, list_t)

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        return lambda: ret(args[0].cdr(), amb)

    def static_type(self) -> bool:
        return True


class Length(Primitive, metaclass=Singleton):
    @classmethod
    def type(cls):
        'list(#t) -> int'
        return inference.Function(Null.type(), Number.type())

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        return lambda: ret(Number(len(args[0])), amb)

    def static_type(self) -> bool:
        return True


class Print(Primitive):
    @classmethod
    def type(cls):
        'string -> string'
        return inference.Function(
            LinkedList.type(Char.type()),
            LinkedList.type(Char.type())
        )

    def __init__(self, output):
        self._output = output

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        self._output.write(str(args[0]))
        self._output.write("\n")
        return lambda: ret(args, amb)

    def static_type(self) -> bool:
        return True


class Cont(Primitive):
    """wrapper for the continuation passed by `here` (CallCC)
    """

    @classmethod
    def type(cls):
        '#t'
        return inference.TypeVariable()

    def __init__(self, ret: callable):
        self._ret = ret

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        return lambda: self._ret(args[0], amb)

    def static_type(self) -> bool:
        return True


class CallCC(SpecialForm, metaclass=Singleton):
    """The `here` function
    """

    @classmethod
    def type(cls):
        '(#t -> #u) -> #u'
        t = inference.TypeVariable()
        u = inference.TypeVariable()
        return inference.Function(
            inference.Function(t, u),
            u
        )

    def apply(self,
              args: LinkedList,
              env: 'environment.Environment',
              ret: types.Continuation,
              amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        def do_apply(closure: Closure, amb: ambivalence.Amb) -> types.Promise:
            verify(amb)
            return lambda: closure.apply(LinkedList.list([Cont(ret)]), env, ret, amb)

        return args[0].eval(env, do_apply, amb)

    def static_type(self) -> bool:
        return True


class Exit(Primitive):
    @classmethod
    def type(cls):
        '#t'
        return inference.TypeVariable()

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        return None

    def static_type(self) -> bool:
        return True


class Spawn(Primitive):
    @classmethod
    def type(cls):
        return Boolean.type()

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        return [lambda: ret(T(), amb), lambda: ret(F(), amb)]

    def static_type(self) -> bool:
        return True


class Error(SpecialForm):
    @classmethod
    def type(cls):
        '#t'
        return inference.TypeVariable()

    def __init__(self, cont):
        self.cont = cont

    def apply(self,
              args: LinkedList,
              env: 'environment.Environment',
              ret: types.Continuation,
              amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        def print_continuation(printer: Print, amb: ambivalence.Amb) -> types.Promise:
            verify(amb)
            return lambda: printer.apply(args, env, self.cont, amb)

        return env.lookup(Symbol("print"), print_continuation, amb)

    def static_type(self) -> bool:
        return True


class TypeSystem(Expr):
    """
    classes in this group have specific behaviour and constitute the components of a typedef statement.
    Plan:
        1. prepare_analysis of the typedefs creates the type definitions
           for the type constructors in the current type environment
        2. evaluation of the typedef creates the actual type constructor
           functions in the current execution environment
    """
    pass


class FlatType(TypeSystem):
    """
    represents the type being defined in a typedef statement
    """

    def __init__(self, symbol: Symbol, type_components: LinkedList):
        self.symbol = symbol
        self.type_components = type_components

    def make_type(self, env: inference.TypeEnvironment, non_generic: set):
        types = []
        for var in self.type_components:
            env[var] = inference.TypeVariable()
            types += [env[var]]
            non_generic.add(env[var])
        return inference.TypeOperator(self.symbol.value(), *types)

    def __str__(self):
        if type(self.type_components) is Null:
            return str(self.symbol)
        else:
            return str(self.symbol) + str(self.type_components)


class TypeDef(TypeSystem):
    """
    represents a typedef statement
    """

    def __init__(self, flat_type: FlatType, constructors: LinkedList):
        self.flat_type = flat_type
        self.constructors = constructors

    def prepare_analysis(self, env: inference.TypeEnvironment):
        env[self.flat_type.symbol] = inference.TypeVariable()
        self.constructors.prepare_analysis(env)

    @trace
    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set):
        new_env = env.extend()
        new_non_generic = non_generic.copy()
        return_type = self.flat_type.make_type(new_env, new_non_generic)
        # we may be looked up as a type variable if there are no argument types
        env[self.flat_type.symbol].unify(return_type)
        for constructor in self.constructors:
            debug("unifying", constructor.name, "in", env)
            env[constructor.name].unify(constructor.make_type(new_env, return_type, new_non_generic))
            env.note_type_constructor(constructor.name)
        return return_type

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        return self.constructors.eval(env, lambda _, amb: ret(Nothing(), amb), amb)

    def __str__(self):
        return "typedef(" + str(self.flat_type) + " : " + str(self.constructors) + ")"


class TypeConstructor(TypeSystem):
    """
    represents a type constructor definition in the body
    of a typedef
    """

    def __init__(self, name: Symbol, arg_types: LinkedList):
        self.name = name
        self.arg_types = arg_types

    def prepare_analysis(self, env: inference.TypeEnvironment):
        if env.noted_type_constructor(self.name):
            raise PySchemeInferenceError("attempt to override type constructor " + str(self.name))
        debug("pre-installing", self.name, "in", env)
        env[self.name] = inference.TypeVariable()

    def make_type(self, env: inference.TypeEnvironment, return_type: inference.Type,
                  non_generic: set) -> inference.Type:
        """
        We are given a return type, plus an environment where our argument type variables are defined
        """

        def make_type_recursive(arg_types: LinkedList) -> inference.Type:
            if type(arg_types) is Null:
                return return_type
            else:
                return inference.Function(
                    arg_types.car().make_type(env, non_generic),
                    make_type_recursive(arg_types.cdr())
                )

        return make_type_recursive(self.arg_types)

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        if len(self.arg_types) == 0:
            return lambda: env.define(self.name, NamedTuple(self.name, Null()), ret, amb)
        else:
            def make_args(num: int):
                if num == 0:
                    return Null()
                else:
                    return Pair(Symbol.generate(), make_args(num - 1))

            args = make_args(len(self.arg_types))

            def make_closure() -> Closure:
                closure = Closure(
                    args,
                    Application(
                        TupleConstructor(self.name, len(self.arg_types)),
                        args
                    ),
                    env
                )
                closure.set_name('*' + str(self.name))
                return closure

            return lambda: env.define(self.name, make_closure(), ret, amb)

    def __str__(self):
        if type(self.arg_types) is Null:
            return str(self.name)
        else:
            return str(self.name) + str(self.arg_types)

    __repr__ = __str__


class Prototype(TypeSystem):
    """
    A prototype declaration of an environment type
    """
    def __init__(self, name: Symbol, components: Sequence):
        self.name = name
        self.components = components

    @trace
    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        new_env = env.extend()
        self.components.analyse_internal(new_env, non_generic.copy())
        val = inference.PrototypeType(new_env)
        env[self.name] = val
        return val

    def __str__(self):
        return "prototype " + str(self.name) + ' ' + str(self.components)

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: ambivalence.Amb):
        verify(amb)
        return lambda: ret(Nothing(), amb)

    __repr__ = __str__


class PrototypeComponent(TypeSystem):
    """
    a component of a prototype, i.e. "name: type"
    """
    def __init__(self, name: Symbol, type: 'Type'):
        self.name = name
        self.type = type

    @trace
    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        env[self.name] = self.type.make_type(env.extend(), non_generic)
        return env[self.name]

    def __str__(self):
        return str(self.name) + ' : ' + str(self.type)

    __repr__ = __str__


class Type(TypeSystem):
    """
    represents a type as argument to a type constructor
    in the body of a typedef
    """
    def __init__(self, name: Symbol, components: LinkedList):
        self.name = name
        self.components = components

    def make_type(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        # self is either a type variable or a concrete type, predefined or typedef'd
        # possibly even the type currently being defined.
        components = self.components.map(lambda component: component.make_type(env, non_generic))
        if type(components) is Null:
            # default just looks up in env, either a type var or a typedef
            return self.get_or_make_type(env)
        else:
            # necessary because this may be a recursive use of the type
            # being defined, and the types of the components in the usage
            # may be more restrictive than the types of our components
            # in the type being defined, so we can't just do a lookup
            # on self.name, we have to unify with that.
            return inference.TypeOperator(self.name.value(), *components)

    def get_or_make_type(self, env):
        return env[self.name]

    def __str__(self):
        if str(self.name).isalnum():
            return str(self.name) + ('' if type(self.components) is Null else str(self.components))
        else:  # looks like an op
            num_components = len(self.components)
            if num_components == 2:
                return '(' + str(self.components[0]) + ' ' + str(self.name) + ' ' + str(self.components[1]) + ')'
            else:
                return str(self.name) + ('' if num_components == 0 else str(self.components))

    __repr__ = __str__


class TypeVar(Type):
    def __init__(self, name: Symbol):
        super(TypeVar, self).__init__(name, Null())

    def get_or_make_type(self, env):
        if self.name not in env:
            env[self.name] = inference.TypeVariable()
        return env[self.name]


class TupleConstructor(Primitive):
    """
    TupleConstructor is to TypeDef what Closure is to Lambda,
    it's a function of n arguments that returns a Compound Data Structure
    """

    def __init__(self, name: Symbol, num_args: int):
        self.name = name
        self.num_args = num_args

    def apply_evaluated_args(self, args, ret: types.Continuation, amb: ambivalence.Amb):
        verify(amb)
        return lambda: ret(NamedTuple(self.name, args), amb)

    def __str__(self):
        return "(TupleConstructor " + str(self.name) + ")"


class NamedTuple(Expr):
    def __init__(self, name: Symbol, values: LinkedList):
        self.name = name
        self.values = values

    def analyse_farg(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        final_type = inference.TypeVariable()

        def analyse_values(values: LinkedList) -> inference.Type:
            if type(values) is Null:
                return final_type
            else:
                return inference.Function(
                    values.car().analyse_farg(env, non_generic),
                    analyse_values(values.cdr())
                )

        our_fn = analyse_values(self.values)
        env[self.name].fresh(non_generic).unify(our_fn)
        return final_type

    def match(self, other: 'NamedTuple', env: 'environment.Environment', ret: types.Continuation,
              amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        if self.name == other.name:
            return lambda: self.values.match(other.values, env, ret, amb)
        else:
            return lambda: amb()

    def __str__(self):
        if type(self.values) is Null:
            return str(self.name)
        else:
            return str(self.name) + str(self.values)

    __repr__ = __str__

    def __cmp__(self, other: 'NamedTuple'):
        return self.name.__cmp__(other.name) or self.values.__cmp__(other.values)

    def __eq__(self, other: 'NamedTuple'):
        return self.name == other.name and self.values == other.values


class Composite(Primitive):
    """
    represents the combined body of a composite function
    """

    def __init__(self, components: LinkedList):
        self.components = components
        self.name = 'anon'

    def set_name(self, name: str):
        self.name = name

    def __str__(self):
        return "fn " + self.components.qualified_str('{', ' ', '}')

    @trace
    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set):
        last_type = None
        for component in self.components:
            this_type = component.analyse_internal(env, non_generic)
            if last_type is not None:
                this_type.unify(last_type)
            last_type = this_type
        return last_type

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        if self.has_no_args():
            return lambda: self.default_body().eval(env, ret, amb)

        def post_eval_continuation(evaluated_components, amb) -> types.Promise:
            verify(amb)
            closure = CompositeClosure(evaluated_components)
            closure.set_name(self.name)
            return lambda: ret(closure, amb)

        return lambda: self.components.eval(env, post_eval_continuation, amb)

    def has_no_args(self):
        return len(self.components) == 0 or self.components[0].num_args() == 0

    def default_body(self):
        if len(self.components) == 0:
            return Nothing()
        else:
            return self.components[0]._body


class ComponentLambda(Lambda):
    """
    represents a single sub-function in a composite function body
    """

    def closure(self, args: LinkedList, body: Expr, env: 'environment.Environment') -> Closure:
        """
        overrides Lambda.closure
        """
        return ComponentClosure(args, body, env)


class CompositeClosure(Closure):
    """
    type of closure resulting from evaluation of a Composite
    """

    def __init__(self, components: LinkedList):
        self.components = components
        self.name = 'unknown'

    def set_name(self, name: str):
        self.name = name

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb):
        verify(amb)
        hlDebug(self.name, args)
        if len(args) < self.num_args():

            def try_recursive(
                    components: LinkedList,
                    result: LinkedList,
                    ret: types.Continuation,
                    amb: ambivalence.Amb) -> types.Promise:
                verify(amb)
                if type(components) is Null:
                    return lambda: ret(result, amb)
                else:
                    def amb2() -> types.Promise:
                        return lambda: try_recursive(components.cdr(), result, ret, amb)

                    def ret2(val, amb: ambivalence.Amb) -> types.Promise:
                        verify(amb)
                        return lambda: try_recursive(components.cdr(), Pair(val, result), ret, amb)

                    return lambda: components.car().apply_evaluated_args(args, ret2, ambivalence.Amb(amb2, amb.cut()))

            def collect_successes(successes: LinkedList, amb: ambivalence.Amb) -> types.Promise:
                verify(amb)
                if isinstance(successes, Null):
                    return amb
                else:
                    return ret(CompositeClosure(successes), amb)

            return try_recursive(self.components, Null(), collect_successes, amb)

        else:
            def try_recursive(components: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
                verify(amb)
                if type(components) is Null:
                    return amb
                else:
                    def amb2() -> types.Promise:
                        return lambda: try_recursive(components.cdr(), ret, amb)

                    return lambda: components.car().apply_evaluated_args(args, ret, ambivalence.Amb(amb2, amb.cut()))

            return try_recursive(self.components, ret, amb.cut_point())

    def num_args(self):
        if isinstance(self.components, Null):
            return 0
        else:
            return self.components.car().num_args()

    def __str__(self):
        return 'CompositeClosure{' + str(self.components) + '}'


class ComponentClosure(Closure):
    """
    type of closure resulting from the evaluation of a ComponentLambda
    """

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        new_env = self._env.extend()

        def apply_evaluated_recursive(
                fargs: LinkedList,
                aargs: LinkedList,
                ret: types.Continuation,
                amb: ambivalence.Amb
        ) -> types.Promise:
            verify(amb)
            if type(fargs) is Null and type(aargs) is Null:
                return lambda: self._body.eval(new_env, ret, ambivalence.Amb(amb.cut()))
            elif type(fargs) is Null:  # over-application
                def re_apply_continuation(closure: Closure, amb: ambivalence.Amb) -> types.Promise:
                    return lambda: closure.apply_evaluated_args(aargs, ret, amb)

                return lambda: self._body.eval(new_env, re_apply_continuation, ambivalence.Amb(amb.cut()))
            elif type(aargs) is Null:  # currying
                return lambda: ret(ComponentClosure(fargs, self._body, new_env), amb)
            else:
                def next_continuation(_, amb) -> types.Promise:
                    return lambda: apply_evaluated_recursive(fargs.cdr(), aargs.cdr(), ret, amb)

                return lambda: fargs.car().match(aargs.car(), new_env, next_continuation, amb)

        return apply_evaluated_recursive(self._args, args, ret, amb)


class NothingType(Type):
    def __init__(self):
        Type.__init__(self, Symbol("nothing"), Null())

    def get_or_make_type(self, env):
        return Nothing.type()


class ListType(Type):
    def __init__(self, components: LinkedList):
        Type.__init__(self, Symbol("list"), components)


class IntType(Type):
    def __init__(self):
        Type.__init__(self, Symbol("int"), Null())

    def get_or_make_type(self, env):
        return Number.type()


class CharType(Type):
    def __init__(self):
        Type.__init__(self, Symbol("char"), Null())

    def get_or_make_type(self, env):
        return Char.type()


class BoolType(Type):
    def __init__(self):
        Type.__init__(self, Symbol("bool"), Null())

    def get_or_make_type(self, env):
        return Boolean.type()


class Load(Expr):
    """
    conceptually:
    load a.b.c
        define a = env { define b = env { define c = env extends globalenv { "content of ./a/b/c.fn" } } }
    load a.b.c as d
        define d = env { define b = env { define c = env extends globalenv { "content of ./a/b/c.fn" } } }.b.c
    load a as b
        define b = env extends globalenv { "content of ./a.fn" }

    however, it's more complicated than that:

    load a.b.c
    load a.b.d as d
        define a = env { define b = env { define c = env extends globalenv { "content of ./a/b/c.fn" };
                                          define d = env extends globalenv { "content of ./a/b/d.fn" } } }
        define d = a.b.d;
    """
    loaded_packages = {}

    def __init__(self, package: LinkedList, alias: Symbol, get_reader: callable):
        self.packages = [package]
        self.aliases = {}
        if not isinstance(alias, Null):
            self.aliases[alias] = package
        self.wrapper = None
        self.current = {}
        if not self.loaded(package):
            self.load(package, get_reader)
        self.note_current_load(package)

    def merge(self, other):
        self.merge_packages(other)
        self.merge_aliases(other)
        self.merge_current(other)

    def merge_packages(self, other: 'Load'):
        self.packages += other.packages

    def merge_aliases(self, other: 'Load'):
        for alias in other.aliases.keys():
            self.aliases[alias] = other.aliases[alias]

    def merge_current(self, other: 'Load'):
        def merge_recursive(a: dict, b: dict):
            if isinstance(a, dict):
                for key in b.keys():
                    if key in a:
                        merge_recursive(a[key], b[key])
                    else:
                        a[key] = b[key]

        merge_recursive(self.current, other.current)

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: ambivalence.Amb) -> types.Promise:
        verify(amb)
        return lambda: self.make_wrapper().eval(env, ret, amb)

    def note_current_load(self, package: LinkedList):
        def note_recursive(package: LinkedList, dictionary: dict):
            if isinstance(package.cdr(), Null):
                dictionary[package.car()] = self.file_name(package)
            else:
                if package.car() not in dictionary:
                    dictionary[package.car()] = {}
                note_recursive(package.cdr(), dictionary[package.car()])

        note_recursive(package, self.current)

    def make_wrapper(self):
        if self.wrapper is None:
            def convert_current_to_environments(current: dict, path: list) -> Sequence:
                if isinstance(current, dict):
                    definitions = []
                    for component in current.keys():
                        definitions += [
                            Definition(
                                component,
                                Env(
                                    convert_current_to_environments(current[component], path + [component]),
                                    Pair(Symbol("globalenv"), Null())
                                )
                            )
                        ]
                    return Sequence(LinkedList.list(definitions))
                else:
                    return self.get_content(path[:-1] + [current])

            def convert_path_to_env_access(path: LinkedList, result) -> Union[Symbol, EnvContext]:
                if isinstance(path, Null):
                    return result
                else:
                    return convert_path_to_env_access(path.cdr(), EnvContext(result, path.car()))

            environments = convert_current_to_environments(self.current, [])
            alias_definitions = []
            for alias in self.aliases.keys():
                alias_definitions += [
                    Definition(
                        alias,
                        convert_path_to_env_access(
                            self.aliases[alias].cdr(),
                            self.aliases[alias].car()
                        )
                    )
                ]

            if len(alias_definitions) > 0:
                environments = Sequence(
                    environments.get_exprs().append(LinkedList.list(alias_definitions))
                )

            self.wrapper = environments

        return self.wrapper

    @classmethod
    def get_content(cls, path: list) -> Sequence:
        def get_content_recursive(package: LinkedList, packages: Union[dict, Sequence]) -> Sequence:
            if isinstance(package.cdr(), Null):
                return packages[package.car()]
            else:
                return get_content_recursive(package.cdr(), packages[package.car()])

        return get_content_recursive(LinkedList.list(path), Load.loaded_packages)

    @classmethod
    def file_name(cls, pair: LinkedList) -> Symbol:
        return Symbol(str(pair.car()) + ".fn")

    def loaded(self, package: LinkedList) -> bool:
        def recursive_check(pkg: LinkedList, packages: dict) -> bool:
            if isinstance(pkg.cdr(), Null):
                file = self.file_name(pkg)
                return file in packages
            elif pkg.car() in packages:
                return recursive_check(pkg.cdr(), packages[pkg.car()])
            else:
                return False

        return recursive_check(package, Load.loaded_packages)

    def load(self, package: LinkedList, get_reader: callable):
        path = self.get_data_dir().joinpath(self.make_path(package))
        if path.is_file():
            contents = []
            with path.open() as fh:
                reader = get_reader(fh)
                while True:
                    parsed_expr = reader.read()
                    if parsed_expr is None:
                            break
                    contents += [parsed_expr]

            def recursive_set(pkg: LinkedList, packages: dict):
                if isinstance(pkg.cdr(), Null):
                    file = self.file_name(pkg)
                    packages[file] = Sequence(LinkedList.list(contents))
                else:
                    if pkg.car() not in packages:
                        packages[pkg.car()] = {}
                    recursive_set(pkg.cdr(), packages[pkg.car()])
            recursive_set(package, Load.loaded_packages)
        else:
            raise FileNotFoundError(str(path))

    @classmethod
    def make_path(cls, package: LinkedList) -> Path:
        return Path(package.qualified_str('', '/', '.fn'))

    def prepare_analysis(self, env: inference.TypeEnvironment):
        self.make_wrapper().prepare_analysis(env)

    @trace
    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set):
        return self.make_wrapper().analyse_internal(env, non_generic)

    # this is just a stopgap while testing
    def get_data_dir(self) -> Path:
        return Path(self.get_script_dir()).parent.joinpath(Path('data'))

    def get_script_dir(self, follow_symlinks=True):
        if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
            path = os.path.abspath(sys.executable)
        else:
            path = inspect.getabsfile(self.get_script_dir)
        if follow_symlinks:
            path = os.path.realpath(path)
        return os.path.dirname(path)
