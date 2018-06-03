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
from .exceptions import NonBooleanExpressionError, PySchemeInternalError, MissingPrototypeError, PySchemeInferenceError
from .singleton import Singleton, FlyWeight
from . import types
from . import inference


def debug(*args, **kwargs):
    if Config.debug:
        print(*args, **kwargs)


class Config:
    debug = False


class Expr:
    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return lambda: ret(self, amb)

    def apply(self,
              args: 'LinkedList',
              env: 'environment.Environment',
              ret: types.Continuation,
              amb: types.Amb) -> types.Promise:
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
              amb: types.Amb) -> types.Promise:
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

    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        return self.type()

    def static_type(self) -> bool:
        return False

    def __cmp__(self, other):
        raise PySchemeInternalError(self.__class__.__name__ + " objects are not comparable")

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


class Nothing(Expr, metaclass=Singleton):
    """
    analogous to Python's 'None'
    """

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
              amb: types.Amb) -> types.Promise:
        if self == other:
            return lambda: ret(self, amb)
        else:
            return lambda: amb()

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
    counter = 1

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return lambda: env.lookup(self, ret, amb)

    def match(self, other: 'Expr', env: 'environment.Environment', ret: types.Continuation,
              amb: types.Amb) -> types.Promise:
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

    @classmethod
    def generate(cls):
        name = ''
        counter = cls.counter
        while counter > 0:
            remainder = counter % 26
            name += chr(ord('a') + remainder)
            counter = counter // 26
        cls.counter += 1
        return cls('#' + name)


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
        symbol = self.symbol()
        arg_type = env[self.type_symbol()]
        env[symbol] = arg_type
        non_generic.add(arg_type)
        return arg_type

    __repr__ = __str__


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
            return self.qualified_repr('[', ', ', ']')

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

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: types.Amb) -> types.Promise:
        # noinspection PyShadowingNames
        def car_continuation(evaluated_car: Expr, amb: types.Amb) -> types.Promise:
            # noinspection PyShadowingNames
            def cdr_continuation(evaluated_cdr: LinkedList, amb: types.Amb) -> types.Promise:
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
              amb: types.Amb) -> types.Promise:
        # noinspection PyShadowingNames
        def car_continuation(_, amb) -> types.Promise:
            return lambda: self.cdr().match(other.cdr(), env, ret, amb)

        return lambda: self.car().match(other.car(), env, car_continuation, amb)

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

        def analyse_recursive(pair: Pair) -> inference.Type:
            if isinstance(pair, Null):
                result_type = Pair.type(type_so_far)
                result_type.unify(Null.type())
                return result_type  # list of something
            elif isinstance(pair, Symbol):
                result_type = Pair.type(type_so_far)
                env[pair] = result_type
                return result_type
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
        return self

    def cdr(self) -> LinkedList:
        return self

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
              amb: types.Amb) -> types.Promise:
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

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: types.Amb) -> types.Promise:
        # noinspection PyShadowingNames
        def test_continuation(result: Expr, amb: types.Amb) -> types.Promise:
            if result.is_true():
                return lambda: self._consequent.eval(env, ret, amb)
            else:
                return lambda: self._alternative.eval(env, ret, amb)

        return self._test.eval(env, test_continuation, amb)

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

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: types.Amb) -> types.Promise:
        if len(self._args) == 0:
            return lambda: self._body.eval(env, ret, amb)  # conform to type-checker's expectations
        else:
            return lambda: ret(self.closure(self._args, self._body, env), amb)

    def closure(self, args: LinkedList, body: Expr, env: 'environment.Environment') -> 'Closure':
        """
        intended to be overridden by i.e. ComponentLambda
        """
        return Closure(args, body, env)

    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set):
        new_env = env.extend()
        new_non_generic = non_generic.copy()

        def analyse_recursive(args: LinkedList) -> inference.Type:
            if type(args) is Null:
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

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: types.Amb) -> types.Promise:

        # noinspection PyShadowingNames
        def evaluated_op_continuation(evaluated_op: 'Op', amb: types.Amb) -> types.Promise:
            return lambda: evaluated_op.apply(self._operands, env, ret, amb)

        return self._operation.eval(env, evaluated_op_continuation, amb)

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
        return str(self._operation) + str(self._operands)

    __repr__ = __str__


