# PyScheme lambda language written in Python
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

# Credit: Rob Smallshire wrote the original python implementation at
# https://github.com/rob-smallshire/hindley-milner-python

from typing import Dict
from . import expr
from .exceptions import SymbolNotFoundError, SymbolAlreadyDefinedError, PySchemeInferenceError, PySchemeTypeError
from typing import Union

TypeOrVar = Union['TypeVariable', 'Type']


def debug(*args, **kwargs):
    if Config.debug:
        print(*args, **kwargs)


class Config:
    debug = False


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

    def unify(self, other, seen=None):
        if seen is None:
            seen = set()
        self.prune().unify_internal(other.prune(), seen)

    def unify_internal(self, other, seen):
        raise PySchemeTypeError(self, other)

    def fresh(self, non_generics):
        return self.freshrec(non_generics, {})

    def freshrec(self, non_generics, mapping):
        return self.prune().make_fresh(non_generics, mapping)

    def final_result(self):
        return self


class TypeVariable(Type):
    next_variable_id = 0

    def __init__(self):
        self.id = TypeVariable.next_variable_id
        TypeVariable.next_variable_id += 1
        self.instance = None
        self.__name = None

    @classmethod
    def reset_names(cls):
        """used for consistency during testing"""
        expr.Symbol.reset()

    @property
    def name(self):
        if self.__name is None:
            self.__name = expr.Symbol.generate().value()
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

    def unify_internal(self, other, seen):
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
    def __init__(self, env: 'TypeEnvironment'):
        self._env = env

    def prune(self):
        return self

    def env(self) -> 'TypeEnvironment':
        return self._env

    def make_fresh(self, non_generics, mapping):
        return self

    def unify_internal(self, other, seen):
        if isinstance(other, TypeVariable):
            other.unify_internal(self, seen)
        elif isinstance(other, EnvironmentType):
            self.env().unify_internal(other.env(), seen)
        else:
            raise PySchemeTypeError(self, other)

    def __str__(self):
        return "EnvironmentType " + str(self._env) + self._env.dump_dict()


class TypeOperator(Type):
    def __init__(self, name: str, *types):
        self.name = name
        self.types = types

    def prune(self):
        return self

    def unify_internal(self, other, seen):
        if isinstance(other, TypeVariable):
            other.unify_internal(self, seen)
        elif isinstance(other, TypeOperator):
            if self.name != other.name or len(self.types) != len(other.types):
                raise PySchemeTypeError(self, other)
            for p, q in zip(self.types, other.types):
                p.unify(q, seen)
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

    def final_result(self):
        return self.types[1].final_result()


class TypeEnvironment:
    counter = 0

    def extend(self, dictionary: Dict['expr.Symbol', Type]=None) -> 'TypeEnvironment':
        if dictionary is None:
            dictionary = {}
        result = TypeFrame(self, dictionary)
        debug("extend -> ", str(result))
        return result

    def unify_internal(self, other, seen):
        pass

    @classmethod
    def next_id(cls):
        my_id = TypeEnvironment.counter
        TypeEnvironment.counter += 1
        return my_id

    def flatten(self, definitions):
        pass

    def dump_dict(self):
        return ''

    def note_type_constructor(self, name: 'expr.Symbol'):
        pass

    def noted_type_constructor(self, name: 'expr.Symbol'):
        return False

    def in_current_frame(self, name: 'expr.Symbol'):
        return False

    def __getitem__(self, symbol: 'expr.Symbol'):
        raise SymbolNotFoundError(symbol)

    def __contains__(self, symbol: 'expr.Symbol') -> bool:
        return False

    def __setitem__(self, symbol: 'expr.Symbol', typevar: Type):
        pass

    def __str__(self):
        return '<0>'

    def __repr__(self):
        return "Root"


class TypeFrame(TypeEnvironment):
    def __init__(self, parent: TypeEnvironment, dictionary: Dict['expr.Symbol', Type]):
        self._parent = parent
        self._dictionary = dictionary
        self.type_constructors = set()
        TypeEnvironment.counter += 1
        self._id = TypeEnvironment.counter

    def unify_internal(self, other, seen):
        if self in seen or other in seen:
            return
        seen.add(self)
        seen.add(other)
        self.unify_half(other, seen)
        other.unify_half(self, seen)

    def unify_half(self, other, seen):
        definitions = self.flatten()
        for k, v in definitions.items():
            v.unify(other[k], seen)

    def flatten(self, definitions=None):
        if definitions is None:
            definitions = {}
        for k in self._dictionary.keys():
            if k not in definitions:
                definitions[k] = self[k]
        self._parent.flatten(definitions)
        return definitions

    def note_type_constructor(self, name: 'expr.Symbol'):
        self.type_constructors.add(name)

    def noted_type_constructor(self, name: 'expr.Symbol'):
        return name in self.type_constructors or self._parent.noted_type_constructor(name)

    def dump_dict(self):
        return ''

    def in_current_frame(self, name: 'expr.Symbol'):
        return name in self._dictionary


    def __getitem__(self, symbol: 'expr.Symbol') -> Type:
        if symbol in self._dictionary:
            return self._dictionary[symbol]
        else:
            return self._parent[symbol]

    def __contains__(self, symbol: 'expr.Symbol') -> bool:
        return symbol in self._dictionary or symbol in self._parent

    def __setitem__(self, symbol: 'expr.Symbol', typevar: Type):
        if symbol in self._dictionary:
            raise SymbolAlreadyDefinedError(symbol)
        else:
            self._dictionary[symbol] = typevar

    def __str__(self):
        return '<' + str(self._id) + '>' + str(self._parent)

    def __repr__(self):
        return str(self) + self.dump_dict() + ' ---> ' + repr(self._parent)

    def __hash__(self):
        return id(self)
