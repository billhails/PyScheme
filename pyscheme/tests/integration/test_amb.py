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

    def test_logic_puzzle(self):

        self.assertEval(
            "40",
            """
            define barrels_of_fun = fn () {
                define barrels = [30, 32, 36, 38, 40, 62];
                define beer = one_of(barrels);
                define wine = exclude([beer], barrels);
                define barrel_1 = one_of(wine);
                define barrel_2 = one_of(exclude([barrel_1], wine));
                define purchase = some_of(exclude([barrel_1, barrel_2], wine));
                require((barrel_1 + barrel_2) * 2 == sum(purchase));
                beer
            }
            ;
            define one_of = fn (list) {
                require(length(list) > 0);
                head(list) then one_of(tail(list))
            }
            ;
            define exclude = fn (items, list) {
                if (length(list) > 0) {
                    if (member(head(list), items)) {
                        exclude(items, tail(list))
                    } else {
                        head(list) @ exclude(items, tail(list))
                    }
                } else {
                    []
                }
            }
            ;
            define member = fn (item, list) {
                if (length(list) > 0) {
                    if (item == (head(list))) {
                        true
                    } else {
                        member(item, tail(list))
                    }
                } else {
                    false
                }
            }
            ;
            define some_of = fn (list) {
                require(length(list) > 0);
                [head(list)] then some_of(tail(list)) then head(list) @ some_of(tail(list))
            }
            ;
            define require = fn (condition) {
                if (condition) {
                    true
                } else {
                    fail
                }
            }
            ;
            define sum = fn (list) {
                if (length(list) == 0) {
                    0
                } else {
                    head(list) + sum(tail(list))
                }
            }
            ;
            barrels_of_fun()
            """
        )
