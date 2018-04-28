class PySchemeError(Exception):
    pass


class SymbolNotFoundError(PySchemeError):
    def __init__(self, symbol):
        self._symbol = symbol