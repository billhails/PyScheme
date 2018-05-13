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

from typing import Dict
from . import expr
from .exceptions import SymbolNotFoundError, SymbolAlreadyDefinedError, PySchemeTypeError
from typing import Union

TypeOrVar = Union['TypeVariable', 'Type']


class Type:
    def unify(self, other: TypeOrVar):
        if type(other) is Type:
            self.match(other)
        else:
            other.unify(self)

    def match(self, other: 'Type'):  # deep comparison with unification
        pass


class TypeVariable:
    def __init__(self, value: TypeOrVar=None):
        self._value = value

    def unify(self, other: TypeOrVar):
        if self._value is None:
            self._value = other
        else:
            self._value.unify(other)


class TypeEnvironment:

    def extend(self, dictionary: Dict['expr.Symbol', TypeVariable]):
        return TypeFrame(self, dictionary)

    def lookup(self, symbol: 'expr.Symbol'):
        raise SymbolNotFoundError(symbol)


class TypeFrame(TypeEnvironment):
    def __init__(self, parent: TypeEnvironment, dictionary: Dict['expr.Symbol', TypeVariable]):
        self._parent = parent
        self._dictionary = dictionary

    def lookup(self, symbol: 'expr.Symbol') -> TypeVariable:
        if symbol in self._dictionary:
            return self._dictionary[symbol]
        else:
            return self._parent.lookup(symbol)

    def define(self, symbol: 'expr.Symbol', typevar: TypeVariable):
        if symbol in self._dictionary:
            raise SymbolAlreadyDefinedError(symbol)
        else:
            self._dictionary[symbol] = typevar

