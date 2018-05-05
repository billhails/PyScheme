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