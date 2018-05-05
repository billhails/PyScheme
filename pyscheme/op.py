from functools import reduce
from typing import Callable
from pyscheme.environment import Environment
from pyscheme.singleton import Singleton

"""
We need to distinguish between
1. primitives that have their arguments evaluated for them
   do not take a continuation
2. primitives that are lazy (special forms)
   take a continuation
3. closures that have their arguments evaluated for them
   still need a continuation to evaluate the body
4. macros
   evaluate body with unevaluated args, then re-evaluate result
"""


class Op:
    def apply(self, args, env, ret: Callable, amb: Callable):
        pass


class Primitive(Op):
    def apply(self, args, env: Environment, ret: Callable, amb: Callable):
        def deferred_apply(evaluated_args, amb: Callable):
            return lambda: self.apply_evaluated(evaluated_args, ret, amb)
        return args.eval(env, deferred_apply, amb)

    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        pass


class SpecialForm(Op):
    pass


class Closure(Primitive):
    def __init__(self, args, body, env: Environment):
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


class And(SpecialForm, metaclass=Singleton):
    def apply(self, args, env: Environment, ret: Callable, amb: Callable):
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
    def apply(self, args, env: Environment, ret: Callable, amb: Callable):
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
    def apply(self, args, env: Environment, ret: Callable, amb: Callable):
        def amb2():
            return lambda: args[1].eval(env, ret, amb)
        return lambda: args[0].eval(env, ret, amb2)


class Fail(SpecialForm, metaclass=Singleton):
    def apply(self, args, env: Environment, ret: Callable, amb: Callable):
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
    def apply(self, args, env: Environment, ret: Callable, amb: Callable):
        def do_define(value, amb):
            return lambda: env.define(args[0], value, ret, amb)
        return lambda: args[1].eval(env, do_define, amb)


class Length(Primitive, metaclass=Singleton):
    def apply_evaluated(self, args, ret: Callable, amb: Callable):
        from pyscheme.expr import Constant
        return lambda: ret(Constant(len(args[0])), amb)