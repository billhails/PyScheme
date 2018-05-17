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
import io


class Base(TestCase):

    @classmethod
    def eval(cls, text: str, error_file: io.StringIO) -> str:
        in_file = io.StringIO(text)
        out_file = io.StringIO()
        repl = Repl(in_file, out_file, error_file)
        repl.run()
        return out_file.getvalue()

    def assertEval(self, expected: str, text: str, msg: str = ''):
        error_file = io.StringIO()
        result = self.eval(text, error_file)
        self.assertEqual(expected, result.rstrip(), msg + ' (stderr: "' + error_file.getvalue() + '")')
