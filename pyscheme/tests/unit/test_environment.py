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

import unittest
import pyscheme.environment as env
import pyscheme.expr as expr
from pyscheme.exceptions import SymbolNotFoundError


class TestEnvironment(unittest.TestCase):
    def setUp(self):
        self.env = env.Environment()

    def tearDown(self):
        self.env = None

    def test_environment_exists(self):
        self.assertIsInstance(self.env, env.Environment, "environment should be set up")

    def test_lookup(self):
        a = expr.Symbol("a")
        b = expr.Constant(10)
        new_env = self.env.extend({a: b})
        c = None

        def cont(v, amb):
            nonlocal c
            c = v

        new_env.lookup(a, cont, lambda: None)()  # we have to bounce the result to evaluate cont.
        self.assertEqual(b, c, "lookup should find a = 10")

    def test_failed_lookup(self):
        a = expr.Symbol("a")

        def cont(_, amb):
            pass

        with self.assertRaises(SymbolNotFoundError):
            self.env.lookup(a, cont, lambda: None)


if __name__ == "__main__":
    unittest.main()
