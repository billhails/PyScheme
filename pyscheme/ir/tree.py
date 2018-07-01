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


class Tree:
    pass


class BinOp(Tree):
    def __init__(self, left: Tree, right: Tree):
        self.left = left
        self.right = right


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


class Int(Tree):
    def __init__(self, value):
        self.value = value