class Sequence(Expr):
    def __init__(self, exprs: LinkedList):
        self._exprs = exprs

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: types.Amb) -> types.Promise:
        # noinspection PyShadowingNames
        def take_last_continuation(expr: LinkedList, amb: types.Amb) -> types.Promise:
            return lambda: ret(expr.last(), amb)

        return self._exprs.eval(env, take_last_continuation, amb)

    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        if len(self._exprs) > 0:
            self._exprs.prepare_analysis(env)
            these_types = self._exprs.map(lambda expr: expr.analyse_internal(env, non_generic))
            return these_types.last()
        else:
            return Null.type()

    def __str__(self) -> str:
        return self._exprs.qualified_str('{ ', ' ; ', ' }')


class Nest(Expr):
    def __init__(self, body: Sequence):
        self._body = body

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: types.Amb) -> types.Promise:
        """Evaluate the body in an extended environment
        """
        return self._body.eval(env.extend(), ret, amb)

    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        new_env = env.extend()
        self._body.prepare_analysis(new_env)
        return self._body.analyse_internal(new_env, non_generic.copy())

    def __str__(self):
        return str(self._body)


class EnvironmentWrapper(Expr):
    """Wrapper for Environments to make them Exprs
    """

    def __init__(self, env: 'environment.Environment'):
        self._env = env

    def env(self):
        return self._env

    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        return inference.EnvironmentType(env)


class Env(Expr):
    """Implements the 'env' construct
    """

    def __init__(self, body: Sequence):
        self._body = body

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: types.Amb) -> types.Promise:
        """evaluate the body in an extended env then return the extended env as the result
        """
        new_env = env.extend()

        def eval_continuation(val: Expr, amb: types.Amb) -> types.Promise:
            return ret(EnvironmentWrapper(new_env), amb)

        return self._body.eval(new_env, eval_continuation, amb)

    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        new_env = env.extend()
        self._body.analyse_internal(new_env, non_generic.copy())
        return inference.EnvironmentType(new_env)


class Definition(Expr):
    """
    The `define` statement
    """

    def __init__(self, symbol: Symbol, value: Expr):
        self._symbol = symbol
        self._value = value

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: types.Amb) -> types.Promise:
        def define_continuation(value: Expr, amb: types.Amb) -> types.Promise:
            def ret_nothing(_: Expr, amb: types.Amb) -> types.Promise:
                return lambda: ret(Nothing(), amb)

            return lambda: env.define(self._symbol, value, ret_nothing, amb)

        return lambda: self._value.eval(env, define_continuation, amb)

    def prepare_analysis(self, env: inference.TypeEnvironment):
        if env.noted_type_constructor(self._symbol):
            raise PySchemeInferenceError("attempt to override type constructor " + str(self._symbol))
        env[self._symbol] = inference.TypeVariable()

    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        defn_type = self._value.analyse_internal(env, non_generic)
        env[self._symbol].unify(defn_type)
        return env[self._symbol]

    def __str__(self):
        return "define " + str(self._symbol) + " = " + str(self._value)


class EnvContext(Expr):
    """
    the '.' operator
    """

    def __init__(self, env: Expr, expr: Expr):
        self._env = env
        self._expr = expr

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: types.Amb) -> types.Promise:
        def env_continuation(new_env: EnvironmentWrapper, amb: types.Amb) -> types.Promise:
            return lambda: self._expr.eval(new_env.env(), ret, amb)

        return self._env.eval(env, env_continuation, amb)

    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set) -> inference.Type:
        lhs = self._env.analyse_internal(env, non_generic)
        if type(lhs) is inference.TypeVariable:
            raise MissingPrototypeError(self._env)
        return self._expr.analyse_internal(lhs.prune().env(), non_generic)


class Op(Expr):
    """base class for operators
    """

    def apply(self, args: LinkedList, env: 'environment.Environment', ret: types.Continuation,
              amb: types.Amb) -> types.Promise:
        pass


