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