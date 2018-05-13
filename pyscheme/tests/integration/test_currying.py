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


from .base import Base


class TestCurrying(Base):
    def test_currying(self):
        self.assertEval(
            '10',
            '''
                fn add (x, y) {
                    x + y
                }
                
                define add2 = add(2);
                
                add2(8);
            '''
        )

    def test_over_application(self):
        self.assertEval(
            '10',
            '''
                fn adder(x) {
                    fn (y) { x + y }
                }
                adder(5, 5);
            '''
        )