class Primitive(Op):
    """primitive operators can have their arguments evaluated for them
    """

    def apply(self, args: LinkedList, env: 'environment.Environment', ret: types.Continuation,
              amb: types.Amb) -> types.Promise:
        def deferred_apply(evaluated_args: LinkedList, amb: types.Amb) -> types.Promise:
            return lambda: self.apply_evaluated_args(evaluated_args, ret, amb)

        return args.eval(env, deferred_apply, amb)

    def apply_evaluated_args(self, args, ret: types.Continuation, amb: types.Amb) -> types.Promise:
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

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        formal_args = self._args
        actual_args = args
        dictionary = {}
        while type(formal_args) is not Null and type(actual_args) is not Null:
            farg = formal_args.car()
            if type(farg) is TypedSymbol:
                farg = farg.symbol()
            dictionary[farg] = actual_args.car()
            formal_args = formal_args.cdr()
            actual_args = actual_args.cdr()
        if type(formal_args) is not Null:  # currying
            return lambda: ret(Closure(formal_args, self._body, self._env.extend(dictionary)), amb)
        elif type(actual_args) is not Null:  # over-complete function application

            def re_apply_continuation(closure: Closure, amb: types.Amb) -> types.Promise:
                return lambda: closure.apply_evaluated_args(actual_args, ret, amb)

            return lambda: self._body.eval(self._env.extend(dictionary), re_apply_continuation, amb)
        else:  # formal and actual args match
            return lambda: self._body.eval(self._env.extend(dictionary), ret, amb)

    def __str__(self) -> str:
        return self.__class__.__name__ + "(" + str(self._args) + ": " + str(self._body) + ")"


class BinaryArithmetic(Primitive):
    """common base class for binary arithmetic operators.
    type is always `int -> int -> int`
    """

    @classmethod
    def type(self):
        return inference.Function(
            Number.type(),
            inference.Function(Number.type(), Number.type())
        )

    def static_type(self) -> bool:
        return True


class Addition(BinaryArithmetic, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb):
        return lambda: ret(args[0] + args[1], amb)


