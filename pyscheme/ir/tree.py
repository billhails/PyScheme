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

import re
from pyscheme.exceptions import PySchemeInternalError


class Tree:
    def result(self):
        raise PySchemeInternalError(str(type(self)) + ' does not implement result')


class Label(Tree):
    counter = 0

    def __init__(self, name: str, unique=True):
        if unique:
            suffix = '_' + str(Label.counter)
            Label.counter += 1
        else:
            suffix = ''
        self.name = name + suffix

    def result(self):
        return self

    def __str__(self):
        return 'Label(' + self.name + ')'


class Temp(Tree):
    counter = 0

    def __init__(self):
        self.id = str(Temp.counter)
        Temp.counter += 1

    def result(self):
        return self

    def __str__(self):
        return 'Temp(' + self.id + ')'


def reset_counters():
    """
    for testing
    """
    Label.counter = 0
    Temp.counter = 0


class Int(Tree):
    def __init__(self, value):
        self.value = value

    def result(self):
        return self

    def __str__(self):
        return 'Int(' + str(self.value) + ')'


class BinOp(Tree):
    def __init__(self, target: Temp, left: Temp, right: Temp):
        self.target = target
        self.left = left
        self.right = right

    def base_name(self):
        return re.sub("'>", '', re.sub('.*\.', '', str(type(self))))

    def result(self):
        return self.target

    def __str__(self):
        return str(self.target) + ' = ' + self.base_name() + '(' + str(self.left) + ', ' + str(self.right) + ')'


class Add(BinOp):
    pass


class Mul(BinOp):
    pass


class Sub(BinOp):
    pass


class Div(BinOp):
    pass


class Mod(BinOp):
    pass


class Pow(BinOp):
    pass


class Eq(BinOp):
    pass


class Ne(BinOp):
    pass


class Lt(BinOp):
    pass


class Gt(BinOp):
    pass


class Le(BinOp):
    pass


class Ge(BinOp):
    pass


class And(BinOp):
    pass


class Or(BinOp):
    pass


class Xor(BinOp):
    pass


class Not(Tree):
    def __init__(self, target: Temp, value):
        self.target = target
        self.value = value

    def result(self):
        return self.target

    def __str__(self):
        return str(self.target) + ' = Not(' + str(self.value) + ')'


class Jmp(Tree):
    def __init__(self, label: Label):
        self.label = label

    def __str__(self):
        return 'Jmp(' + str(self.label) + ')'


class Cjmp(Tree):
    def __init__(self, expr: Tree, if_true: Label, if_false: Label):
        self.expr = expr
        self.if_true = if_true
        self.if_false = if_false

    def result(self):
        """
        both brances should have the same target
        """
        return self.if_true.result()

    def __str__(self):
        return 'Cjmp(' + str(self.expr) + ', ' + str(self.if_true) + ', ' + str(self.if_false) + ')'


class Seq(Tree):
    def __init__(self, *statements):
        filtered = []
        for s in statements:
            if not isinstance(s, Int):
                if isinstance(s, Seq):
                    filtered += s.statements
                else:
                    filtered += [s]
        self.statements = filtered

    def result(self):
        if len(self.statements):
            return self.statements[-1].result()
        else:
            return Int(0)

    def __str__(self):
        return 'Seq(' + ', '.join([str(s) for s in self.statements]) + ')'


class Assign(Tree):
    def __init__(self, target: Temp, value: Tree):
        self.target = target
        self.value = value

    def result(self):
        return self.target

    def __str__(self):
        return str(self.target) + ' = ' + str(self.value)


class Rec(Tree):
    def __init__(self, temp: Temp, size: int):
        self.size = size
        self.temp = temp

    def result(self):
        return self.temp

    def __str__(self):
        return 'Rec(' + str(self.temp) + ', '  + str(self.size) + ')'


class SetRec(Tree):
    def __init__(self, temp: Temp, offset: int, val: Tree):
        self.temp = temp
        self.offset = offset
        self.val = val

    def result(self):
        return self.temp

    def __str__(self):
        return 'SetRec(' + str(self.temp) + ', ' + str(self.offset) + ', ' + str(self.val) + ')'


class Env(Tree):
    def __init__(self, target: Temp, frame_number: int, position: int):
        self.target = target
        self.frame_number = frame_number
        self.position = position

    def result(self):
        return self.target

    def __str__(self):
        return str(self.target) + ' = Env(' + str(self.frame_number) + ', ' + str(self.position) + ')'


class ExtendEnv(Tree):
    def __init__(self, size):
        self.size = size

    def __str__(self):
        return 'ExtendEnv(' + str(self.size) + ')'


class SetEnv(Tree):
    def __init__(self, frame_number: int, position: int, source: Temp):
        self.frame_number = frame_number
        self.position = position
        self.source = source

    def result(self):
        return self.source

    def __str__(self):
        return 'Env(' + str(self.frame_number) + ', ' + str(self.position) + ') = ' + str(self.source)


class SetResult(Tree):
    def __init__(self, source: Temp):
        self.source = source

    def result(self):
        return self.source

    def str(self):
        return "result = " + str(self.source)


class Continue(Tree):
    def __str__(self):
        return "Continue()"


class PopEnv(Tree):
    def __str__(self):
        return "PopEnv()"
