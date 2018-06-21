# PyScheme lambda language written in Python
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


# This code originally translated from Andrew Appel "Compiling with Continuations"

from enum import Enum, auto
from typing import List, Tuple


class var:
    def __init__(self, name: str):
        self.name = name


class value:
    """
    The union of all different types of atomic arguments
    that can be provided to the CPS operators
    """
    pass


class VAR(value):
    def __init__(self, v: var):
        self.var = v


class LABEL(value):
    def __init__(self, v: var):
        self.var = v


class INT(value):
    def __init__(self, i: int):
        self.int = i


class REAL(value):
    def __init__(self, r: str):
        self.real = r


class STRING(value):
    def __init__(self, s: str):
        self.string = s


class accesspath:
    pass


class OFFp(accesspath):
    def __init__(self, i: int):
        self.int = i


class SELp(accesspath):
    def __init__(self, i: int, a: accesspath):
        self.int = i
        self.accesspath = a


class primop(Enum):
    mul = auto()
    add = auto()
    sub = auto()
    div = auto()
    mod = auto()
    exp = auto()
    eq = auto()
    ne = auto()
    gt = auto()
    lt = auto()
    ge = auto()
    le = auto()
    # etc.


class cexp:
    """
    The abstract type of continuation expressions
    """
    pass


class RECORD(cexp):
    """
    RECORD([(VAR(var('a')), OFFp(0)), (INT(2), OFFp(0)), (VAR(var('c')), OFFp(0))] w, E)
    makes a 3-word record initialised to (a, 2, c) and puts its address in w, then continues with E
    """
    def __init__(self, t: List[Tuple[value, accesspath]], v: var, c: cexp):
        """
        :param t: List[Tuple[value, accesspath]] - fields of the record
        :param v: var - result address
        :param c: cexp - continuation
        """
        self.tuples = t
        self.var = v
        self.cexp = c


class SELECT(cexp):
    """
    SELECT(i, v, w, E) fetches the i'th field of v into w then continues at E
    """
    def __init__(self, i: int, val: value, w: var, c: cexp):
        """
        :param i: int - index in to record
        :param val: value - address of record
        :param w: var - result
        :param c: cexp - continuation
        """
        self.int = i
        self.value = val
        self.var = w
        self.cexp = c


class OFFSET(cexp):
    """
    OFFSET(i, v, w, E)
    if v points at the j'th field of a record this makes w point at the j+i'th fiels, and continues at E
    """
    def __init__(self, i: int, val: value, v: var, c: cexp):
        """
        :param i: int - offset
        :param val: value - current pointer
        :param v: var - result
        :param c: cexp - continuation
        """
        self.int = i
        self.value = val
        self.var = v
        self.cexp = c


class APP(cexp):
    """
    APP(var('f'), [a1, a2,..., an])
    Apply a function to actual arguments.
    N.B the continuation is in each function.
    """
    def __init__(self, function: value, arguments: List[value]):
        """
        :param function: value - the function
        :param arguments: List[value] - the actual arguments
        """
        self.function = function
        self.arguments = arguments


class FIX(cexp):
    """
    define a set of mutually recursive functions
    FIX([(f1, [v11, v12,..., v1m], B1)
         (f2, [v21, v22,..., v2m], B2)
         ...
         (fn, [vn1, vn2,..., vnm], Bn)],
         E)
    defines 0 or more functions fj callable from E or from one another's bodies Bj
    Formal arguments are vnm, fn are the resulting function (closure?) addresses
    """
    def __init__(self, functions: List[Tuple[var, List[var], cexp]], c: cexp):
        """
        :param functions: List[Tuple[var, List[var], cexp]] - functions
        :param c: cexp - continuation
        """
        self.functions = functions
        self.cexp = c


class SWITCH(cexp):
    """
    multi-way branches
    SWITCH(VAR(var('i')), [E0, E1, E2, E3, E4])
    chooses Ei
    """
    def __init__(self, val: value, cexps: List[cexp]):
        """
        :param val: value - switch
        :param cexps: List[cexp] - cases
        """
        self.value = val
        self.cexps = cexps


class PRIMOP(cexp):
    """
    primitive operations, for example
    if (a > b) F G
    can be expressed as PRIMOP(primop.gt, [VAR(var('a')), VAR(var('b'))], [], [F, G])
    """
    def __init__(self, prim: primop, args: List[value], results: List[var], cexps: List[cexp]):
        """
        :param prim: primop - primitive
        :param args: List[value] - arguments to the primop
        :param results: List[var] - result storage
        :param cexps: List[cexp] - continuation(s)
        """
        self.primop = prim
        self.args = args
        self.results = results
        self.cexps = cexps
