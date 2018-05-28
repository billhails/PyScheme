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


class TestInference(Base):

    def test_inference_1(self):
        self.assertError(
            'PySchemeTypeError: bool != int',
            '''
            1 == true;
            '''
        )

    def test_inference_2(self):
        self.assertError(
            'PySchemeTypeError: bool != int',
            '''
            fn (x) {
                x * 2
            }(true);
            '''
        )

    def test_inference_3(self):
        self.assertEval(
            "3\n3",
            '''
            fn len(l) {
                if (l == []) {
                    0
                } else {
                    1 + len(tail(l))
                }
            }
            
            len([1, 2, 3]);
            
            len([true, true, false]);
            '''
        )

    def test_inference_4(self):
        self.assertError(
            "PySchemeTypeError: int != bool",
            '''
            [1, 2, false];
            '''
        )

    def test_inference_5(self):
        self.assertError(
            "PySchemeTypeError: string != int",
            '''
            (0 @ []) @@ ("hello" @ []);
            '''
        )

    def test_inference_6(self):
        self.assertError(
            "PySchemeInferenceError: recursive unification",
            '''
            fn (f) { f(f) };
            '''
        )

    def test_inference_7(self):
        self.assertEval(
            "5",
            '''
            fn g (f) { 5 }

            g(g);
            '''
        )

    def test_inference_8(self):
        self.assertEval(
            "Closure([f]: { Lambda [g]: { { Lambda [arg]: { { g[f[arg]] } } } } })",
            '''
            fn (f) { fn (g) { fn (arg) { g(f(arg)) } } };
            ''',
            'function composition'
        )

    def test_inference_101(self):
        self.assertError(
            "PySchemeTypeError: bool != int",
            """
            if (length([])) {
                true
            } else {
                false
            }
            """,
            "'if' requires a boolean"
        )

    def test_inference_115(self):
        self.assertEval(
            "9",
            """
            env e {
                fn sum(x, y) { x + y }
            }
            fn g(x:e) {
                x.sum(4, 5)
            }
            g(e);
            """,
            ""
        )

    def test_inference_116(self):
        self.assertError(
            "PySchemeTypeError: bool != int",
            """
            env e {
                fn sum(x, y) { x + y }
            }
            fn g(x:e) {
                x.sum(4, true)
            }
            g(e);
            """,
            ""
        )

    def test_inference_130(self):
        self.assertError(
            "SymbolNotFoundError: nosumhere",
            """
            env e1 {
                fn sum(x, y) { x + y }
            }
            env e2 {
                fn nosumhere() { false }
            }
            fn g(e3:e1) {
                e3.sum(4, 5)
            }
            g(e2);
            """,
            "env type checking"
        )

    def test_inference_163(self):
        self.assertError(
            "MissingPrototypeError: a",
            """
            fn (a) {
                a.x + a.y
            }(
                env {
                    define x = 2;
                    define y = 3
                }
            );
            """,
            ""
        )

    def test_inference_179(self):
        self.assertEval(
            "true",
            """
            typedef named_list(t) { named(string, list(t)) }
            fn (x) {
                x == named("hello", [1, 2, 3])
            }(named("hello", [1, 2, 3]));
            """,
            ""
        )

    def test_inference_191(self):
        self.assertEval(
            "false",
            """
            typedef named_list(t) { named(string, list(t)) }
            fn (x) {
                x == named("hello", [1, 2, 3])
            }(named("goodbye", [1, 2, 3]));
            """,
            ""
        )

    def test_inference_204(self):
        self.assertError(
            "PySchemeTypeError: bool != string",
            """
            typedef named_list(t) { named(string, list(t)) }
            fn (x) {
                x == named("hello", [1, 2, 3])
            }(named(false, [1, 2, 3]));
            """,
            ""
        )

    def test_inference_216(self):
        self.assertError(
            "PySchemeTypeError: bool != int",
            """
            typedef named_list(t) { named(string, list(t)) }
            fn (x) {
                x == named("hello", [1, 2, 3])
            }(named("hello", [true, false]));
            """,
            ""
        )

    def test_inference_228(self):
        self.assertEval(
            "24",
            """
            fn factorial {
                (0) { 1 }
                (n) { n * factorial(n - 1) }
            }
            factorial(4);
            """,
            ""
        )