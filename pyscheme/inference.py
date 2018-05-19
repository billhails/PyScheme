from typing import Dict
from . import expr
from .exceptions import SymbolNotFoundError, SymbolAlreadyDefinedError, PySchemeInferenceError, PySchemeTypeError
from typing import Union

TypeOrVar = Union['TypeVariable', 'Type']


class Type:
    def prune(self):
        pass

    def occurs_in(self, types):
        return any(self.occurs_in_type(t) for t in types)

    def is_generic(self, non_generic):
        return not self.occurs_in(non_generic)

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
        raise PySchemeTypeError(self, other)

    def fresh(self, non_generics):
        return self.freshrec(non_generics, {})

    def freshrec(self, non_generics, mapping):
        return self.prune().make_fresh(non_generics, mapping)


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

    def make_fresh(self, non_generics, mapping):
        if self.is_generic(non_generics):
            if self not in mapping:
                mapping[self] = TypeVariable()
            return mapping[self]
        else:
            return self

    def prune(self):
        if self.instance is not None:
            self.instance = self.instance.prune()
            return self.instance
        return self

    def unify_internal(self, other):
        if self != other:
            if self.occurs_in_type(other):
                raise PySchemeInferenceError("recursive unification")
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
            env = TypeEnvironment().extend()
        self._env = env

    def prune(self):
        return self

    def env(self) -> 'TypeEnvironment':
        return self._env

    def make_fresh(self, non_generics, mapping):
        if self.is_generic(non_generics):
            if self not in mapping:
                mapping[self] = TypeVariable()
            return mapping[self]
        else:
            return self

    def unify_internal(self, other):
        if isinstance(other, TypeVariable):
            other.unify_internal(self)
        elif isinstance(other, EnvironmentType):
            self.env().unify_internal(other.env())
        else:
            raise PySchemeTypeError(self, other)


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
                raise PySchemeTypeError(self, other)
            for p, q in zip(self.types, other.types):
                p.unify(q)
        else:
            raise PySchemeTypeError(self, other)

    def make_fresh(self, non_generics, mapping):
        return TypeOperator(self.name, *[x.freshrec(non_generics, mapping) for x in self.types])

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


class EnvironmentTracker:
    def __init__(self):
        self.missing = {}

    def note_missing(self, symbol, path):
        if symbol not in self.missing:
            self.missing[symbol] = {}
        if path not in self.missing[symbol]:
            self.missing[symbol][path] = TypeVariable()
        return self.missing[symbol][path]

    def note_added(self, symbol, value, path: str):
        if symbol in self.missing:
            for location in self.missing[symbol].keys():
                if location.startswith(path):
                    self.missing[symbol][path].unify(value)


class TypeEnvironment:
    counter = 0
    missing = EnvironmentTracker()

    def extend(self, dictionary: Dict['expr.Symbol', Type]=None) -> 'TypeEnvironment':
        if dictionary is None:
            dictionary = {}
        return TypeFrame(self, dictionary)

    def unify_internal(self, other):
        pass

    def note_missing(self, symbol, path):
        return TypeEnvironment.missing.note_missing(symbol, path)

    def note_added(self, symbol, value, path):
        self.missing.note_added(symbol, value, path)

    @classmethod
    def next_id(cls):
        my_id = TypeEnvironment.counter
        TypeEnvironment.counter += 1
        return my_id

    def flatten(self, definitions):
        pass

    def __getitem__(self, symbol: 'expr.Symbol'):
        raise SymbolNotFoundError(symbol)

    def __contains__(self, symbol: 'expr.Symbol') -> bool:
        return False

    def __setitem__(self, symbol: 'expr.Symbol', typevar: Type):
        pass

    def __str__(self):
        return '<0>'


class TypeFrame(TypeEnvironment):
    def __init__(self, parent: TypeEnvironment, dictionary: Dict['expr.Symbol', Type]):
        self._parent = parent
        self._dictionary = dictionary
        self._id = TypeEnvironment.counter
        TypeEnvironment.counter += 1

    def extend_path(self, path):
        return '.' + str(self._id) + path

    def note_missing(self, symbol, path='.'):
        return self._parent.note_missing(symbol, self.extend_path(path))

    def note_added(self, symbol, value, path='.'):
        self._parent.note_added(symbol, value, self.extend_path(path))

    def unify_internal(self, other):
        definitions = {}
        self.flatten(definitions)
        for k in definitions.keys():
            if k in other:
                definitions[k].unify(other[k])
            else:
                typevar = other.note_missing(k)
                typevar.unify(definitions[k])

    def flatten(self, definitions):
        for k in self._dictionary.keys():
            if k not in definitions:
                definitions[k] = self[k]
        self._parent.flatten(definitions)

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
            self.note_added(symbol, typevar)

    def __str__(self):
        return '<' + str(self._id) + '>' + str(self._parent)
