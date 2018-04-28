import pyscheme.environment as envt
from typing import Callable

class List:
    pass


class List:
    _null_instance = None

    @classmethod
    def null(cls):
        """singleton factory method for Null"""
        if cls._null_instance is None:
            cls._null_instance = Null()
        return cls._null_instance

    @classmethod
    def list(cls, *args):
        if len(args) == 0:
            return cls.null()
        else:
            return Cons(args[0], cls.list(*(args[1:])))

    def is_null(self):
        return False

    def car(self):
        pass

    def cdr(self):
        pass

    def map_eval(self, env: envt.Environment, ret: Callable):
        pass

    def __len__(self):
        pass

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def trailing_string(self) -> str:
        pass

    def append(self, other) -> List:
        pass

    def __iter__(self):
        return Iterator(self)


class Cons(List):
    def __init__(self, car, cdr: List):
        self._car = car
        self._cdr = cdr
        self._len = 1 + len(cdr)

    def car(self):
        return self._car

    def cdr(self):
        return self._cdr

    def map_eval(self, env: envt.Environment, ret: Callable):
        def car_continuation(evaluated_car):
            def cdr_continuation(evaluated_cdr):
                return lambda: ret(Cons(evaluated_car, evaluated_cdr))
            return lambda: self._cdr.map_eval(env, cdr_continuation)
        return self._car.eval(env, car_continuation)

    def __len__(self):
        return self._len

    def __str__(self):
        return '(' + str(self._car) + self._cdr.trailing_string()

    __repr__ = __str__

    def trailing_string(self) -> str:
        return ', ' + str(self._car) + self._cdr.trailing_string()

    def append(self, other):
        Cons(self._car, self._cdr.append(other))


class Null(List):
    def is_null(self):
        return True

    def car(self):
        return self

    def cdr(self):
        return self

    def map_eval(self, env: envt.Environment, ret: Callable):
        return ret(self)

    def __len__(self):
        return 0

    def __str__(self):
        return '()'

    __repr__ = __str__

    def trailing_string(self) -> str:
        return ')'

    def append(self, other):
        return other


class Iterator:
    def __init__(self, lst: List):
        self._lst = lst

    def __next__(self):
        if self._lst.is_null():
            raise StopIteration
        else:
            val = self._lst.car()
            self._lst = self._lst.cdr()
            return val