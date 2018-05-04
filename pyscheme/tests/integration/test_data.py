from pyscheme.tests.integration.base import Base


class TestData(Base):
    def test_list(self):
        self.assertEval(
            "[5, 6]",
            "[2 + 3, 3 + 3]"
        )


class TestOperations(Base):
    def test_addition(self):
        self.assertEval("10", "5 + 5")

    def test_equality(self):
        self.assertEval("true", "5 == 5")

    def test_and(self):
        self.assertEval("true", "true and true")
        self.assertEval("false", "true and false")
        self.assertEval("unknown", "true and unknown")
        self.assertEval("false", "false and true")
        self.assertEval("false", "false and false")
        self.assertEval("false", "false and unknown")
        self.assertEval("unknown", "unknown and true")
        self.assertEval("false", "unknown and false")
        self.assertEval("unknown", "unknown and unknown")

    def test_cons(self):
        self.assertEval(
            "[8, 10, 12]",
            "8 @ 10 @ [12]"
        )

    def test_cons2(self):
        self.assertEval(
            "[8, 10, 12]",
            "8 @ 10 @ 12 @ []"
        )

    def test_append(self):
        self.assertEval(
            "[8, 10, 12]",
            "[8] @@ [10] @@ [12]"
        )

    def test_append2(self):
        self.assertEval(
            "[8, 10, 12]",
            "[8, 10] @@ [12] @@ []"
        )