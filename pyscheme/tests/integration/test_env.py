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


class TestEnv(Base):

    def test_anonymous_env(self):
        self.assertEval(
            "5",
            '''
            env e { // need a prototype env
                define x = 0;
                define y = 0;
            }
            fn (a:e) {
                a.x + a.y
            }(
                env {
                    define x = 2;
                    define y = 3
                }
            );
            ''',
            'environments are first class'
        )

    def test_anonymous_env_2(self):
        self.assertEval(
            '11',
            """
                env {
                    define x = 11
                }.x;
            """,
            'enviroments can be declared and accessed anonymously'
        )

    def test_named_env(self):
        self.assertEval(
            "11",
            """
            env x {
                fn double(x) { x * 2 }
                fn add1(x) { x + 1 }
            }
            
            x.add1(x.double(5));
            """,
            'environments are first class'
        )

    def test_nested_env(self):
        self.assertEval(
            '10',
            '''
            env a {
                fn bar() { 10 }
                env b {
                    fn foo() {
                        bar()
                    }
                }
            }
            
            a.b.foo();
            ''',
            "code can see definitions in enclosing environments"
        )

    def test_not_found(self):
        self.assertError(
            'SymbolNotFoundError: no_such_symbol',
            '''
            {
                no_such_symbol
            }
            '''
        )

    def test_redefine_error(self):
        self.assertError(
            'SymbolAlreadyDefinedError: x',
            '''
            define x = 10;
            define x = 10;
            '''
        )

    def test_redefine_scope_ok(self):
        self.assertEval(
            '10',
            '''
            {
                define x = 10;
                {
                    define x = 12;
                }
                x;
            }
            '''
        )

    def test_typedef_in_env(self):
        self.assertEval(
            'pair[2, pair[3, null]]',
            '''
            env e {
                typedef lst(t) {pair(t, lst(t)) | null }

                fn map {
                    (f, null) { null }
                    (f, pair(h, t)) { pair(f(h), map(f, t)) }
                }
            }

            fn test(e:e) {
                define l = e.pair(1, e.pair(2, e.null));
                e.map(1 +, l)
            }

            test(e);
            '''
        )

    def test_typedef_in_env_2(self):
        self.assertEval(
            'Closure([e:e]: { define l = e.pair[1, e.pair[2, e.null]] ; e.map[Lambda [#c]: { { +[1, #c] } }, l] })',
            '''
            env e {
                typedef lst(t) {pair(t, lst(t)) | null }

                fn map {
                    (f, null) { null }
                    (f, pair(h, t)) { pair(f(h), map(f, t)) }
                }
            }

            fn test(e:e) {
                define l = e.pair(1, e.pair(2, e.null));
                e.map(1 +, l)
            }

            test;
            '''
        )

    def test_typedef_in_env_3(self):
        self.assertEval(
            'Closure([#a, #b]: (TupleConstructor pair)[#a, #b])',
            '''
            env e {
                typedef lst(t) {pair(t, lst(t)) | null }
            }

            e.pair;
            '''
        )
