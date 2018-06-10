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


class TestTypedef(Base):
    def test_typedef_23(self):
        self.assertEval(
            'red',
            '''
            typedef colour { red }
            
            red;
            ''',
            "type constructors with no args are values"
        )

    def test_typedef_33(self):
        self.assertEval(
            "true",
            """
            typedef colour { red | green }
            
            red == red;
            """,
            "type values can be compared"
        )

    def test_typedef_48(self):
        self.assertEval(
            "false",
            """
            typedef colour { red | green }
            
            red == green;
            """,
            "type values can be compared"
        )

    def test_typedef_63(self):
        self.assertEval(
            "pair[1, null]",
            """
            typedef lst(t) { pair(t, lst(t)) | null }
            
            pair(1, null);
            
            """,
            "constructed types have sensible print values"
        )

    def test_typedef_75(self):
        self.assertEval(
            "true",
            """
            typedef lst(t) { pair(t, lst(t)) | null }
            
            pair(1, null) == pair(1, null);
            """,
            "lists of the same type and equal values can be compared and are equal"
        )

    def test_typedef_90(self):
        self.assertEval(
            "ok",
            """
            typedef lst(t) { pair(t, lst(t)) | null }
            
            if (pair(1, null) == pair(2, null)) {
                "nok"
            } else {
                "ok"
            }
            """,
            "lists of the same type and different values can be compared and are unequal"
        )

    def test_typedef_105(self):
        self.assertError(
            "PySchemeTypeError: bool != int",
            """
            typedef lst(t) { pair(t, lst(t)) | null }
            
            pair(1, null) == pair(true, null);
            """,
            "cannot compare lists of different types"
        )

    def test_typedef_116(self):
        self.assertEval(
            "pair[1, pair[2, null]]",
            """
            typedef lst(t) { pair(t, lst(t)) | null }
            
            pair(1, pair(2, null));
            """,
            "lists can only contain the same types"
        )

    def test_typedef_127(self):
        self.assertError(
            "PySchemeTypeError: bool != int",
            """
            typedef lst(t) { pair(t, lst(t)) | null }
            
            pair(1, pair(true, null));
            """,
            "lst cannot contain mixed types"
        )

    def test_typedef_139(self):
        self.assertError(
            "PySchemeTypeError: lst(int) != colour",
            """
            typedef lst(t) { pair(t, lst(t)) | null }
            typedef colour { red | green }

            red == pair(1, null);
            """,
            "cannot compare different types"
        )

    def test_typedef_151(self):
        self.assertEval(
            "false",
            """
            typedef colour { red | green }
            
            fn(x, y) {
                x == y
            }(red, green);
            """,
            ""
        )

    def test_typedef_152(self):
        self.assertError(
            "PySchemeTypeError: bool != colour",
            """
            typedef colour { red | green }

            fn(x, y) {
                x == y
            }(red, true);
            """,
            "type inference works for user defined types"
        )

    def test_curried_type(self):
        self.assertEval(
            'group[1, 2]',
            '''
            typedef some(n) { group(n, n) }
            
            define start = group(1);
            
            start(2);
            ''',
            'type constructors can be curried'
        )

    def test_lst_append(self):
        self.assertEval(
            'pair[1, pair[2, pair[3, pair[4, pair[5, pair[6, null]]]]]]',
            '''
            {
                typedef lst(t) { pair(t, lst(t)) | null }
                
                fn append {
                    (null, ys) { ys }
                    (pair(h, t), ys) { pair(h, append(t, ys)) }
                }
                
                define xs = pair(1, pair(2, pair(3, null)));
                define ys = pair(4, pair(5, pair(6, null)));
                
                append(xs, ys);
            }
            '''
        )
