# PyScheme lambda language written in Python
#
# operators mostly bound in the top-level env by the repl
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

from typing import Callable
from pyscheme import environment
from pyscheme.singleton import Singleton
from pyscheme import expr

"""
We need to distinguish between
1. primitives that have their arguments evaluated for them
   do not take a continuation
2. primitives that are lazy (special forms)
   take a continuation
3. closures that have their arguments evaluated for them
   still need a continuation to evaluate the body
4. macros
   evaluate body with unevaluated args, binop_then re-evaluate result
"""


class Op:
    def apply(self, args: 'expr.List', env, ret: Callable, amb: Callable):
        pass


class Primitive(Op):
    def apply(self, args, env: 'environment.Environment', ret: Callable, amb: Callable):
        def deferred_apply(evaluated_args, amb: Callable):
            return lambda: self.apply_evaluated(evaluated_args, ret, amb)
        return args.eval(env, deferred_apply, amb)

    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        pass


class SpecialForm(Op):
    pass


class Closure(Primitive):
    def __init__(self, args, body, env: 'environment.Environment'):
        self._args = args
        self._body = body
        self._env = env

    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: self._body.eval(self._env.extend(dict(zip(self._args, args))), ret, amb)

    def __str__(self):
        return "Closure(" + str(self._args) + ": " + str(self._body) + ")"


class Addition(Primitive, metaclass=Singleton):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: ret(args[0] + args[1], amb)


class Subtraction(Primitive, metaclass=Singleton):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: ret(args[0] - args[1], amb)


class Multiplication(Primitive, metaclass=Singleton):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: ret(args[0] * args[1], amb)


class Division(Primitive, metaclass=Singleton):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: ret(args[0] // args[1], amb)


class Modulus(Primitive, metaclass=Singleton):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: ret(args[0] % args[1], amb)


class Equality(Primitive, metaclass=Singleton):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: ret(args[0].eq(args[1]), amb)


class GT(Primitive, metaclass=Singleton):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: ret(args[0].gt(args[1]), amb)


class LT(Primitive, metaclass=Singleton):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: ret(args[0].lt(args[1]), amb)


class GE(Primitive, metaclass=Singleton):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: ret(args[0].ge(args[1]), amb)


class LE(Primitive, metaclass=Singleton):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: ret(args[0].le(args[1]), amb)


class NE(Primitive, metaclass=Singleton):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: ret(args[0].ne(args[1]), amb)


class And(SpecialForm, metaclass=Singleton):
    def apply(self, args, env: 'environment.Environment', ret: Callable, amb: Callable):
        def cont(lhs, amb: Callable):
            if lhs.is_true():
                return lambda: args[1].eval(env, ret, amb)
            elif lhs.is_false():
                return lambda: ret(lhs, amb)
            else:
                def cont2(rhs, amb: Callable):
                    if rhs.is_false():
                        return lambda: ret(rhs, amb)
                    else:
                        return lambda: ret(lhs, amb)
                return lambda: args[1].eval(env, cont2, amb)

        return lambda: args[0].eval(env, cont, amb)


class Or(SpecialForm, metaclass=Singleton):
    def apply(self, args, env: 'environment.Environment', ret: Callable, amb: Callable):
        def cont(lhs, amb: Callable):
            if lhs.is_true():
                return lambda: ret(lhs, amb)
            elif lhs.is_false():
                return lambda: args[1].eval(env, ret, amb)
            else:
                def cont2(rhs, amb: Callable):
                    if rhs.is_true():
                        return lambda: ret(rhs, amb)
                    else:
                        return lambda: ret(lhs, amb)
                return lambda: args[1].eval(env, cont2, amb)
        return lambda: args[0].eval(env, cont, amb)


class Then(SpecialForm, metaclass=Singleton):
    def apply(self, args, env: 'environment.Environment', ret: Callable, amb: Callable):
        def amb2():
            return lambda: args[1].eval(env, ret, amb)
        return lambda: args[0].eval(env, ret, amb2)


class Back(SpecialForm, metaclass=Singleton):
    def apply(self, args, env: 'environment.Environment', ret: Callable, amb: Callable):
        return lambda: amb()


class Not(Primitive, metaclass=Singleton):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: ret(~(args[0]), amb)


class Xor(Primitive, metaclass=Singleton):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: ret(args[0] ^ args[1], amb)


class Cons(Primitive, metaclass=Singleton):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        from pyscheme.expr import Pair
        return lambda: ret(Pair(args[0], args[1]), amb)


class Append(Primitive, metaclass=Singleton):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: ret(args[0].append(args[1]), amb)


class Head(Primitive, metaclass=Singleton):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: ret(args[0].car(), amb)


class Tail(Primitive, metaclass=Singleton):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: ret(args[0].cdr(), amb)


class Define(SpecialForm, metaclass=Singleton):
    def apply(self, args, env: 'environment.Environment', ret: Callable, amb: Callable):

        def do_define(value, amb):
            def ret_none(value, amb):
                return lambda: ret(None, amb)
            return lambda: env.define(args[0], value, ret_none, amb)
        return lambda: args[1].eval(env, do_define, amb)


class Length(Primitive, metaclass=Singleton):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        from pyscheme.expr import Constant
        return lambda: ret(Constant(len(args[0])), amb)


class Print(Primitive):
    def __init__(self, output):
        self._output = output

    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        for arg in args:
            self._output.write(str(arg))
        self._output.write("\n")
        return lambda: ret(args, amb)


class Continuation(Primitive):
    def __init__(self, ret: callable):
        self._ret = ret

    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return lambda: self._ret(args[0], amb)

    def eval(self, env, ret: callable, amb: callable):
        return lambda: ret(self, amb)


class CallCC(SpecialForm, metaclass=Singleton):
    def apply(self, args, env: 'environment.Environment', ret: Callable, amb: Callable):
        from pyscheme.expr import List
        def do_apply(closure: Closure, amb):
            return lambda: closure.apply(List.list([Continuation(ret)]), env, ret, amb)
        return lambda: args[0].eval(env, do_apply, amb)


class Exit(Primitive):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        return None

class Error(SpecialForm):
    def __init__(self, cont):
        self.cont = cont

    def apply(self, args, env: 'environment.Environment', ret: Callable, amb: Callable):
        from pyscheme.expr import Symbol

        def print_continuation(printer: Print, amb: callable):
            return lambda: printer.apply(args, env, self.cont, amb)

        return lambda: env.lookup(Symbol("print"), print_continuation, amb)