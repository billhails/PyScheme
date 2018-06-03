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


class Amb:
    """
    Object representation of Amb that also carries the cut continuation
    Scenarios:
    Normal amb creation is by `define`, `then` and the implicit `cut` after arguments are matched.
    Cut amb creation is by apply_evaluated_args in CompositeClosure
    Normal amb invocation is by `back` and by `match`
    Cut amb invocation is by the cut amb if backtracked to?
        No. The cut installs the cut amb as the actual amb, it is never invoked directly as a cut.
    """
    def __init__(self, amb: callable, cut: 'Amb'=None):
        self._amb = amb
        self._cut = cut

    def __call__(self):
        return self._amb()

    def cut(self):
        return self._cut

    def cut_point(self):
        return Amb(self._amb, Amb(self._amb))