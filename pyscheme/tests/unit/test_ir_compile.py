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
        tree = result.compile(self.repl.compile_time_env)
        self.assertEqual(expected_result, str(tree), msg)

    def test_compile_arithmetic(self):
        self.assertIrCompile('', '2 + 2;', '')