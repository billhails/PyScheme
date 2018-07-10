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


class TestMonads(Base):
    def test_monads_1(self):
        self.assertEval(
            'Nothing',
            '''
            load utils.monads as monads;
            env test extends monads {
                a = safe_div(Just(3), Nothing);
            }
            test.a;
            '''
        )

    def test_monads_2(self):
        self.assertEval(
            'Nothing',
            '''
            load utils.monads as monads;
            env test extends monads {
                a = safe_div(Just(3), Just(0));
            }
            test.a;
            '''
        )

    def test_monads_3(self):
        self.assertEval(
            'Just[2]',
            '''
            load utils.monads as monads;
            env test extends monads {
                a = safe_div(Just(4), Just(2));
            }
            test.a;
            '''
        )

    def test_monads_3(self):
        self.assertEval(
            'Nothing',
            '''
            load utils.monads as monads;
            env test extends monads {
                a = safe_div(safe_div(Just(4), Just(0)), Just(2));
            }
            test.a;
            '''
        )

    def test_monads_4(self):
        self.assertEval(
            'Just[6]',
            '''
            load utils.monads;
            env test extends utils.monads {
                a = safe_add(1, 2, 3);
            }
            test.a;
            '''
        )

    def test_monads_5(self):
        self.assertEval(
            'Nothing',
            '''
            load utils.monads;
            env test extends utils.monads {
                a = safe_add(1, 0, 3);
            }
            test.a;
            '''
        )

