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


class TestMetacircular(Base):
    """
    tentative first steps
    """

    def test_metacircular_evaluator(self):
        self.assertEval(
            '11',
            '''
            {
                // very simple AST
                typedef expression {
                    plus(expression, expression) |
                    minus(expression, expression) |
                    times(expression, expression) |
                    divide(expression, expression) |
                    number(int) |
                    symbol(string)
                }

                // very simple environment
                typedef environment { frame(string, int, environment) | root }

                // an interpreter
                fn eval {
                    (plus(l, r), e) { eval(l, e) + eval(r, e) }
                    (minus(l, r), e) { eval(l, e) - eval(r, e) }
                    (times(l, r), e) { eval(l, e) * eval(r, e) }
                    (divide(l, r), e) { eval(l, e) / eval(r, e) }
                    (number(i), e) { i }
                    (symbol(s), e) { lookup(s, e) }
                }

                // lookup access to the environment
                fn lookup {
                    (s, frame(key, value, parent)) {
                        if (s == key) {
                            value
                        } else {
                            lookup(s, parent)
                        }
                    }
                    (s, root) { error("mce symbol not defined " @@ s) }
                }

                // try it out
                eval(
                    plus(
                        number(2),
                        times(
                            number(3),
                            symbol("a")
                        )
                    ),
                    frame("a", 3, frame("a", 2, root))
                );
            }
            '''
        )

    def test_metacircular_evaluator_2(self):
        self.assertEval(
            '11',
            '''
            {
                // very simple AST
                typedef expression {
                    plus(expression, expression) |
                    minus(expression, expression) |
                    times(expression, expression) |
                    divide(expression, expression) |
                    number(int) |
                    symbol(string)
                }

                // very simple environment
                typedef environment { frame(string, expression, environment) | root }

                // an interpreter
                fn eval {
                    (plus(l, r), e) { eval(l, e) + eval(r, e) }
                    (minus(l, r), e) { eval(l, e) - eval(r, e) }
                    (times(l, r), e) { eval(l, e) * eval(r, e) }
                    (divide(l, r), e) { eval(l, e) / eval(r, e) }
                    (number(i), e) { i }
                    (symbol(s), e) { lookup(s, e) }
                }

                // lookup access to the environment
                fn lookup {
                    (s, frame(key, number(value), parent)) {
                        if (s == key) {
                            value
                        } else {
                            lookup(s, parent)
                        }
                    }
                    (s, root) { error("mce symbol not defined " @@ s) }
                }

                // try it out
                eval(
                    plus(
                        number(2),
                        times(
                            number(3),
                            symbol("a")
                        )
                    ),
                    frame("a", number(3), frame("a", number(2), root))
                );
            }
            '''
        )
