# PyScheme lambda language written in Python
#
# Singleton and FlyWeight meta classes
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

class Singleton(type):
    """Singleton type

    Singletons are fine as long as you don't keep state in them
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class FlyWeight(type):
    """FlyWeight type

    The first argument to the constructor must be the identifier of the flyweight
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        name = args[0]
        if cls not in cls._instances:
            cls._instances[cls] = {}
        if name not in cls._instances[cls]:
            cls._instances[cls][name] = super(FlyWeight, cls).__call__(*args, **kwargs)
        return cls._instances[cls][name]