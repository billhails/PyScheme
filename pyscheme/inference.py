from typing import Dict
from . import expr
from .exceptions import SymbolNotFoundError, SymbolAlreadyDefinedError, InferenceError
from typing import Union

TypeOrVar = Union['TypeVariable', 'Type']


class AST:
    def analyse(self, env, non_generic=None):
        if non_generic is None:
            non_generic = set()
        return self.analyse_internal(env, non_generic)

    def analyse_internal(self, env, non_generic):
        pass


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


class Type:
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


class TypeVariable(Type):
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


class EnvironmentType(Type):
    def __init__(self, env: 'TypeEnvironment'=None):
        if env is None:
            env = TypeEnvironment();
        self._env = env

    def prune(self):
        return self

    def env(self) -> 'TypeEnvironment':
        return self._env


class TypeOperator(Type):
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


class TypeEnvironment:
    def extend(self, dictionary: Dict['expr.Symbol', Type]=None) -> 'TypeEnvironment':
        if dictionary is None:
            dictionary = {}
        return TypeFrame(self, dictionary)

    def __getitem__(self, symbol: 'expr.Symbol'):
        raise SymbolNotFoundError(symbol)

    def __contains__(self, symbol: 'expr.Symbol') -> bool:
        return False

    def __setitem__(self, symbol: 'expr.Symbol', typevar: Type):
        pass


class TypeFrame(TypeEnvironment):
    def __init__(self, parent: TypeEnvironment, dictionary: Dict['expr.Symbol', Type]):
        self._parent = parent
        self._dictionary = dictionary

    def __getitem__(self, symbol: 'expr.Symbol') -> Type:
        if symbol in self._dictionary:
            return self._dictionary[symbol]
        else:
            return self._parent[symbol]

    def __contains__(self, symbol: 'expr.Symbol'):
        return symbol in self._dictionary or symbol in self._parent

    def __setitem__(self, symbol: 'expr.Symbol', typevar: Type):
        if symbol in self._dictionary:
            raise SymbolAlreadyDefinedError(symbol)
        else:
            self._dictionary[symbol] = typevar
