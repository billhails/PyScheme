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
                    (l = lambda(_, _), e)            { closure(l, e) }
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
                    (s, frame(s, value, _))  { value }
                    (s, frame(_, _, parent)) { lookup(s, parent) }
                    (s, root)                { error("mce symbol not defined " @@ s) }
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


    def test_metacircular_compiler_it_takes_too_long(self):
        self.assertEval(
            '''
            sequence[
                [envt, argl],
                [envt, continue, argl, proc, val1, val2, val],
                [
                    assign[proc, value_procedure[label[entry], envt]],
                    goto[address_label[label[after-lambda]]],
                    tag[label[entry]],
                    assign[envt, value_procedure_env[proc]],
                    assign[envt, value_extend_env[x, argl, envt]],
                    assign[val, value_lookup[x]],
                    test[location_register[val], value_const[0], label[false-branch]],
                    tag[label[true-branch]],
                    assign[val1, value_lookup[x]],
                    assign[val2, value_const[2]],
                    assign[val, value_binop[add, value_register[val1], value_register[val2]]],
                    goto[address_register[continue]],
                    tag[label[false-branch]],
                    assign[val, value_lookup[x]],
                    goto[address_register[continue]],
                    tag[label[after-if]],
                    tag[label[after-lambda]],
                    assign[val, value_const[3]],
                    test[location_register[proc], value_isprimitive, label[primitive-branch]],
                    tag[label[compiled-branch]],
                    assign[continue, value_label[label[after-call]]],
                    assign[val, value_compiled_procedure_entry[proc]],
                    tag[label[primitive-branch]],
                    assign[val, value_apply_primitive[proc, argl]],
                    tag[label[after-call]]
                ]
            ]
            ''',
            '''
            
            load utils.compiler as compiler;
            
            env t extends compiler {
                // try it out: ((lambda (x) (if x (+ x 2) x)) 3)
                result = compile(
                    application(
                        lambda(
                            variable("x"),
                            conditional(
                                variable("x"),
                                addition(variable("x"), number(2)),
                                variable("x")
                            )
                        ),
                        number(3)
                    ),
                    val,
                    next
                );
            }
            
            t.result;
            '''
        )
