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


class TestWildcard(Base):
    """
    wildcard '_' in formal arguments behaves like a constant that
    matches (equals) anything
    """

    def test_wildcard_1(self):
        self.assertEval(
            'hello',
            '''
            fn ignore (_, _, foo) { foo }
            
            ignore(true, 10, "hello");
            '''
        )

    def test_wildcard_2(self):
        self.assertEval(
            '3',
            '''
            {
                fn len {
                    ([]) { 0 }
                    (_ @ t) { 1 + len(t) }
                }
                
                len([1, 2, 3]);
            }
            '''
        )

    def test_wildcard_3(self):
        self.assertEval(
            '2',
            '''
            typedef tree(t) { branch(tree(t), t, tree(t)) | leaf }

            fn ignore {
                (leaf) { 0 }
                (branch(_, t, _)) { t }
            }

            ignore(branch(leaf, 2, leaf));
            '''
        )
