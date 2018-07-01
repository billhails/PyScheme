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

from unittest import TestCase
import pyscheme.reader as reader
import io
from pyscheme.exceptions import PySchemeSyntaxError


class TestReader(TestCase):

    def assertParse(self, expected, code, message=''):
        input_file = io.StringIO(code)
        stderr = io.StringIO()
        tokeniser = reader.Tokeniser(input_file)
        parser = reader.Reader(tokeniser, stderr)
        for expect in expected:
            self.assertEqual(expect, str(parser.read()), message + ": " + code)

    def assertSyntaxError(self, code, message=''):
        input_file = io.StringIO(code)
        stderr = io.StringIO()
        tokeniser = reader.Tokeniser(input_file)
        parser = reader.Reader(tokeniser, stderr)
        exception_caught = False
        try:
            result = parser.read()
        except PySchemeSyntaxError as e:
            exception_caught = True
        self.assertTrue(exception_caught, message)

    def test_parse_basic(self):
        self.assertParse(["1"], "1;")

    def test_syntax_error(self):
        self.assertSyntaxError(
            '''
            some garbage } nonsense
            '''
        )
    def test_parse_arithmetic(self):
        self.assertParse(
            ["(1 + (2 * 3))"],
            "1 + 2 * 3;",
            "basic arithmetic precedence works"
        )

    def test_parse_multiple(self):
        self.assertParse(
            [
                "(1 + (2 * 3))",
                "(5 + 4)"
            ],
            "1 + 2 * 3;\n5 + 4;",
            "basic arithmetic precedence works"
        )

    def test_parse_not(self):
        self.assertParse(
            ["not[not[a]]"],
            "not not a;"
        )

    def test_parse_funcall(self):
        self.assertParse(
            ["foo[bar]"],
            "foo(bar);",
            "function application works"
        )

    def test_parse_then_funcall(self):
        self.assertParse(
            ["(foo then bar[baz])"],
            "foo then bar(baz);"
        )

    def test_parse_lassoc_add(self):
        self.assertParse(
            ["((1 + 2) + 3)"],
            "1 + 2 + 3;"
        )

    def test_parse_lassoc_mul(self):
        self.assertParse(
            ['(((1 / 2) * 3) % 4)'],
            "1 / 2 * 3 % 4;"
        )

    def test_parse_lassoc_and(self):
        self.assertParse(
            ["xor[or[and[a, b], c], d]"],
            "a and b or c xor d;"
        )

    def test_parse_rassoc_then(self):
        self.assertParse(
            ['(a then (b then c))'],
            'a then b then c;'
        )

    def test_parse_rassoc_cons(self):
        self.assertParse(
            ['(a @ (b @@ c))'],
            'a @ b @@ c;'
        )

    def test_parse_then_funcall_2(self):
        self.assertParse(
            ["(foo then bar)[baz]"],
            "(foo then bar)(baz);"
        )

    def test_parse_nested_funcall(self):
        self.assertParse(
            ["foo[a][b]"],
            "foo(a)(b);"
        )

    def test_parse_typedef_1(self):
        self.assertParse(
            ['typedef(lst[#t] : [pair[#t, lst[#t]], null])'],
            "typedef lst(#t) { pair(#t, lst(#t)) | null }"
            #                 ----              ----    : type constructors
            #        ------        -  ------            : types
            #             -        -      -             : typevars
        )

    def test_parse_typedef_2(self):
        self.assertParse(
            ['typedef(colour : [red, green, blue])'],
            "typedef colour { red | green | blue }"
        )

    def test_parse_typedef_3(self):
        self.assertParse(
            ['typedef(union[#t, #u] : [first[#t], second[#u]])'],
            "typedef union(#t, #u) { first(#t) | second(#u) }"
        )

    def test_parse_typedef_4(self):
        self.assertParse(
            ['typedef(funny[#t, #u] : [pair[#t, lst[lst[#u]]]])'],
            "typedef funny(#t, #u) { pair(#t, lst(lst(#u))) }"
        )

    def test_parse_composite_1(self):
        self.assertParse(
            ['define map = fn {ComponentLambda [f, null]: { { null } } ComponentLambda [f, pair[h, t]]: { { pair[f[h], map[f, t]] } }}'],
            """
            fn map {
                (f, null) { null }
                (f, pair(h, t)) { pair(f(h), map(f, t)) }
            }
            """
        )

    def test_parse_composite_2(self):
        self.assertParse(
            ['define factorial = fn {ComponentLambda [0]: { { 1 } } ComponentLambda [n]: { { (n * factorial[(n - 1)]) } }}'],
            """
            fn factorial {
                (0) { 1 }
                (n) { n * factorial(n - 1) }
            }
            """
        )

    def test_parse_composite_3(self):
        self.assertParse(
            ['define len = fn {ComponentLambda [[]]: { { 0 } } ComponentLambda [[_ . t]]: { { (1 + len[t]) } }}'],
            """
            fn len {
                ([]) { 0 }
                (_ @ t) { 1 + len(t) }
            }
            """
        )

    def test_parse_sub_function_arg_2(self):
        self.assertParse(
            ['define foo = fn {ComponentLambda [[a, b]]: { { b } }}'],
            '''
            fn foo ([a, b]) {
                b
            }
            '''
        )
