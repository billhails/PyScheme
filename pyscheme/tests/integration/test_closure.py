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


class TestClosure(Base):
    def test_simple_lambda(self):
        self.assertEval(
            "Closure([x]: x)",
            "fn (x) { x }"
        )

    def test_simple_lambda_application(self):
        self.assertEval("12", "fn (a) { a + a }(6)")

    def test_lambda_application(self):
        self.assertEval(
            "10",
            """
                fn (double) {
                    double(5)
                }(fn (a) { a + a })
            """
        )

    def test_closure_capture(self):
        self.assertEval(
            "7",
            """
                fn (add2) {
                    add2(5)
                }(
                    fn (a) {
                        fn (b) { a + b }
                    }(2)
                )
            """
        )

    def test_lambda_string(self):
        self.assertEval(
            "Closure([a]: if (Application(==: [a, 2])) {12} else {Lambda []: { 14 }})",
            "fn (a) { if (a == 2) { 12 } else { fn () { 14 } } }"
        )