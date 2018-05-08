# PyScheme lambda language written in Python
#
# Various Exceptions (likely temporary as we'll handle exceptions through the repl)
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


class PySchemeError(Exception):
    pass


class SymbolError(PySchemeError):
    def __init__(self, symbol):
        self._symbol = symbol


class SymbolNotFoundError(SymbolError):
    pass


class SymbolAlreadyDefinedError(SymbolError):
    pass


class NonBooleanExpressionError(PySchemeError):
    pass


class SyntaxError(Exception):
    def __init__(self, msg, line, next):
        self.msg = msg
        self.line = line
        self.next = next

    def __str__(self):
        return str(self.msg) + ", line: " + str(self.line) + ", next token: " + str(self.next)

    __repr__ = __str__