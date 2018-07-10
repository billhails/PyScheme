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

from pyscheme.singleton import Singleton
from pyscheme.exceptions import PySchemeInternalError


class Environment:

    def extend(self, names: dict):
        return Frame(self, names)

    def lookup(self, name, frame_number=0):
        raise PySchemeInternalError("symbol " + str(name) + " not found in compile-time environment")

    def install(self, name, value):
        raise PySchemeInternalError("install " + str(name) + " called on root compile-time environment")

    def count(self):
        return 0


class Frame(Environment):
    def __init__(self, parent: Environment, names: dict):
        self.parent = parent
        self.position_counter = 0
        self.dictionary = {}
        for name, value in names.items():
            self.install(name, value)

    def install(self, name, value=None):
        self.dictionary[name] = (self.position_counter, value)
        self.position_counter += 1

    def lookup(self, name, frame_number=0):
        if name in self.dictionary:
            return frame_number, self.dictionary[name][0], self.dictionary[name][1]
        else:
            return self.parent.lookup(name, frame_number + 1)

    def count(self):
        return len(self.dictionary)
