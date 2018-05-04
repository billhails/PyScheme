from functools import reduce
from typing import Callable

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
    def apply(self, args, env, ret: Callable):
        pass


class Primitive(Op):
    def apply(self, args, env, ret: Callable):
        def deferred_apply(evaluated_args):
            return lambda: self.apply_evaluated(evaluated_args, ret)
        return args.eval(env, deferred_apply)

    def apply_evaluated(self, args, ret: Callable):
        pass


class SpecialForm(Op):
    pass


class Closure(Primitive):
    def __init__(self, args, body, env):
        self._args = args
        self._body = body
        self._env = env

    def apply_evaluated(self, args, ret: Callable):
        return lambda: self._body.eval(self._env.extend(dict(zip(self._args, args))), ret)

    def __str__(self):
        return "Closure(" + str(self._args) + ": " + str(self._body) + ")"


class Addition(Primitive):
    def apply_evaluated(self, args, ret: Callable):
        import pyscheme.expr as expr
        return lambda: ret(expr.Constant(reduce(lambda x, y: x.value() + y.value(), args)))


class Equality(Primitive):
    def apply_evaluated(self, args, ret: Callable):
        return lambda: ret(args.car().eq(args.cdr().car()))


class And(SpecialForm):
    def apply(self, args, env, ret: Callable):
        def cont(lhs):
            if lhs.is_true():
                return lambda: args.cdr().car().eval(env, ret)
            elif lhs.is_false():
                return lambda: ret(lhs)
            else:
                def cont2(rhs):
                    if rhs.is_false():
                        return lambda: ret(rhs)
                    else:
                        return lambda: ret(lhs)
                return lambda: args.cdr().car().eval(env, cont2)

        return lambda: args.car().eval(env, cont)


class Or(SpecialForm):
    def apply(self, args, env, ret: Callable):
        def cont(lhs):
            if lhs.is_true():
                return lambda: ret(lhs)
            elif lhs.is_false():
                return lambda: args.cdr().car().eval(env, ret)
            else:
                def cont2(rhs):
                    if rhs.is_true():
                        return lambda: ret(rhs)
                    else:
                        return lambda: ret(lhs)
                return lambda: args.cdr().car().eval(env, cont2)

        return lambda: args.car().eval(env, cont)


class Not(Primitive):
    def apply_evaluated(self, args, ret: Callable):
        return lambda: ret(~(args.car()))


class Xor(Primitive):
    def apply_evaluated(self, args, ret: Callable):
        return lambda: ret(args.car() ^ args.cdr().car())


class Cons(Primitive):
    def apply_evaluated(self, args, ret: Callable):
        from pyscheme.expr import Pair
        return lambda: ret(Pair(args.car(), args.cdr().car()))


class Append(Primitive):
    def apply_evaluated(self, args, ret:Callable):
        return lambda: ret(args.car().append(args.cdr().car()))
