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
from pyscheme.exceptions import TypeSymbolNotFoundError, PySchemeInferenceError, PySchemeTypeError
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

    def assertTypes(self, expected_types: list, expression: str):
        self.input.write(expression)
        self.input.seek(0)
        analysis = []
        while True:
            result = self.repl.reader.read()
            if result is None:
                break
            analysis += [str(result.analyse(self.repl.type_env))]
        self.assertEqual(expected_types, analysis)

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
        self.assertType('list(list(char))', '["a", "b"];')

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
            '(list(#b) -> int)',
            '''
            {
                fn len(lst) {
                    if (lst == []) {
                        0
                    } else {
                        1 + len(tail(lst))
                    }
                }
                len
            }
            '''
        )

    def test_polymorphic_map(self):
        self.assertType(
            '((#c -> #d) -> (list(#c) -> list(#d)))',
            '''
            {
                fn map(func, lst) {
                    if (lst == []) {
                        []
                    } else {
                        func(head(lst)) @ map(func, tail(lst))
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
        self.assertTypeFailure(TypeSymbolNotFoundError, '[f(3), f(true)];')

    def test_occurs_check(self):
        self.assertTypeFailure(PySchemeInferenceError, 'fn (f) { f(f) };')

    def test_override_check(self):
        self.assertTypeFailure(
            PySchemeInferenceError,
            '''
            {
                typedef colour { red | green }
                {
                    define red = 5;
                }
            }
            '''
        )

    def test_override_check_2(self):
        self.assertTypeFailure(
            PySchemeInferenceError,
            '''
            {
                typedef colour { red | green }
                {
                    typedef colours { red | blue }
                }
            }
            '''
        )

    def test_generic_non_generic(self):
        self.assertType(
            '(#a -> list(#a))',
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
            '((#a -> #b) -> ((#c -> #a) -> (#c -> #b)))',
            '''
            fn (f) { fn (g) { fn (arg) { f(g(arg)) } } };
            '''
        )

    def test_builtin_type(self):
        self.assertType(
            '(list(char) -> (list(#b) -> named_list(#b)))',
            '''
            {
            typedef named_list(#t) { named(list(char), list(#t)) }
            named;
            }
            '''
        )

    def test_composite_type(self):
        self.assertType(
            '((#c -> #d) -> (list(#c) -> list(#d)))',
            '''
            {
                fn map {
                    (f, []) { [] }
                    (f, h @ t) { f(h) @ map(f, t) }
                }
                map;
            }
            '''
        )

    def test_composite_with_user_types(self):
        self.assertType(
            '((#c -> #d) -> (l(#c) -> l(#d)))',
            '''
            {
                typedef l(#t) { p(#t, l(#t)) | n }
                fn map {
                    (f, n)       { n }
                    (f, p(h, t)) { p(f(h), map(f, t)) }
                }
                map;
            }
            '''
        )

    def test_composite_with_constants(self):
        self.assertType(
            '(int -> int)',
            '''
            {
                fn factorial {
                    (0) { 1 }
                    (n) { n * factorial(n - 1) }
                }
                factorial;
            }
            '''
        )

    def test_composite_with_constants_2(self):
        self.assertType(
            '(l(#b) -> int)',
            '''
            {
                typedef l(#t) { p(#t, l(#t)) | n }
                fn len {
                    (n) { 0 }
                    (p(h, t)) { 1 + len(t) }
                }
                len;
            }
            '''
        )

    def test_composite_with_call(self):
        self.assertType(
            'int',
            '''
            {
                typedef lst(#t) { pair(#t, lst(#t)) | null }
                fn len {
                    (null) { 0 }
                    (pair(h, t)) { 1 + len(t) }
                }
                len(pair(1, pair(2, pair(3, null))));
            }
            '''
        )

    def test_composite_with_call_type(self):
        self.assertTypes(
            ['lst(#a)', 'nothing', '(lst(#b) -> int)'],
            '''
                typedef lst(#t) { pair(#t, lst(#t)) | null }

                fn len {
                    (null) { 0 }
                    (pair(h, t)) { 1 + len(t) }
                }
                
                len;
            
            '''
        )

    def test_filter(self):
        self.assertType(
            '((#b -> bool) -> (list(#b) -> list(#b)))',
            '''
            {
                fn filter {
                        (f, []) { [] }
                        (f, h @ t) {
                            if (f(h)) {
                                h @ filter(f, t)
                            } else {
                                filter(f, t)
                            }
                        }
                    }
                filter
            }
            '''
        )

    def test_qsort(self):
        self.assertType(
            '(list(#e) -> list(#e))',
            '''
            {
                fn qsort {
                    ([]) { [] }
                    (pivot @ rest) {
                        define lesser = filter(ge(pivot), rest);
                        define greater = filter(lt(pivot), rest);
                        qsort(lesser) @@ [pivot] @@ qsort(greater)
                    }
                }

                fn lt(a, b) { a < b }

                fn ge(a, b) { a >= b }

                fn filter {
                    (f, []) { [] }
                    (f, h @ t) {
                        if (f(h)) {
                            h @ filter(f, t)
                        } else {
                            filter(f, t)
                        }
                    }
                }

                qsort
            }
            '''
        )

    def test_filter_type(self):
        self.assertTypes(
            [
                'nothing',
                '((#a -> bool) -> (list(#a) -> list(#a)))',
            ],
            '''
                fn filter {
                    (f, []) { [] }
                    (f, h @ t) {
                        if (f(h)) {
                            h @ filter(f, t)
                        } else {
                            filter(f, t)
                        }
                    }
                }

                filter;
            
            '''
        )

    def test_ge(self):
        self.assertType(
            '(#b -> (#b -> bool))',
            '''
            {
                fn ge(a, b) { a >= b }
                ge
            }
            '''
        )

    def test_env(self):
        self.assertTypes(
            [
                'nothing',
                '(#a -> (lst(#a) -> lst(#a)))'
            ],
            '''
            env e {
                typedef lst(#t) {pair(#t, lst(#t)) | null }
            }

            e.pair;
            '''
        )

    def test_meta(self):
        self.assertType(
            '(expression(#b) -> (expression(#b) -> expression(#b)))',
            '''
            {
                typedef expression(#t) {
                    plus(expression(#t), expression(#t)) |
                    minus(expression(#t), expression(#t)) |
                    times(expression(#t), expression(#t)) |
                    divide(expression(#t), expression(#t)) |
                    number(#t) |
                    symbol(list(char))
                }

                plus;
            }
            '''
        )

    def test_meta_2(self):
        self.assertType(
            '(expression -> (expression -> expression))',
            '''
            {
                typedef expression {
                    plus(expression, expression) |
                    minus(expression, expression) |
                    times(expression, expression) |
                    divide(expression, expression) |
                    number(int) |
                    symbol(list(char))
                }

                plus;
            }
            '''
        )

    def test_inference_multiple_functions(self):
        self.assertType(
            '(int -> (int -> int))',
            '''
            {
                fn add (x, y) {
                    x + y
                }
                
                 fn f1 (a, b) {
                    add(a, b)
                }
                
               f1
            }
            '''
        )
