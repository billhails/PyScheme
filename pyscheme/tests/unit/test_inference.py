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
import pyscheme.repl as repl
import io
from pyscheme.exceptions import SymbolNotFoundError, PySchemeInferenceError, PySchemeTypeError
from pyscheme.inference import TypeVariable


class TestInference(TestCase):

    def setUp(self):
        self.input = io.StringIO()
        self.output = io.StringIO()
        self.error = io.StringIO()
        # we use a Repl because it sets up the type environment for the type checker
        self.repl = repl.Repl(self.input, self.output, self.error)
        TypeVariable.reset_names()

    def tearDown(self):
        self.input = None
        self.output = None
        self.error = None
        self.repl = None

    def assertType(self, expected_type: str, expression: str):
        self.input.write(expression)
        self.input.seek(0)
        result = self.repl.reader.read()
        if result is None:
            self.fail("parse of '" + expression + "' failed: " + self.error.getvalue())
        analysis = result.analyse(self.repl.type_env)
        self.assertEqual(expected_type, str(analysis))

    def assertTypeFailure(self, expected_exception, expression: str):
        self.input.write(expression)
        self.input.seek(0)
        result = self.repl.reader.read()
        if result is None:
            self.fail("parse of '" + expression + "' failed: " + self.error.getvalue())
        with self.assertRaises(expected_exception):
            result.analyse(self.repl.type_env)

    def test_and(self):
        self.assertType('bool', '1 == 2 and true;')

    def test_length(self):
        self.assertType('int', 'length([]);')

    def test_add(self):
        self.assertType('int', '1 + 2;')

    def test_list_int(self):
        self.assertType('list(int)', '[1, 2];')

    def test_list_string(self):
        self.assertType('list(string)', '["a", "b"];')

    def test_nested_list(self):
        self.assertType('list(list(int))', '[[0, 1, 2], []];')

    def test_cons(self):
        self.assertType('list(int)', '1 @ [2];')

    def test_append(self):
        self.assertType('list(int)', '[1] @@ [2];')

    def test_factorial(self):
        self.assertType(
            '(int -> int)',
            """
            {
                fn factorial (n) {
                    if (n == 0) {
                        1
                    } else {
                        n * factorial(n - 1)
                    }
                }
                factorial
            }
            """
        )

    def test_polymorphic_len(self):
        self.assertType(
            '(list(a) -> int)',
            '''
            {
                fn len(list) {
                    if (list == []) {
                        0
                    } else {
                        1 + len(tail(list))
                    }
                }
                len
            }
            '''
        )

    def test_polymorphic_map(self):
        self.assertType(
            '((a -> b) -> (list(a) -> list(b)))',
            '''
            {
                fn map(func, list) {
                    if (list == []) {
                        []
                    } else {
                        func(head(list)) @ map(func, tail(list))
                    }
                }
                map
            }
            '''
        )

    def test_mixed_lists_fail(self):
        self.assertTypeFailure(PySchemeTypeError, '[0] @@ [true];')
        self.assertTypeFailure(PySchemeTypeError, '0 @ [true];')

    def test_mixed_nested_lists_fail(self):
        self.assertTypeFailure(PySchemeTypeError, '[[0]] @@ [[true]];')

    def test_non_polymorphic_fail(self):
        self.assertTypeFailure(PySchemeTypeError, 'fn (f) { [f(3), f(true)] };')

    def test_undefined_symbol(self):
        self.assertTypeFailure(SymbolNotFoundError, '[f(3), f(true)];')

    def test_occurs_check(self):
        self.assertTypeFailure(PySchemeInferenceError, 'fn (f) { f(f) };')

    def test_generic_non_generic(self):
        self.assertType(
            '(a -> list(a))',
            '''
            fn (g) {
                fn (f) {
                    [ f(2), f(3) ]
                }(fn(x) { g })
            };
            '''
        )

    def test_function_comp(self):
        self.assertType(
            '((a -> b) -> ((c -> a) -> (c -> b)))',
            '''
            fn (f) { fn (g) { fn (arg) { f(g(arg)) } } };
            '''
        )
