from pyscheme.exceptions import SymbolNotFoundError, SymbolAlreadyDefinedError
from typing import Callable


class Environment:
    def extend(self, dictionary):
        return Frame(self, dictionary)

    def lookup(self, symbol, ret: Callable, amb: Callable):
        raise SymbolNotFoundError(symbol)

    def define(self, symbol, value, ret: Callable, amb: Callable):
        pass


class Frame(Environment):
    def __init__(self, parent: Environment, dictionary):
        self._parent = parent
        self._dictionary = dictionary

    def lookup(self, symbol, ret: Callable, amb: Callable):
        if symbol in self._dictionary.keys():
            return lambda: ret(self._dictionary.get(symbol), amb)
        else:
            return lambda: self._parent.lookup(symbol, ret, amb)

    def define(self, symbol, value, ret: Callable, amb: Callable):
        if symbol in self._dictionary.keys():
            raise SymbolAlreadyDefinedError
        else:
            self._dictionary[symbol] = value
            def undo():
                del self._dictionary[symbol]
                return lambda: amb()
            return lambda: ret(symbol, undo)
