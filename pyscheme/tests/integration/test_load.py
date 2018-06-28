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


class TestTestLoad(Base):
    """
    The files being loaded are under PyScheme/data
    """
    def test_test_load_1(self):
        self.assertEval(
            '[2, 3, 3, 4, 5, 6, 8]',
            '''
            load utils.sort as sort;

            unsorted = [5, 4, 6, 2, 3, 3, 8];

            sort.qsort(unsorted);
            '''
        )

    def test_test_load_2(self):
        self.assertEval(
            '[3, 4, 4, 5, 6, 7, 9]',
            '''
            {
                load utils.sort;
                load utils.lists as lists;

                unsorted = [5, 4, 6, 2, 3, 3, 8];

                lists.map(1+, utils.sort.qsort(unsorted));
            }
            '''
        )

    def test_test_load_3(self):
        self.assertEval(
            '10',
            '''
            {
                load utils.lists as lists;

                fn add(x, y) { x + y }

                lists.reduce(add, 0, [1, 2, 3, 4]);
            }
            '''
        )
