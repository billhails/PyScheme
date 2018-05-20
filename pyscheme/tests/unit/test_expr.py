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

from unittest import TestCase
import pyscheme.expr as expr
from pyscheme.exceptions import NonBooleanExpressionError


class TestExpr(TestCase):
    def setUp(self):
        self.expr = expr.Expr()

    def tearDown(self):
        self.expr = None

    def test_equality(self):
        self.assertEqual(self.expr, self.expr, "op_funcall should equal itself")

    def test_non_equality(self):
        self.assertNotEqual(self.expr, expr.Expr(), "different objects should not normally compare equal")

    def test_eq(self):
        self.assertIsInstance(self.expr.eq(self.expr), expr.T, "eq method returns boolean T")

    def test_not_null(self):
        self.assertFalse(self.expr.is_null(), "only null should be null")

    def test_non_boolean_exception(self):
        with self.assertRaises(NonBooleanExpressionError):
            self.expr.is_true()


class TestConstant(TestCase):
    def setUp(self):
        self.constant_10 = expr.Constant(10)
        self.constant_10b = expr.Constant(10)
        self.constant_12 = expr.Constant(12)

    def tearDown(self):
        self.constant_10 = None
        self.constant_10b = None
        self.constant_12 = None

    def test_value(self):
        self.assertEqual(10, self.constant_10.value(), "value should return underlying value")

    def test_equality(self):
        self.assertEqual(self.constant_10, self.constant_10b, "two constants with the same value should compare equal")

    def test_non_equality(self):
        self.assertNotEqual(self.constant_10,
                            self.constant_12,
                            "two constants with different values should not compare equal")

    def test_string(self):
        self.assertEqual("10", str(self.constant_10), "string value should be sensible")


class TestBoolean(TestCase):
    def setUp(self):
        self.t = expr.T()
        self.f = expr.F()
        self.u = expr.U()

    def tearDown(self):
        self.t = None
        self.f = None
        self.u = None

    def test_not(self):
        t = self.t
        f = self.f
        u = self.u
        for args in [
            [t, f],
            [f, t],
            [u, u]
        ]:
            with self.subTest(args = args):
                self.assertEqual(args[1], ~args[0])

    def test_and(self):
        t = self.t
        f = self.f
        u = self.u
        for args in [
            [t, t, t],
            [t, f, f],
            [t, u, u],
            [f, t, f],
            [f, f, f],
            [f, u, f],
            [u, t, u],
            [u, f, f],
            [u, u, u]
        ]:
            with self.subTest(args = args):
                self.assertEqual(args[2], args[0] & args[1])

    def test_or(self):
        t = self.t
        f = self.f
        u = self.u
        for args in [
            [t, t, t],
            [t, f, t],
            [t, u, t],
            [f, t, t],
            [f, f, f],
            [f, u, u],
            [u, t, t],
            [u, f, u],
            [u, u, u]
        ]:
            with self.subTest(args = args):
                self.assertEqual(args[2], args[0] | args[1])

    def test_xor(self):
        t = self.t
        f = self.f
        u = self.u
        for args in [
            [t, t, f],
            [t, f, t],
            [t, u, u],
            [f, t, t],
            [f, f, f],
            [f, u, u],
            [u, t, u],
            [u, f, u],
            [u, u, u]
        ]:
            with self.subTest(args = args):
                self.assertEqual(args[2], args[0] ^ args[1])

    def test_eq(self):
        t = self.t
        f = self.f
        u = self.u
        for args in [
            [t, t, t],
            [t, f, f],
            [t, u, f],
            [f, t, f],
            [f, f, t],
            [f, u, f],
            [u, t, f],
            [u, f, f],
            [u, u, t]
        ]:
            with self.subTest(args=args):
                self.assertEqual(args[2], args[0].eq(args[1]))

    def test_str(self):
        self.assertEqual("true", str(self.t))
        self.assertEqual("false", str(self.f))
        self.assertEqual("unknown", str(self.u))


class TestSymbol(TestCase):
    def setUp(self):
        self.a = expr.Symbol("a")
        self.b = expr.Symbol("b")
        self.b2 = expr.Symbol("b")

    def tearDown(self):
        self.a = None
        self.b = None
        self.b2 = None

    def test_equality(self):
        self.assertEqual(self.b, self.b2, "two symbols with the same name should compare equal")

    def test_non_equality(self):
        self.assertNotEqual(self.a, self.b, "two symbols with different names should not compare equal")

    def test_comparison(self):
        self.assertIsInstance(self.a.eq(self.b), expr.F, "boolean object should be false")
        self.assertIsInstance(self.b.eq(self.b2), expr.T, "boolean object should be true")

    def test_hash(self):
        self. assertEqual(hash(self.a), id(self.a), "hash function should use id")

    def test_str(self):
        self.assertEqual("a", str(self.a), "string representation should be sensible")


class TestList(TestCase):
    def setUp(self):
        self.a = expr.Symbol("a")
        self.b = expr.Symbol("b")
        self.c = expr.Symbol("c")
        self.list = expr.List.list([self.a, self.b, self.c])
        self.null = expr.Null()

    def tearDown(self):
        self.a = None
        self.b = None
        self.c = None
        self.list = None
        self.null = None

    def test_null(self):
        self.assertTrue(self.null.is_null(), "null class method should return null")
        self.assertFalse(self.list.is_null(), "non-empty list should not be null")

    def test_car(self):
        self.assertEqual(self.a, self.list.car(), "car of list should be a")

    def test_car2(self):
        self.assertEqual(self.null, self.null.car(), "car of null should be null")

    def test_cdr(self):
        self.assertEqual(self.b, self.list.cdr().car(), "car of cdr of list should be b")

    def test_cdr2(self):
        self.assertEqual(self.null, self.null.cdr(), "cdr of null should be null")

    def test_len(self):
        self.assertEqual(3, len(self.list), "list should be length three")

    def test_str(self):
        self.assertEqual("[a, b, c]",
                         str(self.list),
                         "list as string should be sensible")

    def test_append(self):
        self.assertEqual("[a, b, c, a, b, c]",
                         str(self.list.append(self.list)),
                         "append to self should double size")

    def test_iter(self):
        result = []
        for s in self.list:
            result += [s]
        self.assertEqual([self.a, self.b, self.c], result, "iteration should work")

    def test_getitem(self):
        self.assertEqual(self.b,
                         self.list[1])

    def test_getitem2(self):
        with self.assertRaises(KeyError):
            print(self.null[0])

    def test_getitem3(self):
        with self.assertRaises(TypeError):
            print(self.list["a"])

    def test_getitem4(self):
        with self.assertRaises(TypeError):
            print(self.null["a"])

    def test_getitem5(self):
        with self.assertRaises(KeyError):
            print(self.list[5])

    def test_getitem6(self):
        with self.assertRaises(KeyError):
            print(self.list[-1])

    def test_last1(self):
        self.assertEqual(self.c, self.list.last(), "last item of list should be c")

    def test_last2(self):
        self.assertEqual(self.null, self.null.last(), "last item of null should be null")