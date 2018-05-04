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

    def test_inequality(self):
        self.assertEval("false", "5 == 6")
        self.assertEval("false", "5 == unknown")

    def test_list_equality(self):
        self.assertEval("true", "[5, 5] == [5, 5]")

    def test_list_inequality(self):
        self.assertEval("false", "[5, 5] == [5, 6]")
        self.assertEval("false", "[5, 6] == [5]")

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

    def test_or(self):
        self.assertEval("true", "true or true")
        self.assertEval("true", "true or false")
        self.assertEval("true", "true or unknown")
        self.assertEval("true", "false or true")
        self.assertEval("false", "false or false")
        self.assertEval("unknown", "false or unknown")
        self.assertEval("true", "unknown or true")
        self.assertEval("unknown", "unknown or false")
        self.assertEval("unknown", "unknown or unknown")

    def test_xor(self):
        self.assertEval("false", "true xor true")
        self.assertEval("true", "true xor false")
        self.assertEval("unknown", "true xor unknown")
        self.assertEval("true", "false xor true")
        self.assertEval("false", "false xor false")
        self.assertEval("unknown", "false xor unknown")
        self.assertEval("unknown", "unknown xor true")
        self.assertEval("unknown", "unknown xor false")
        self.assertEval("unknown", "unknown xor unknown")

    def test_not(self):
        self.assertEval("false", "not true")
        self.assertEval("true", "not false")
        self.assertEval("unknown", "not unknown")

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


class TestConditional(Base):
    def test_if_true(self):
        self.assertEval("10", "if (5 == 5) { 10 } else { 12 }")

    def test_if_false(self):
        self.assertEval("12", "if (5 == 6) { 10 } else { 12 }")
