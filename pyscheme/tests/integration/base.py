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
