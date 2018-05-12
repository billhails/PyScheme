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
    """
    "amb" adds chronological backtracking by doing three things:
    1. A binary operator "binop_then" which:
        a. evaluates and returns its lhs.
        b. if backtracked to once evaluates and returns its rhs.
        c. if backtracked to a second time backtracks further.
    2. A keyword "back" that backtracks immediately.
    3. A change to "define" which undoes its definition before backtracking further.
    """

    def test_then_back(self):
        self.assertEval(
            "here\n12",
            """
                fn (x) {
                    if (x == 10) {
                        print("here");
                        back;
                    } else {
                        x;
                    }
                } (10 then 12);
            """
        )

    def test_then_back_2(self):
        self.assertEval(
            "4",
            """
                fn require(x) {
                    x or back
                }
                
                fn one_of(list) {
                    require(length(list) > 0);
                    head(list) then one_of(tail(list));
                }
                
                {
                    define x = one_of([1, 2, 3, 4, 5]);
                    require(x == 4);
                    x;
                }
            """
        )

    def test_barrels_of_fun(self):
        """
        A wine merchant has six barrels of wine and beer containing 30, 32, 36, 38, 40 and 62 gallons respectively.
        Five barrels are filled with wine, and one with beer.
        The first customer purchases two barrels of wine.
        The second customer purchases twice as much wine as the first customer.
        Which barrel contains beer?
        """
        self.assertEval(
            "40",
            """
            
            fn barrels_of_fun() {
                define barrels = [30, 32, 36, 38, 40, 62];
                define beer = one_of(barrels);
                define wine = exclude([beer], barrels);
                define barrel_1 = one_of(wine);
                define barrel_2 = one_of(exclude([barrel_1], wine));
                define purchase = some_of(exclude([barrel_1, barrel_2], wine));
                require((barrel_1 + barrel_2) * 2 == sum(purchase));
                beer;
            }
            
            fn one_of(list) {
                require(length(list) > 0);
                head(list) then one_of(tail(list))
            }
            
            fn exclude(items, list) {
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
            
            fn member(item, list) {
                if (length(list) > 0) {
                    if (item == (head(list))) {
                        true
                    } else {
                        member(item, tail(list));
                    }
                } else {
                    false
                }
            }

            fn some_of(list) {
                require(length(list) > 0);
                [head(list)] then some_of(tail(list)) then head(list) @ some_of(tail(list));
            }

            fn require(condition) {
                condition or back
            }

            fn sum(list) {
                if (length(list) == 0) {
                    0
                } else {
                    head(list) + sum(tail(list))
                }
            }

            barrels_of_fun();
            """
        )
