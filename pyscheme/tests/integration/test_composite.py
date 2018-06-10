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


class TestComposite(Base):

    def test_composite_1(self):
        self.assertEval(
            'branch[branch[branch[leaf, 1, leaf], 2, leaf], 3, branch[leaf, 4, leaf]]',
            '''
            typedef tree(t) { branch(tree(t), t, tree(t)) | leaf }

            fn insert {
                (t, leaf) { branch(leaf, t, leaf) }
                (t, branch(left, u, right)) {
                    if (t < u) {
                        branch(insert(t, left), u, right)
                    } else if (t == u) {
                        branch(left, u, right)
                    } else {
                        branch(left, u, insert(t, right))
                    }
                }
            }

            insert(1, insert(3, insert(2, insert(4, insert(3, leaf)))));
            ''',
            'btrees'
        )

    def test_composite_2(self):
        self.assertEval(
            '[1, 2, 3, 4]',
            '''
            typedef tree(t) { branch(tree(t), t, tree(t)) | leaf }

            fn insert {
                (t, leaf) { branch(leaf, t, leaf) }
                (t, x = branch(left, u, right)) {
                    if (t < u) {
                        branch(insert(t, left), u, right)
                    } else if (t == u) {
                        x
                    } else {
                        branch(left, u, insert(t, right))
                    }
                }
            }

            fn flatten {
                (leaf) { [] }
                (branch(l, u, r)) { flatten(l) @@ [u] @@ flatten(r) }
            }

            flatten(insert(1, insert(3, insert(2, insert(4, insert(3, leaf))))));
            ''',
            'btrees'
        )

    def test_composite_3(self):
        self.assertEval(
            'some["there"]',
            '''
            {
                typedef tree(t) { branch(tree(t), int, t, tree(t)) | leaf }

                fn insert {
                    (index, val, leaf) { branch(leaf, index, val, leaf) }
                    (index, val, branch(left, j, w, right)) {
                        if (index < j) {
                            branch(insert(index, val, left), j, w, right)
                        } else if (index == j) {
                            branch(left, j, val, right)
                        } else {
                            branch(left, j, w, insert(index, val, right))
                        }
                    }
                }

                typedef t_or_fail(t) {some(t) | fail}

                fn retrieve {
                    (index, leaf) { fail }
                    (index, branch(left, j, val, right)) {
                        if (index < j) {
                            retrieve(index, left)
                        } else if (index > j) {
                            retrieve(index, right)
                        } else {
                            some(val)
                        }
                    }
                }

                retrieve(3,
                    insert(1, "hi",
                        insert(3, "there",
                            insert(2, "how",
                                insert(4, "are",
                                    insert(3, "you", leaf))))));
            }
            ''',
            'btrees'
        )

    def test_composite_3(self):
        self.assertEval(
            'branch[branch[leaf, true, leaf], true, branch[leaf, true, leaf]]',
            '''
            {
                typedef tree(t) { branch(tree(t), t, tree(t)) | leaf }
                
                fn complete {
                    (v, 0) { leaf }
                    (v, n) { branch(complete(v, n-1), v, complete(v, n-1)) }
                }
                
                complete(true, 2);
            }
            '''
        )

    def test_composite_44(self):
        self.assertEval(
            "branch[leaf, 1, branch[leaf, 2, leaf]]",
            """
            {
                typedef tree(t) { branch(tree(t), t, tree(t)) | leaf }
                
                fn insert {
                    (t, leaf) { branch(leaf, t, leaf) }
                    (t, branch(left, u, right)) {
                        if (t < u) {
                            branch(insert(t, left), u, right)
                        } else {
                            branch(left, u, insert(t, right))
                        }
                    }
                }
                
                define i1 = insert(1, leaf);
                define i2 = insert(2);
    
                i2(i1);
            }
            """,
            "composites can be curried, but only within a single expression"
        )
