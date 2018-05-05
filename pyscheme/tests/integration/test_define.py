from pyscheme.tests.integration.base import Base


class TestDefine(Base):
    def test_define(self):
        self.assertEval(
            "10",
            """
                fn () {
                    define t = 10 ;
                    t
            }()
            """
        )

    def test_define_fn(self):
        self.assertEval(
            "4",
            """
                define double = fn (x) { x + x };
                double(2)
            """
        )