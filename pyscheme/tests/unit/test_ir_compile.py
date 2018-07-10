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
import pyscheme.repl as repl
from pyscheme.inference import TypeVariable
import re
import pyscheme.ir.tree as ir

class TestIrCompile(TestCase):

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

    def assertIrCompile(self, expected_result: str, expression: str, msg=''):
        self.input.write(expression)
        self.input.seek(0)
        result = self.repl.reader.read()
        if result is None:
            self.fail("parse of '" + expression + "' failed: " + self.error.getvalue())
        result.analyse(self.repl.type_env)
        ir.reset_counters()
        tree = result.compile(self.repl.compile_time_env)
        self.assertEqual(re.sub('\s+', '', expected_result),
                         re.sub('\s+', '', str(tree)),
                         msg)

    def test_compile_add(self):
        self.assertIrCompile('Seq(Temp(1) = Add(Int(2), Int(2)))', '2 + 2;', '')

    def test_compile_sub(self):
        self.assertIrCompile('''
        Seq(
            Temp(2) = Add(Int(2), Int(2)),
            Temp(3) = Sub(Temp(2), Int(3))
        )
        ''', '2 + 2 - 3;', '')

    def test_compile_mul(self):
        self.assertIrCompile(
            '''
            Seq(
                Temp(3) = Mul(Int(2), Int(5)),
                Temp(4) = Add(Int(2), Temp(3)),
                Temp(5) = Sub(Temp(4), Int(3))
            )
            ''', '2 + 2 * 5 - 3;', '')

    def test_compile_div(self):
        self.assertIrCompile(
            '''
            Seq(
                Temp(3) = Div(Int(2), Int(5)),
                Temp(4) = Add(Int(2), Temp(3)),
                Temp(5) = Sub(Temp(4), Int(3))
            )
            ''', '2 + 2 / 5 - 3;', '')

    def test_compile_mod(self):
        self.assertIrCompile(
            '''
            Seq(
                Temp(3) = Mod(Int(2), Int(5)),
                Temp(4) = Add(Int(2), Temp(3)),
                Temp(5) = Sub(Temp(4), Int(3))
            )
            ''',
            '2 + 2 % 5 - 3;', ''
        )

    def test_compile_pow(self):
        self.assertIrCompile(
            '''
            Seq(
                Temp(3) = Pow(Int(2), Int(5)),
                Temp(4) = Add(Int(2), Temp(3)),
                Temp(5) = Sub(Temp(4), Int(3))
            )
            ''',
            '2 + 2 ** 5 - 3;', '')

    def test_compile_eq(self):
        self.assertIrCompile('Seq(Temp(1) = Eq(Int(2), Int(2)))', '2 == 2;', '')

    def test_compile_ne(self):
        self.assertIrCompile('Seq(Temp(1) = Ne(Int(2), Int(2)))', '2 != 2;', '')

    def test_compile_gt(self):
        self.assertIrCompile('Seq(Temp(1) = Gt(Int(2), Int(2)))', '2 > 2;', '')

    def test_compile_lt(self):
        self.assertIrCompile('Seq(Temp(1) = Lt(Int(2), Int(2)))', '2 < 2;', '')

    def test_compile_ge(self):
        self.assertIrCompile('Seq(Temp(1) = Ge(Int(2), Int(2)))', '2 >= 2;', '')

    def test_compile_le(self):
        self.assertIrCompile('Seq(Temp(1) = Le(Int(2), Int(2)))', '2 <= 2;', '')

    def test_compile_and(self):
        self.assertIrCompile('Seq(Temp(1) = And(Int(1), Int(0)))', 'true and false;', '')

    def test_compile_or(self):
        self.assertIrCompile('Seq(Temp(1) = Or(Int(1), Int(0)))', 'true or false;', '')

    def test_compile_xor(self):
        self.assertIrCompile('Seq(Temp(1) = Xor(Int(1), Int(0)))', 'true xor false;', '')

    def test_compile_not(self):
        self.assertIrCompile('Seq(Temp(1) = Not(Int(1)))', 'not true;', '')

    def test_compile_if(self):
        self.assertIrCompile(
            '''
            Seq(
                Cjmp(Int(1), Label(if_true_0), Label(if_false_1)),
                Label(if_true_0),
                Temp(0) = Int(1),
                Jmp(Label(after_2)),
                Label(if_false_1),
                Temp(0) = Int(0),
                Label(after_2)
            )
            ''',
            'if (true) { 1 } else { 0 };'
        )

    def test_compile_list(self):
        self.assertIrCompile(
            '''
            Seq(
                Rec(Temp(0),2),
                SetRec(Temp(0),0,Int(2)),
                SetRec(Temp(0),1,Int(0)),
                Rec(Temp(1),2),
                SetRec(Temp(1),0,Int(1)),
                SetRec(Temp(1),1,Temp(0))
            )
            ''',
            '[1, 2];'
        )

    def test_compile_cons_1(self):
        self.assertIrCompile(
            '''
            Seq(
                Rec(Temp(2),2),
                SetRec(Temp(2),0,Int(1)),
                SetRec(Temp(2),1,Int(0))
            )
            ''',
            '1 @ [];'
        )

    def test_compile_cons_2(self):
        self.assertIrCompile(
            '''
            Seq(
                Rec(Temp(4),2),
                SetRec(Temp(4),0,Int(3)),
                SetRec(Temp(4),1,Int(0)),
                Rec(Temp(6),2),
                SetRec(Temp(6),0,Int(2)),
                SetRec(Temp(6),1,Temp(4)),
                Rec(Temp(8),2),
                SetRec(Temp(8),0,Int(1)),
                SetRec(Temp(8),1,Temp(6))
            )
            ''',
            '1 @ 2 @ 3 @ [];'
        )

    def test_compile_definition(self):
        self.assertIrCompile(
            '''
            Seq(
                Temp(0) = Int(10),
                Env(0, 0) = Temp(0)
            )
            ''',
            'a = 10;'
        )

    def test_compile_define_lambda_no_args(self):
        self.assertIrCompile(
            '''
            Seq(
                ExtendEnv(0),
                Temp(0) = Add(Int(2), Int(2)),
                PopEnv(),
                Env(0, 0) = Temp(0)
            )
            ''',
            'fn foo() { 2 + 2 }'
        )

    def test_compile_define_lambda_args(self):
        self.assertIrCompile(
            '''
            xxx
            ''',
            'fn square(x) { x * x }'
        )
