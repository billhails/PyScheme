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
            'number[5]',
            '''
            {
                // very simple environment
                typedef environment { frame(string, expression, environment) | root }
            
                // very simple AST
                typedef expression {
                    addition(expression, expression) |
                    subtraction(expression, expression) |
                    multiplication(expression, expression) |
                    division(expression, expression) |
                    number(int) |
                    symbol(string) |
                    conditional(expression, expression, expression) |
                    lambda(expression, expression) |
                    closure(expression, environment) |
                    application(expression, expression)
                }
            
                // an interpreter
                fn eval {
                    (addition(l, r), e)              { add(eval(l, e), eval(r, e)) }
                    (subtraction(l, r), e)           { sub(eval(l, e), eval(r, e)) }
                    (multiplication(l, r), e)        { mul(eval(l, e), eval(r, e)) }
                    (division(l, r), e)              { div(eval(l, e), eval(r, e)) }
                    (i = number(_), e)               { i }
                    (symbol(s), e)                   { lookup(s, e) }
                    (conditional(test, pro, con), e) { cond(test, pro, con, e) }
                    (l = lambda(symbol(_), body), e) { closure(l, e) }
                    (application(function, arg), e)  { apply(eval(function, e), eval(arg, e)) }
                }
                
                // function application
                fn apply {
                    (closure(lambda(symbol(s), body), e), arg) {
                        eval(body, frame(s, arg, e))
                    }
                }
                
                // built-ins
                fn add { (number(a), number(b)) { number(a + b) } }
                fn sub { (number(a), number(b)) { number(a - b) } }
                fn mul { (number(a), number(b)) { number(a * b) } }
                fn div { (number(a), number(b)) { number(a / b) } }
                fn cond(test, pro, con, e) {
                    fn {
                        (number(0)) { eval(con, e) } // 0 is false
                        (number(_)) { eval(pro, e) }
                    }(eval(test, e))
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
            
                // try it out: ((lambda (x) (if x (+ x 2) x)) a) |- a: 3
                eval(
                    application(
                        lambda(
                            symbol("x"),
                            conditional(
                                symbol("x"),
                                addition(symbol("x"), number(2)),
                                symbol("x")
                            )
                        ),
                        symbol("a")
                    ),
                    frame("a", number(3), root)
                );
            }
            '''
        )
