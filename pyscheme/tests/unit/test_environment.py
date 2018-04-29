import unittest
import pyscheme.environment as env


class TestEnvironment(unittest.TestCase):
    def setUp(self):
        self.env = env.Environment()

    def tearDown(self):
        self.env = None

    def test_environment_exists(self):
        self.assertIsInstance(self.env, env.Environment, "environment should be set up")


if __name__ == "__main__":
    unittest.main()