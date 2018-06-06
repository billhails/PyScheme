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


class TestLists(Base):
    """
    tests exercising various functions over the built-in lists
    """
    def test_homemade_append(self):
        self.assertEval(
            '[1, 2, 3, 4, 5, 6]',
            '''
            fn append {
                ([], other) { other }
                (h @ t, other) { h @ append(t, other) }
            }
            
            append([1, 2, 3], [4, 5, 6]);
            '''
        )

    def test_replace(self):
        self.assertEval(
            '[1, 2, 11, 4, 5]',
            '''
            fn replace {
                ([], i, y)    { error("subscript") }
                (h @ t, 0, y) { y @ t }
                (h @ t, n, y) { h @ replace(t, n - 1, y) }
            }
            
            replace([1, 2, 3, 4, 5], 2, 11);
            '''
        )

    def test_suffixes(self):
        self.assertEval(
            '[[1, 2, 3, 4], [2, 3, 4], [3, 4], [4], []]',
            '''
            fn suffixes {
                ([]) { [[]] }
                (h @ t) { (h @ t) @ suffixes(t) }
            }
            
            suffixes([1, 2, 3, 4]);
            '''
        )

    def test_last(self):
        self.assertEval(
            '4',
            '''
            fn last {
                ([])     { error("empty list") }
                (h @ []) { h }
                (h @ t)  { last(t) }
            }
            
            last([1, 2, 3, 4]);
            '''
        )

    def test_reverse(self):
        self.assertEval(
            '[10, 9, 8, 7, 6, 5, 4, 3, 2, 1]',
            '''
            fn reverse(lst) {
                fn rev {
                    ([], acc) { acc }
                    (h @ t, acc) { rev(t, h @ acc) }
                }
                rev(lst, []);
            }
            
            reverse([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
            '''
        )
