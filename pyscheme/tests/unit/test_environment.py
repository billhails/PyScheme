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
        a = expr.Symbol.make("a")
        b = expr.Constant(10)
        new_env = self.env.extend({a: b})
        c = None

        def cont(v):
            nonlocal c
            c = v

        new_env.lookup(a, cont)()  # we have to bounce the result to evaluate cont.
        self.assertEqual(b, c, "lookup should find a = 10")

    def test_failed_lookup(self):
        a = expr.Symbol.make("a")

        def cont(_):
            pass

        with self.assertRaises(SymbolNotFoundError):
            self.env.lookup(a, cont)


if __name__ == "__main__":
    unittest.main()
