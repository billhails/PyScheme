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


from pyscheme.tests.integration.base import Base


class TestSwitch(Base):
    def test_switch(self):
        self.assertEval(
            'true',
            '''
            a = [1, 2];
            b = [1, 2];
            switch (a, b) {
                ([], [])       { false }
                (h @ t, [])    { false }
                ([], h @ t)    { false }
                (h @ t, h @ t) { true }
            }
            '''
        )

