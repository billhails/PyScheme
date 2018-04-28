from pyscheme.exceptions import SymbolNotFoundError
from typing import Callable

class Environment:
    def extend(self, dictionary):
        return Frame(self, dictionary)

    def lookup(self, symbol, ret: Callable):
        raise SymbolNotFoundError(symbol)


class Frame(Environment):
    def __init__(self, parent: Environment, store):
        self._parent = parent
        self._store = store

    def lookup(self, symbol, ret: Callable):
        if symbol in self._store.keys():
            return lambda: ret(self._store.get(symbol))
        else:
            return lambda: self._parent.lookup(symbol, ret)
