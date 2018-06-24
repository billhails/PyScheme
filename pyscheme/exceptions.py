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

import pyscheme.trace as trace

class PySchemeError(Exception):
    pass


class SymbolError(PySchemeError):
    def __init__(self, symbol):
        self._symbol = symbol


class SymbolNotFoundError(SymbolError):
    def __str__(self):
        return 'SymbolNotFoundError: ' + str(self._symbol)


class TypeSymbolNotFoundError(SymbolError):
    def __str__(self):
        return 'TypeSymbolNotFoundError: ' + str(self._symbol)


class SymbolAlreadyDefinedError(SymbolError):
    def __str__(self):
        return 'SymbolAlreadyDefinedError: ' + str(self._symbol)


class TypeSymbolAlreadyDefinedError(SymbolError):
    def __str__(self):
        return 'TypeSymbolAlreadyDefinedError: ' + str(self._symbol)


class NonBooleanExpressionError(PySchemeError):
    def __str__(self):
        return 'NonBooleanExpressionError'


class MissingPrototypeError(SymbolError):
    def __str__(self):
        return 'MissingPrototypeError: ' + str(self._symbol)


class PySchemeSyntaxError(Exception):
    def __init__(self, msg: str, line: int, next_token):
        self.msg = msg
        self.line = line
        self.next_token = next_token

    def __str__(self) -> str:
        return str(self.msg) + ", line: " + str(self.line) + ", next token: " + str(self.next_token)

    __repr__ = __str__


class PySchemeTypeError(PySchemeError):
    def __init__(self, type1, type2):
        self.type1 = type1
        self.type2 = type2
        self.trace :list = trace.stack.copy()

    def tr(self):
        return ''
        res = '  trace -\n'
        for s in self.trace:
            res += str(s)
            res += "\n"
        return res

    def __str__(self):
        return 'PySchemeTypeError: ' + str(self.type1) + " != " + str(self.type2) + self.tr()


class PySchemeRunTimeError(PySchemeError):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'PySchemeRunTimeError: ' + self.message


class PySchemeInferenceError(PySchemeError):
    def __init__(self, message):
        self.__message = message

    message = property(lambda self: self.__message)

    def __str__(self):
        return 'PySchemeInferenceError: ' + str(self.message)


class PySchemeInternalError(PySchemeError):
    def __init__(self, message):
        self.__message = message

    message = property(lambda self: self.__message)

    def __str__(self):
        return 'PySchemeInternalError: ' + str(self.message)
