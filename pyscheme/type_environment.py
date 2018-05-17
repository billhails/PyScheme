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
from . import inference

TypeOrVar = Union['TypeVariable', 'Type']

class TypeEnvironment:

    def extend(self, dictionary: Dict['expr.Symbol', inference.Type]):
        return TypeFrame(self, dictionary)

    def lookup(self, symbol: 'expr.Symbol'):
        raise SymbolNotFoundError(symbol)


class TypeFrame(TypeEnvironment):
    def __init__(self, parent: TypeEnvironment, dictionary: Dict['expr.Symbol', inference.Type]):
        self._parent = parent
        self._dictionary = dictionary

    def lookup(self, symbol: 'expr.Symbol') -> inference.Type:
        if symbol in self._dictionary:
            return self._dictionary[symbol]
        else:
            return self._parent.lookup(symbol)

    def define(self, symbol: 'expr.Symbol', typevar: inference.Type):
        if symbol in self._dictionary:
            raise SymbolAlreadyDefinedError(symbol)
        else:
            self._dictionary[symbol] = typevar
