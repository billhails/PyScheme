class Continuation:
    def __init__(self, closure):
        self._closure = closure

    def __call__(self, *args, **kwargs):
        return lambda: self._closure(args[0])
