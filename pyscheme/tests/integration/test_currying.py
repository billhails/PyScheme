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

    def test_map_curried(self):
        self.assertEval(
            '[2, 3, 4, 5]',
            '''
                fn map(fun, lst) {
                    if (lst == []) {
                        []
                    } else {
                        fun(head(lst)) @ map(fun, tail(lst))
                    }
                }

                fn add(x, y) {
                    x + y
                }

                map(add(1), [1, 2, 3, 4]);
            '''
        )

    def test_map_curried_binop_1(self):
        self.assertEval(
            '[3, 4, 5, 6]',
            '''
                fn map {
                    (f, []) { [] }
                    (f, h @ t) { f(h) @ map(f, t) }
                }

                map(1 + 1 +, [1, 2, 3, 4]);
            '''
        )

    def test_map_curried_binop_2(self):
        self.assertEval(
            '[6, 7, 8, 9]',
            '''
                fn map {
                    (f, []) { [] }
                    (f, h @ t) { f(h) @ map(f, t) }
                }

                map(2 * 2 + 1 +, [1, 2, 3, 4]);
            '''
        )

    def test_map_curried_binop_3(self):
        self.assertEval(
            '[[2, 1], [2, 2], [2, 3], [2, 4]]',
            '''
                fn map {
                    (f, []) { [] }
                    (f, h @ t) { f(h) @ map(f, t) }
                }

                map(2 @, [[1], [2], [3], [4]]);
            '''
        )

    def test_map_curried_binop_4(self):
        self.assertError(
            'PySchemeTypeError: (list(int) -> list(int)) != list(int)',
            '''
                fn map {
                    (f, []) { [] }
                    (f, h @ t) { f(h) @ map(f, t) }
                }

                map(1 @ 2 @, [[1], [2], [3], [4]]);
            '''
        )

    def test_zero_arguments(self):
        self.assertEval(
            '12\n12',
            '''
            fn x() {    // type of x is int, not (() -> int)
                12
            }
            
            0 + x;

            0 + x();    // also works, x() == x
            '''
        )

    def test_noop_apply(self):
        self.assertEval(
            '12',
            '''
            12();
            ''',
            'application with no args is a no-op'
        )

    def test_over_application(self):
        self.assertEval(
            '12',
            '''
            fn adder(x) {
                fn (y) { x + y }
            }
            
            adder(5, 7);
            ''',
            'over application works'
        )
