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

class TestParser(TestCase):

    def assertParse(self, expected, input, message=''):
        input_file = io.StringIO(input)
        stderr = io.StringIO()
        tokeniser = reader.Tokeniser(input_file)
        parser = reader.Reader(tokeniser, stderr)
        self.assertEqual(expected, str(parser.read()), stderr.getvalue())

    def test_parse_basic(self):
        self.assertParse("1", "1")

    def test_parse_arithmetic(self):
        self.assertParse(
            "Application(+: [1, Application(*: [2, 3])])",
            "1 + 2 * 3;",
            "basic arithmetic precedence works"
        )

    def test_parse_funcall(self):
        self.assertParse(
            "Application(foo: [bar])",
            "foo(bar);",
            "function application works"
        )

    def test_parse_then_funcall(self):
        self.assertParse(
            "Application(then: [foo, Application(bar: [baz])]);",
            "foo then bar(baz);"
        )

    def test_parse_then_funcall_2(self):
        self.assertParse(
            "Application(Application(then: [foo, bar]): [baz]);",
            "(foo then bar)(baz);"
        )