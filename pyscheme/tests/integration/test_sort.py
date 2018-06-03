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


class TestSort(Base):

    def test_sort(self):
        self.assertEval(
            '["everywhere", "goodbye", "hello", "here", "there"]',
            '''
            {
                define unsorted = ["hello", "goodbye", "here", "there", "everywhere"];

                // https://www.objc.io/blog/2014/10/20/functional-snippet-3-functional-quicksort/
                fn qsort {
                    ([]) { [] }
                    (pivot @ rest) {
                        define lesser = filter(ge(pivot), rest);
                        define greater = filter(lt(pivot), rest);
                        qsort(lesser) @@ [pivot] @@ qsort(greater)
                    }
                }

                fn lt(a, b) { a < b }

                fn ge(a, b) { a >= b }

                fn filter {
                    (f, []) { [] }
                    (f, h @ t) {
                        if (f(h)) {
                            h @ filter(f, t)
                        } else {
                            filter(f, t)
                        }
                    }
                }

                qsort(unsorted);
            }
            '''
        )
