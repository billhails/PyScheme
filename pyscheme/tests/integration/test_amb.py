from pyscheme.tests.integration.base import Base


class TestAmb(Base):
    def test_then_fail(self):
        self.assertEval(
            "12",
            """
                fn (x) {
                    if (x == 10) {
                        fail
                    } else {
                        x
                    }
                } (10 then 12)
            """
        )