class Subtraction(BinaryArithmetic, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return lambda: ret(args[0] - args[1], amb)


class Multiplication(BinaryArithmetic, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return lambda: ret(args[0] * args[1], amb)


class Division(BinaryArithmetic, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return lambda: ret(args[0] // args[1], amb)


class Modulus(BinaryArithmetic, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return lambda: ret(args[0] % args[1], amb)


class Exponentiation(BinaryArithmetic, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
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
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return lambda: ret(args[0].eq(args[1]), amb)


class GT(BinaryComparison, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return lambda: ret(args[0].gt(args[1]), amb)


class LT(BinaryComparison, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return lambda: ret(args[0].lt(args[1]), amb)


class GE(BinaryComparison, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return lambda: ret(args[0].ge(args[1]), amb)


class LE(BinaryComparison, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return lambda: ret(args[0].le(args[1]), amb)


class NE(BinaryComparison, metaclass=Singleton):
    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return lambda: ret(args[0].ne(args[1]), amb)


class BinaryLogic(SpecialForm):
    """base class for binary boolean operators.
    type is always `bool -> bool -> bool`
    """

    @classmethod
    def type(self):
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
              amb: types.Amb) -> types.Promise:

        def cont(lhs: Expr, amb: types.Amb) -> types.Promise:
            if lhs.is_true():
                return lambda: args[1].eval(env, ret, amb)
            elif lhs.is_false():
                return lambda: ret(lhs, amb)
            else:
                def cont2(rhs: Expr, amb: types.Continuation) -> types.Promise:
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
              amb: types.Amb) -> types.Promise:

        def cont(lhs: Expr, amb: types.Amb) -> types.Promise:
            if lhs.is_true():
                return lambda: ret(lhs, amb)
            elif lhs.is_false():
                return lambda: args[1].eval(env, ret, amb)
            else:
                def cont2(rhs: Expr, amb: types.Continuation) -> types.Promise:
                    if rhs.is_true():
                        return lambda: ret(rhs, amb)
                    else:
                        return lambda: ret(lhs, amb)

                return lambda: args[1].eval(env, cont2, amb)

        return lambda: args[0].eval(env, cont, amb)


class Xor(Primitive, metaclass=Singleton):
    @classmethod
    def type(self):
        return BinaryLogic.type()

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return lambda: ret(args[0] ^ args[1], amb)

    def static_type(self):
        return True


class Not(Primitive, metaclass=Singleton):
    @classmethod
    def type(self):
        return inference.Function(Boolean.type(), Boolean.type())

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return lambda: ret(~(args[0]), amb)

    def static_type(self) -> bool:
        return True


class Then(SpecialForm, metaclass=Singleton):
    """the `then` operator
    """

    @classmethod
    def type(self):
        typevar = inference.TypeVariable()
        return inference.Function(
            typevar,
            inference.Function(typevar, typevar)
        )

    def apply(self, args: LinkedList,
              env: 'environment.Environment',
              ret: types.Continuation,
              amb: types.Amb) -> types.Promise:
        def amb2() -> types.Promise:
            return lambda: args[1].eval(env, ret, amb)

        return lambda: args[0].eval(env, ret, amb2)

    def static_type(self) -> bool:
        return True


class Back(SpecialForm, metaclass=Singleton):
    """the `back` statement
    """

    @classmethod
    def type(self):
        return inference.TypeVariable()

    def apply(self,
              args: LinkedList,
              env: 'environment.Environment',
              ret: types.Continuation,
              amb: types.Amb) -> types.Promise:
        return lambda: amb()

    def static_type(self) -> bool:
        return True


class Cons(Primitive, metaclass=Singleton):
    @classmethod
    def type(self):
        '#t -> list(#t) -> list(#t)'
        t = inference.TypeVariable()
        list_t = inference.TypeOperator('list', t)
        return inference.Function(t, inference.Function(list_t, list_t))

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return lambda: ret(Pair(args[0], args[1]), amb)

    def static_type(self) -> bool:
        return True


class Append(Primitive, metaclass=Singleton):
    @classmethod
    def type(self):
        'list(#t) -> list(#t) -> list(#t)'
        list_t = Null.type()
        return inference.Function(list_t, inference.Function(list_t, list_t))

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return lambda: ret(args[0].append(args[1]), amb)

    def static_type(self) -> bool:
        return True


class Head(Primitive, metaclass=Singleton):
    @classmethod
    def type(self):
        'list(#t) -> #t'
        t = inference.TypeVariable()
        list_t = inference.TypeOperator('list', t)
        return inference.Function(list_t, t)

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return lambda: ret(args[0].car(), amb)

    def static_type(self) -> bool:
        return True


class Tail(Primitive, metaclass=Singleton):
    @classmethod
    def type(self):
        'list(#t) -> list(#t)'
        list_t = Null.type()
        return inference.Function(list_t, list_t)

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return lambda: ret(args[0].cdr(), amb)

    def static_type(self) -> bool:
        return True


class Length(Primitive, metaclass=Singleton):
    @classmethod
    def type(self):
        'list(#t) -> int'
        return inference.Function(Null.type(), Number.type())

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return lambda: ret(Number(len(args[0])), amb)

    def static_type(self) -> bool:
        return True


class Print(Primitive):
    @classmethod
    def type(self):
        'string -> string'
        return inference.Function(
            LinkedList.type(Char.type()),
            LinkedList.type(Char.type())
        )

    def __init__(self, output):
        self._output = output

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        self._output.write(str(args[0]))
        self._output.write("\n")
        return lambda: ret(args, amb)

    def static_type(self) -> bool:
        return True


class Cont(Primitive):
    """wrapper for the continuation passed by `here` (CallCC)
    """

    @classmethod
    def type(self):
        '#t'
        return inference.TypeVariable()

    def __init__(self, ret: callable):
        self._ret = ret

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return lambda: self._ret(args[0], amb)

    def static_type(self) -> bool:
        return True


class CallCC(SpecialForm, metaclass=Singleton):
    """The `here` function
    """

    @classmethod
    def type(self):
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
              amb: types.Amb) -> types.Promise:
        def do_apply(closure: Closure, amb: types.Amb) -> types.Promise:
            return lambda: closure.apply(LinkedList.list([Cont(ret)]), env, ret, amb)

        return args[0].eval(env, do_apply, amb)

    def static_type(self) -> bool:
        return True


class Exit(Primitive):
    @classmethod
    def type(cls):
        '#t'
        return inference.TypeVariable()

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return None

    def static_type(self) -> bool:
        return True


class Spawn(Primitive):
    @classmethod
    def type(cls):
        return Boolean.type()

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        return [lambda: ret(T(), amb), lambda: ret(F(), amb)]

    def static_type(self) -> bool:
        return True


class Error(SpecialForm):
    @classmethod
    def type(self):
        '#t'
        return inference.TypeVariable()

    def __init__(self, cont):
        self.cont = cont

    def apply(self,
              args: LinkedList,
              env: 'environment.Environment',
              ret: types.Continuation,
              amb: types.Amb) -> types.Promise:
        def print_continuation(printer: Print, amb: types.Amb) -> types.Promise:
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
        self.constructors.prepare_analysis(env)

    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set):
        new_env = env.extend()
        new_non_generic = non_generic.copy()
        return_type = self.flat_type.make_type(new_env, new_non_generic)
        for constructor in self.constructors:
            env[constructor.name].unify(constructor.make_type(new_env, return_type, new_non_generic))
            env.note_type_constructor(constructor.name)
        return Null.type()

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: types.Amb) -> types.Promise:
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

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: types.Amb) -> types.Promise:
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
                return Closure(
                    args,
                    Application(
                        TupleConstructor(self.name, len(self.arg_types)),
                        args
                    ),
                    env
                )

            return lambda: env.define(self.name, make_closure(), ret, amb)

    def __str__(self):
        if type(self.arg_types) is Null:
            return str(self.name)
        else:
            return str(self.name) + str(self.arg_types)

    __repr__ = __str__


class Type(TypeSystem):
    """
    represents a type as argument to a type constructor
    in the body of a typedef
    """

    def __init__(self, name: Symbol, components: LinkedList):
        self.name = name
        self.components = components

    def make_type(self, env: inference.TypeEnvironment, non_generic: set):
        components = self.components.map(lambda component: component.make_type(env, non_generic))
        if type(components) is Null:
            return self.get_or_make_type(env)
        else:
            return inference.TypeOperator(self.name.value(), *components)

    def get_or_make_type(self, env):
        return env[self.name]

    def __str__(self):
        return str(self.name) + ('' if type(self.components) is Null else str(self.components))

    __repr__ = __str__


class TupleConstructor(Primitive):
    """
    TypeConstructor is to TypeDef what Closure is to Lambda,
    it's a function of n arguments that returns a Compound Data Structure
    """

    def __init__(self, name: Symbol, num_args: int):
        self.name = name
        self.num_args = num_args

    def apply_evaluated_args(self, args, ret: types.Continuation, amb: types.Amb):
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
              amb: types.Amb) -> types.Promise:
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

    def __eq__(self, other: 'NamedTuple'):
        return self.name == other.name and self.values == other.values


class Composite(Primitive):
    """
    represents the combined body of a composite function
    """

    def __init__(self, components: LinkedList):
        self.components = components

    def __str__(self):
        return "fn " + self.components.qualified_str('{', ' ', '}')

    def analyse_internal(self, env: inference.TypeEnvironment, non_generic: set):
        last_type = None
        for component in self.components:
            this_type = component.analyse_internal(env, non_generic)
            if last_type is not None:
                this_type.unify(last_type)
            last_type = this_type
        return last_type

    def eval(self, env: 'environment.Environment', ret: types.Continuation, amb: types.Amb) -> types.Promise:
        def post_eval_continuation(evaluated_components, amb) -> types.Promise:
            return lambda: ret(CompositeClosure(evaluated_components), amb)

        return lambda: self.components.eval(env, post_eval_continuation, amb)


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

    def __init__(self, components):
        self.components = components

    def apply_evaluated_args(self, args, ret: types.Continuation, amb: types.Amb):
        def try_recursive(components: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
            if type(components) is Null:
                return lambda: amb()
            else:
                def amb2() -> types.Promise:
                    return lambda: try_recursive(components.cdr(), ret, amb)

                return lambda: components.car().apply_evaluated_args(args, ret, amb2)

        return try_recursive(self.components, ret, amb)


class ComponentClosure(Closure):
    """
    type of closure resulting from the evaluation of a ComponentLambda
    """

    def apply_evaluated_args(self, args: LinkedList, ret: types.Continuation, amb: types.Amb) -> types.Promise:
        new_env = self._env.extend()

        def apply_evaluated_recursive(
                fargs: LinkedList,
                aargs: LinkedList,
                ret: types.Continuation,
                amb: types.Amb
        ) -> types.Promise:
            if type(fargs) is Null and type(aargs) is Null:
                return lambda: self._body.eval(new_env, ret, amb)
            elif type(fargs) is Null:  # over-application
                def re_apply_continuation(closure: Closure, amb: types.Amb) -> types.Promise:
                    return lambda: closure.apply_evaluated_args(aargs, ret, amb)

                return lambda: self._body.eval(new_env, re_apply_continuation, amb)
            elif type(aargs) is Null:  # currying
                return lambda: ret(ComponentClosure(fargs, self._body, new_env), amb)
            else:
                def next_continuation(val, amb) -> types.Promise:
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
        Type.__init__(self, Symbol("bool"))

    def get_or_make_type(self, env):
        return Boolean.type()
