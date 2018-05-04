from pyscheme.exceptions import SymbolNotFoundError
from typing import Callable


class Environment:
    def extend(self, dictionary):
        return Frame(self, dictionary)

    def lookup(self, symbol, ret: Callable):
        raise SymbolNotFoundError(symbol)


class Frame(Environment):
    def __init__(self, parent: Environment, dictionary):
        self._parent = parent
        self._dictionary = dictionary

    def lookup(self, symbol, ret: Callable):
        if symbol in self._dictionary.keys():
            return lambda: ret(self._dictionary.get(symbol))
        else:
            return lambda: self._parent.lookup(symbol, ret)
