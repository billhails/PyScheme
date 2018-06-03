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

from .base import Base


class TestData(Base):
    def test_list(self):
        self.assertEval(
            "[5, 6]",
            "[2 + 3, 3 + 3];"
        )


class TestOperations(Base):
    def test_addition(self):
        self.assertEval("10", "5 + 5;")

    def test_subtraction(self):
        self.assertEval("3", "10 - 7;")

    def test_multiplication(self):
        self.assertEval("70", "10 * 7;")

    def test_division(self):
        self.assertEval("3", "10 / 3;")
        self.assertEval("2", "10 / 2 / 2;")
        self.assertEval("10", "10 / (2 / 2);")

    def test_modulus(self):
        self.assertEval("1", "10 % 3;")

    def test_equality(self):
        self.assertEval("true", "5 == 5;")

    def test_pow(self):
        self.assertEval("64", "(2 ** 2) ** 3;")
        self.assertEval("256", "2 ** 2 ** 3;")

    def test_inequality(self):
        self.assertEval("false", "5 == 6;")
        self.assertError("PySchemeTypeError: bool != int", "5 == unknown;")

    def test_list_equality(self):
        self.assertEval("true", "[5, 5] == [5, 5];")

    def test_list_inequality(self):
        self.assertEval("false", "[5, 5] == [5, 6];")
        self.assertEval("false", "[5, 6] == [5];")

    def test_and(self):
        self.assertEval("true", "true and true;")
        self.assertEval("false", "true and false;")
        self.assertEval("unknown", "true and unknown;")
        self.assertEval("false", "false and true;")
        self.assertEval("false", "false and false;")
        self.assertEval("false", "false and unknown;")
        self.assertEval("unknown", "unknown and true;")
        self.assertEval("false", "unknown and false;")
        self.assertEval("unknown", "unknown and unknown;")

    def test_or(self):
        self.assertEval("true", "true or true;")
        self.assertEval("true", "true or false;")
        self.assertEval("true", "true or unknown;")
        self.assertEval("true", "false or true;")
        self.assertEval("false", "false or false;")
        self.assertEval("unknown", "false or unknown;")
        self.assertEval("true", "unknown or true;")
        self.assertEval("unknown", "unknown or false;")
        self.assertEval("unknown", "unknown or unknown;")

    def test_xor(self):
        self.assertEval("false", "true xor true;")
        self.assertEval("true", "true xor false;")
        self.assertEval("unknown", "true xor unknown;")
        self.assertEval("true", "false xor true;")
        self.assertEval("false", "false xor false;")
        self.assertEval("unknown", "false xor unknown;")
        self.assertEval("unknown", "unknown xor true;")
        self.assertEval("unknown", "unknown xor false;")
        self.assertEval("unknown", "unknown xor unknown;")

    def test_not(self):
        self.assertEval("false", "not true;")
        self.assertEval("true", "not false;")
        self.assertEval("unknown", "not unknown;")

    def test_boolean_equality(self):
        for args in [
            ["true",    "true",    "true"],
            ["true",    "false",   "false"],
            ["true",    "unknown", "false"],
            ["false",   "true",    "false"],
            ["false",   "false",   "true"],
            ["false",   "unknown", "false"],
            ["unknown", "true",    "false"],
            ["unknown", "false",   "false"],
            ["unknown", "unknown", "true"],
        ]:
            with self.subTest(args=args):
                self.assertEval(args[2], args[0] + " == " + args[1] + ";")

    def test_cons(self):
        self.assertEval(
            "[8, 10, 12]",
            "8 @ 10 @ [12];"
        )

    def test_cons2(self):
        self.assertEval(
            "[8, 10, 12]",
            "8 @ 10 @ 12 @ [];"
        )

    def test_append(self):
        self.assertEval(
            "[8, 10, 12]",
            "[8] @@ [10] @@ [12];"
        )

    def test_append2(self):
        self.assertEval(
            "[8, 10, 12]",
            "[8, 10] @@ [12] @@ [];"
        )

    def test_head(self):
        self.assertEval(
            "5",
            "head([5, 5]);"
        )

    def test_tail(self):
        self.assertEval(
            "[5]",
            "tail([5, 5]);"
        )

    def test_tail2(self):
        self.assertEval(
            "[]",
            "tail([5]);"
        )

    def test_tail3(self):
        self.assertEval(
            "[]",
            "tail([]);"
        )

    def test_length(self):
        self.assertEval(
            "2",
            "length([5, 5]);"
        )


class TestConditional(Base):
    def test_if_true(self):
        self.assertEval(
            "10",
            """
                if (5 == 5) {
                    10;
                } else {
                    12;
                }
            """
        )

    def test_if_false(self):
        self.assertEval(
            "12",
            """
                if (5 == 6) {
                    10;
                } else {
                    12;
                }
            """
        )

    def test_lt(self):
        self.assertEval('true', '10 < 12;')

    def test_gt(self):
        self.assertEval('false', '10 > 12;')

    def test_le(self):
        self.assertEval('true', '10 <= 12;')

    def test_ge(self):
        self.assertEval('false', '10 >= 12;')

    def test_ne(self):
        self.assertEval('true', '10 != 12;')

    def test_list_comparison_1(self):
        self.assertEval('true', '[1, 2, 3] < [1, 2, 4];')

    def test_list_comparison_2(self):
        self.assertEval('true', '[1, 2, 3] < [1, 2, 3, 4];')

    def test_list_comparison_3(self):
        self.assertEval('true', '[1, 2, 3, 4] > [1, 2, 3];')

    def test_boolean_comparison(self):
        self.assertEval('true', 'false < unknown;')

    def test_boolean_comparison_2(self):
        self.assertEval('true', 'unknown < true;')

    def test_boolean_comparison_3(self):
        self.assertEval('true', 'false < true;')

    def test_string_comparison_1(self):
        self.assertEval('true', '"hello" > "goodbye";')

    def test_string_comparison_2(self):
        self.assertEval('false', '"hello" < "goodbye";')

    def test_string_comparison_3(self):
        self.assertEval('false', '"hello" <= "goodbye";')

    def test_string_comparison_4(self):
        self.assertEval('true', '"hello" == "hello";')

    def test_nothing(self):
        self.assertEval(
            '',
            'nothing;',
            'repl does not print nothing'
        )

    def test_nothing_comparison(self):
        self.assertEval(
            'true',
            'nothing == nothing;',
            'nothing is nothing'
        )
