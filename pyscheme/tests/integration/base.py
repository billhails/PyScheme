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
from pyscheme.stream import StringStream
import io


class Base(TestCase):
    def eval(self, expr: str) -> str:
        stream_expr = StringStream(expr)
        output = io.StringIO()
        repl = Repl(stream_expr, output)
        repl.run()
        return output.getvalue()

    def assertEval(self, expected: str, expr: str, msg: str = ''):
        result = self.eval(expr)
        self.assertEqual(expected, result, msg)
