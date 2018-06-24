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

    def test_metacircular_compiler(self):
        self.assertEval(
            'number[5]',
            '''
            {
                // very simple environment
                typedef Environment(#t) { frame(string, #t, Environment) | root }

                // very simple AST
                typedef Expression {
                    addition(Expression, Expression) |
                    subtraction(Expression, Expression) |
                    multiplication(Expression, Expression) |
                    division(Expression, Expression) |
                    number(int) |
                    variable(string) |
                    conditional(Expression, Expression, Expression) |
                    lambda(Expression, Expression) |
                    application(Expression, Expression) |
                    definition(Expression, Expression)
                }
                
                // registers
                typedef Register {
                    envt | val | continue | argl | proc | val1 | val2
                }
                
                define all_regs = [envt, val, continue, argl, proc, val1, val2];
                
                // binary operators
                typedef Binop {
                    add | sub | mul | div
                }
                
                // labels
                typedef Label { label(string) }

                // linkage
                typedef Linkage {
                    next |
                    return |
                    jump(Label)
                }

                // locations
                typedef Location {
                    location_register(Register) |
                    location_env(string)
                }
                
                // machine addresses
                typedef Address {
                    address_register(Register) |
                    address_label(Label)
                }
                
                // values
                typedef Value {
                    value_const(int) |
                    value_register(Register) |
                    value_lookup(string) |
                    value_procedure(Label, Register) |
                    value_procedure_env(Register) |
                    value_extend_env(string, Register, Register) |
                    value_binop(Binop, Value, Value) |
                    value_isprimitive |
                    value_apply_primitive(Register, Register) |
                    value_label(Label) |
                    value_compiled_procedure_entry(Register)
                }
                
                typedef Instruction {
                    goto(Address) |
                    assign(Register, Value) |
                    set(Location, Value) |
                    test(Location, Value, Label) |
                    tag(Label)
                }

                typedef InstructionSequence {
                    sequence(list(Register), list(Register), list(Instruction)) | empty
                }
                
                fn compile_linkage {
                    (return) {
                        sequence([continue], [], [goto(address_register(continue))])
                    }
                    (next) {
                        empty
                    }
                    (jump(l)) {
                        sequence([], [], [goto(address_label(l))])
                    }
                }

                fn end_with_linkage(linkage, seq) {
                    preserving([continue], seq, compile_linkage(linkage))
                }
                
                fn preserving(registers, instructions, linkage_instructions) {
                    // TODO
                }

                // a compiler
                fn compile (expr, target, linkage) {
                    fn {
                        (addition(l, r)) {
                            compile_binop(add, l, r, target, linkage)
                        }
                        (subtraction(l, r)) {
                            compile_binop(sub, l, r, target, linkage)
                        }
                        (multiplication(l, r)) {
                            compile_binop(mul, l, r, target, linkage)
                        }
                        (division(l, r)) {
                            compile_binop(div, l, r, target, linkage)
                        }
                        (number(i)) {
                            compile_number(i, target, linkage)
                        }
                        (variable(s)) {
                            compile_variable(s, target, linkage)
                        }
                        (conditional(t3st, consequent, alternative)) {
                            compile_conditional(t3st, consequent, alternative, target, linkage)
                        }
                        (lambda(variable(v), body)) {
                            compile_lambda(v, body, target, linkage)
                        }
                        (application(func, arg)) {
                            compile_application(func, arg, target, linkage)
                        }
                        (definition(variable(v), expr)) {
                            compile_definition(v, expr, target, linkage)
                        }
                    }(expr);
                }
                
                fn compile_binop(op, l, r, target, linkage) {
                    end_with_linkage(
                        linkage,
                        append_instruction_sequences(
                            [
                                compile(l, val1, next),
                                compile(l, val2, next),
                                sequence(
                                    [val1, val2],
                                    [target],
                                    [assign(target, value_binop(op, value_register(val1), value_register(val2)))]
                                )
                            ]
                        )
                    )
                }
                
                fn compile_number(n, target, linkage) {
                    end_with_linkage(
                        linkage,
                        sequence([], [target], [assign(target, value_const(n))])
                    )
                }
                
                fn compile_variable(v, target, linkage) {
                    end_with_linkage(
                        linkage,
                        sequence(
                            [envt],
                            [target], 
                            [assign(target, value_lookup(v))]
                        )
                    )
                }

                fn compile_definition(v, expr, target, linkage) {
                    end_with_linkage(
                        linkage,
                        preserving(
                            [envt],
                            compile(expr, val, next),
                            sequence(
                                [envt, val],
                                [target],
                                [
                                    set(location_env(v), value_register(val)),
                                    assign(target, value_const(0))
                                ]
                            )
                        )
                    )
                }
                
                fn compile_conditional(t3st, consequent, alternative, target, linkage) {
                    define t_branch = label("true-branch");
                    define f_branch = label("false-branch");
                    define after_if = label("after-if");
                    define consequent_linkage =
                        if (linkage == next) {
                            jump(after_if)
                        } else {
                            linkage
                        };
                    define p_code = compile(t3st, val, next);
                    define c_code = compile(consequent, target, consequent_linkage);
                    define a_code = compile(alternative, target, linkage);
                    preserving(
                        [envt, continue],
                        p_code,
                        append_instruction_sequences(
                            [
                                sequence(
                                    [val],
                                    [],
                                    [
                                        test(location_register(val), value_const(0), f_branch)
                                    ]
                                ),
                                parallel_instruction_sequences(
                                    label_instruction_sequence(t_branch, c_code),
                                    label_instruction_sequence(f_branch, a_code)
                                ),
                                label_instruction_sequence(after_if, empty)
                            ]
                        )
                    )
                }

                fn label_instruction_sequence {
                    (l = label(_), sequence(needs, modifies, instructions)) {
                        sequence(needs, modifies, tag(l) @ instructions)
                    }
                    (l = label(_), empty) {
                        sequence([], [], [tag(l)])
                    }
                }

                fn compile_lambda (arg, body, target, linkage) {
                    define proc_entry = label("entry");
                    define after_lambda = label("after-lambda");
                    define lambda_linkage =
                        if (linkage == next) {
                            jump(after_lambda)
                        } else {
                            linkage
                        };
                    append_instruction_sequences(
                        [
                            tack_on_instruction_sequence(
                                end_with_linkage(
                                    lambda_linkage,
                                    sequence(
                                        [envt],
                                        [target],
                                        [assign(target, value_procedure(proc_entry, envt))]
                                    ),
                                    compile_lambda_body(arg, body, proc_entry)
                                )
                            ),
                            label_instruction_sequence(after_lambda, empty)
                        ]
                    )
                }
                
                fn compile_lambda_body(arg, body, proc_entry) {
                    append_instruction_sequences(
                        [
                            sequence(
                                [envt, proc, argl],
                                [envt],
                                [
                                    tag(proc_entry),
                                    assign(envt, value_procedure_env(proc)),
                                    assign(envt, value_extend_env(arg, argl, envt)),
                                ]
                            ),
                            compile(body, val, return)
                        ]
                    )
                }
                
                fn compile_application(func, arg, target, linkage) {
                    define proc_code = compile(func, proc, next);
                    define arg_code = compile(arg, val, next);
                    preserving(
                        [envt, continue],
                        proc_code,
                        preserving(
                            [proc, continue],
                            arg_code,
                            compile_procedure_call(target, linkage)
                        )
                    )
                }
                
                fn compile_procedure_call(target, linkage) {
                    define primitive_branch = label("primitive-branch");
                    define compiled_branch = label("compiled-branch");
                    define after_call = label("after-call");
                    define compiled_linkage =
                        if (linkage == next) {
                            jump(after_call)
                        } else {
                            linkage
                        };
                    append_instruction_sequences(
                        [
                            sequence(
                                [proc],
                                [],
                                [test(location_register(proc), value_isprimitive, primitive_branch)]
                            ),
                            parallel_instruction_sequences(
                                label_instruction_sequence(
                                    compiled_branch,
                                    compile_proc_appl(target, compiled_linkage)
                                ),
                                label_instruction_sequence(
                                    primitive_branch,
                                    end_with_linkage(
                                        linkage,
                                        sequence(
                                            [proc, argl],
                                            [target],
                                            [
                                                assign(target, value_apply_primitive(proc, argl))
                                            ]
                                        )
                                    )
                                )
                            )
                        ]
                    )
                }
                
                fn compile_proc_appl {
                    (val, return) {
                        sequence(
                            [proc, continue],
                            all_regs,
                            [assign(val, value_compiled_procedure_entry(proc))]
                        )
                    }
                    (val, jump(lab)) {
                        sequence(
                            [proc],
                            all_regs,
                            [
                                assign(continue, value_label(lab)),
                                assign(val, value_compiled_procedure_entry(proc))
                            ]
                        )
                    }
                    (_, return) {
                        error("MCC - return linkage, but target is not val")
                    }
                    (target, linkage) {
                        define proc_return = label("proc-return");
                        sequence(
                            [proc],
                            all_regs,
                            [
                                assign(continue, value_label(proc_return)),
                                assign(val, value_compiled_procedure_entry(proc))
                            ]
                        )
                    }
                    
                }
                
                fn append_instruction_sequences {
                    ([]) { empty }
                    (h @ t) {
                        append_two_sequences(h, append_instruction_sequences(t))
                    }
                }
                
                fn append_two_sequences {
                    (empty, b) { b }
                    (a, empty) { a }
                    (sequence(need1, used1, instr1), sequence(need2, used2, instr2)) {
                        sequence(
                            union(need1, difference(need2, used1)),
                            union(used1, used2),
                            instr1 @@ instr2
                        )
                    }
                }
                
                fn parallel_instruction_sequences {
                    (empty, b) { b }
                    (a, empty) { a }
                    (sequence(need1, used1, instr1),
                     sequence(need2, used2, instr2)) {
                        sequence(
                            union(need1, need2),
                            union(used1, used2),
                            instr1 @@ instr2
                        )
                    }
                }
                
                fn tack_on_instruction_sequence {
                    (empty, b) { b }
                    (a, empty) { a }
                    (sequence(need1, used1, instr1),
                     sequence(_, _, instr2)) {
                        sequence(
                            need1,
                            used1,
                            instr1 @@ instr2
                        )
                    }
                }
                
                fn member {
                    (s, []) { false }
                    (s, s @ _) { true }
                    (s, h @ t) { member(s, t) }
                }
                
                fn union {
                    ([], l)    { l }
                    (h @ t, l) {
                        if (member(h, l)) {
                            union(t, l)
                        } else {
                            h @ union(t, l)
                        }
                    }
                }
                
                fn difference {
                    ([], _) { [] }
                    (h @ t, l) {
                        if (member(h, l)) {
                            difference(t, l)
                        } else {
                            h @ difference(t, l)
                        }
                    }
                }

                // try it out: ((lambda (x) (if x (+ x 2) x)) a) |- a: 3
                compile(
                    application(
                        lambda(
                            variable("x"),
                            conditional(
                                variable("x"),
                                addition(variable("x"), number(2)),
                                variable("x")
                            )
                        ),
                        variable("a")
                    ),
                    val,
                    next
                );
            }
            '''
        )
