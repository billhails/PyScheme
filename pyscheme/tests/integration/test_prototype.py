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


from pyscheme.tests.integration.base import Base


class TestPrototype(Base):
    def test_prototype_1(self):
        self.assertEval(
            '',
            '''
            prototype foo {
                map: (#a -> #b) -> list(#a) -> list(#b);
            }
            '''
        )

    def test_prototype_33(self):
        self.assertEval(
            "[2, 3, 4]",
            """
            prototype foo {
                map: (#a -> #b) -> list(#a) -> list(#b);
            }
            
            env bar {
                fn map {
                    (f, []) { [] }
                    (f, h @ t) { f(h) @ map(f, t) }
                }
            }
            
            fn x (mapper: foo) {
                mapper.map(1+, [1, 2, 3])
            }
            
            x(bar);
            """,
            ""
        )

    def test_prototype_57(self):
        self.assertEval(
            "[2, 3, 4]",
            """
            prototype foo {
                map: (#a -> #b) -> list(#a) -> list(#b);
            }
            
            env bar {
                fn map {
                    (f, []) { [] }
                    (f, h @ t) { f(h) @ map(f, t) }
                }
                
                fn other(x) { x }
            }
            
            fn x (mapper: foo) {
                mapper.map(1+, [1, 2, 3])
            }
            
            x(bar);
            """,
            ""
        )

    def test_prototype_83(self):
        self.assertError(
            "PySchemeTypeError: int != list(#a)",
            """
            prototype foo {
                len : list(#t) -> int;
            }
            
            env bar {
                fn len(a) { a }
            }
            
            fn x (lenner:foo) { lenner }
            
            x(bar);
            """,
            ""
        )