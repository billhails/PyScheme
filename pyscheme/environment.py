# PyScheme lambda language written in Python
#
# Base Environment class plus a Frame subclass
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

from pyscheme.exceptions import SymbolNotFoundError, SymbolAlreadyDefinedError
from typing import Callable
from pyscheme import expr
from pyscheme import types


class Environment:
    def extend(self, dictionary) -> 'Frame':
        return Frame(self, dictionary)

    def lookup(self, symbol, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        raise SymbolNotFoundError(symbol)

    def define(self, symbol, value, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        pass


class Frame(Environment):
    def __init__(self, parent: Environment, dictionary):
        self._parent = parent
        self._dictionary = dictionary

    def lookup(self, symbol, ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        if symbol in self._dictionary.keys():
            return lambda: ret(self._dictionary.get(symbol), amb)
        else:
            return lambda: self._parent.lookup(symbol, ret, amb)

    def define(self, symbol: 'expr.Symbol', value: 'expr.Expr', ret: 'types.Continuation', amb: 'types.Amb') -> 'types.Promise':
        if symbol in self._dictionary.keys():
            raise SymbolAlreadyDefinedError
        else:
            self._dictionary[symbol] = value
            def undo() -> 'types.Promise':
                del self._dictionary[symbol]
                return lambda: amb()
            return lambda: ret(symbol, undo)
