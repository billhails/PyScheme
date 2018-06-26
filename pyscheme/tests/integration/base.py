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
from pyscheme.repl import Repl
import pyscheme.expr as expr
from pyscheme.exceptions import PySchemeRunTimeError
import io
import re


class Base(TestCase):

    @classmethod
    def eval(cls, text: str, error_file: io.StringIO) -> tuple:
        in_file = io.StringIO(text)
        out_file = io.StringIO()
        expr.Symbol.reset()
        repl = Repl(in_file, out_file, error_file)
        repl.run()
        return out_file.getvalue(), error_file.getvalue()

    def assertEval(self, expected: str, text: str, msg: str=''):
        error_file = io.StringIO()
        result = self.eval(text, error_file)
        self.assertEqualsIgnoringWhitespace(expected, result[0].rstrip(), msg + ' (stderr: "' + result[1] + '")')

    def assertError(self, expected: str, text: str, msg: str=''):
        error_file = io.StringIO()
        result = self.eval(text, error_file)
        self.assertEqual(expected, result[1].rstrip(), msg)

    def assertRunTimeError(self, expected: str, text: str, msg: str=''):
        error_file = io.StringIO()
        error = ''
        try:
            result = self.eval(text, error_file)
        except PySchemeRunTimeError as e:
            error = e.message
        self.assertEqual(error, expected)

    def assertEqualsIgnoringWhitespace(self, expected: str, result: str, msg: str=''):
        self.assertEqual(self.removeWhitespace(expected), self.removeWhitespace(result), msg)

    def removeWhitespace(self, text: str):
        return re.sub('\s+', '', text)
