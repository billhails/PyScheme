from .exceptions import InferenceError, SymbolNotFoundError


class AST:
    def analyse(self, env, non_generic=None):
        if non_generic is None:
            non_generic = set()
        return self.analyse_internal(env, non_generic)

    def analyse_internal(self, env, non_generic):
        pass


class Lambda(AST):
    def __init__(self, v, body):
        self.arg = v
        self.body = body

    def analyse_internal(self, env, non_generic):
        arg_type = TypeVariable()
        new_env = env.copy()
        new_env[self.arg] = arg_type
        new_non_generic = non_generic.copy()
        new_non_generic.add(arg_type)
        result_type = self.body.analyse_internal(new_env, new_non_generic)
        return Function(arg_type, result_type)


class Literal(AST):
    def __init__(self, value):
        self.value = value


class Number(Literal):
    def analyse_internal(self, env, non_generic):
        return Integer


class Boolean(Literal):
    def analyse_internal(self, env, non_generic):
        return Bool


class Identifier(AST):
    def __init__(self, name):
        self.name = name

    def analyse_internal(self, env, non_generic):
        return self.get_type(env, non_generic)

    def get_type(self, env, non_generic):
        if self.name in env:
            return self.fresh(env[self.name], non_generic)
        else:
            raise SymbolNotFoundError(self.name)

    @classmethod
    def fresh(cls, t, non_generics):
        mappings = {}

        def freshrec(tp):
            def is_generic(v, non_generic):
                return not v.occurs_in(non_generic)

            p = tp.prune()
            if isinstance(p, TypeVariable):
                if is_generic(p, non_generics):
                    if p not in mappings:
                        mappings[p] = TypeVariable()
                    return mappings[p]
                else:
                    return p
            elif isinstance(p, TypeOperator):
                return TypeOperator(p.name, *[freshrec(x) for x in p.types])

        return freshrec(t)


class Apply(AST):
    def __init__(self, fn, arg):
        self.fn = fn
        self.arg = arg

    def analyse_internal(self, env, non_generic):
        result_type = TypeVariable()
        Function(
            self.arg.analyse_internal(env, non_generic),
            result_type
        ).unify(self.fn.analyse_internal(env, non_generic))
        return result_type


class Let(AST):
    def __init__(self, v, defn, body):
        self.v = v
        self.defn = defn
        self.body = body

    def analyse_internal(self, env, non_generic):
        defn_type = self.defn.analyse_internal(env, non_generic)
        new_env = env.copy()
        new_env[self.v] = defn_type
        return self.body.analyse_internal(new_env, non_generic)


class Letrec(AST):
    def __init__(self, v, defn, body):
        self.v = v
        self.defn = defn
        self.body = body

    def analyse_internal(self, env, non_generic):
        new_type = TypeVariable()
        new_env = env.copy()
        new_env[self.v] = new_type
        new_non_generic = non_generic.copy()
        new_non_generic.add(new_type)
        defn_type = self.defn.analyse_internal(new_env, new_non_generic)
        new_type.unify(defn_type)
        return self.body.analyse_internal(new_env, non_generic)


class InferenceType:
    def prune(self):
        pass

    def occurs_in(self, types):
        return any(self.occurs_in_type(t) for t in types)

    def occurs_in_type(self, other):
        pruned_other = other.prune()
        if pruned_other == self:
            return True
        elif isinstance(pruned_other, TypeOperator):
            return self.occurs_in(pruned_other.types)
        return False

    def unify(self, other):
        self.prune().unify_internal(other.prune())

    def unify_internal(self, other):
        assert 0, "Not unified"


class TypeVariable(InferenceType):
    next_variable_id = 0

    def __init__(self):
        self.id = TypeVariable.next_variable_id
        TypeVariable.next_variable_id += 1
        self.instance = None
        self.__name = None

    next_variable_name = 'a'

    @property
    def name(self):
        if self.__name is None:
            self.__name = TypeVariable.next_variable_name
            TypeVariable.next_variable_name = chr(ord(TypeVariable.next_variable_name) + 1)
        return self.__name

    def prune(self):
        if self.instance is not None:
            self.instance = self.instance.prune()
            return self.instance
        return self

    def unify_internal(self, other):
        if self != other:
            if self.occurs_in_type(other):
                raise InferenceError("recursive unification")
            self.instance = other

    def __str__(self):
        if self.instance is not None:
            return str(self.instance)
        else:
            return self.name

    def __repr__(self):
        return "TypeVariable(id = {0})".format(self.id)


class TypeOperator(InferenceType):
    def __init__(self, name, *types):
        self.name = name
        self.types = types

    def prune(self):
        return self

    def unify_internal(self, other):
        if isinstance(other, TypeVariable):
            other.unify_internal(self)
        elif isinstance(other, TypeOperator):
            if self.name != other.name or len(self.types) != len(other.types):
                raise InferenceError("Type mismatch: {0} != {1}".format(str(self), str(other)))
            for p, q in zip(self.types, other.types):
                p.unify(q)
        else:
            assert 0, "Not unified"

    def __str__(self):
        num_types = len(self.types)
        if num_types == 0:
            return self.name
        elif num_types == 2:
            return "({0} {1} {2})".format(str(self.types[0]), self.name, str(self.types[1]))
        else:
            return "{0}({1})".format(self.name, ' '.join([str(t) for t in self.types]))


class Function(TypeOperator):
    def __init__(self, from_type, to_type):
        super(Function, self).__init__("->", from_type, to_type)


Integer = TypeOperator("int")

Bool = TypeOperator("bool")
