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
