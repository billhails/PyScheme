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


class TestStrings(Base):
    def test_strings_23(self):
        self.assertEval(
            "Hello, world!",
            """
            "Hello," @@ " world!";
            """,
            "append works on strings"
        )

    def test_strings_32(self):
        self.assertEval(
            "Hello",
            """
            'H' @ "ello";
            """,
            "cons works with chars and strings"
        )

    def test_strings_41(self):
        self.assertEval(
            "5",
            """
            length("hello");
            """,
            "length works on string"
        )

    def test_strings_50(self):
        self.assertEval(
            '["h", "e", "l", "l", "o"]',
            """
            {
                fn map {
                    (f, []) { [] }
                    (f, h @ t) { f(h) @ map(f, t) }
                }

                map( fn(c) { [c] }, "hello")
            }
            """,
            ""
        )