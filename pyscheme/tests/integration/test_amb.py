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

from .base import Base


class TestAmb(Base):
    """
    "amb" adds chronological backtracking by doing three things:
    1. A binary operator "then" which:
        a. evaluates and returns its lhs.
        b. if backtracked to once evaluates and returns its rhs.
        c. if backtracked to a second time backtracks further.
    2. A keyword "back" that backtracks immediately.
    3. A change to "define" which undoes its definition (side-effect) before backtracking further.
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
                
                fn one_of(lst) {
                    require(length(lst) > 0);
                    head(lst) then one_of(tail(lst));
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
            {
                fn require(condition) {
                    condition or back
                }
    
                fn one_of {
                    ([]) { back }
                    (h @ t) { h then one_of(t) }
                }
                
                fn member {
                    (item, []) { false }
                    (item, h @ t) {
                        if (item == h) {
                            true
                        } else {
                            member(item, t);
                        }
                    }
                }
    
                fn exclude {
                    (items, []) { [] }
                    (items, h @ t) {
                        if (member(h, items)) {
                            exclude(items, t)
                        } else {
                            h @ exclude(items, t)
                        }
                    }
                }
                
                fn some_of {
                    ([]) { back }
                    (h @ t) { [h] then some_of(t) then h @ some_of(t) }
                }
    
                fn sum {
                    ([]) { 0 }
                    (h @ t) { h + sum(t) }
                }
    
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
                
                barrels_of_fun();
            }
            """
        )

    def test_multiple_dwellings(self):
        """
        Baker, Cooper, Fletcher, Miller, and Smith live on different floors of an
        apartment house that contains only five floors. Baker does not live on the
        top floor. Cooper does not live on the bottom floor. Fletcher does not
        live on either the top or the bottom floor. Miller lives on a higher floor
        than does Cooper. Smith does not live on a floor adjacent to Fletcher's.
        Fletcher does not live on a floor adjacent to Cooper's.
        Where does everyone live?
        """
        self.assertEval(
            '[result["baker", 3], result["cooper", 2], result["fletcher", 4], result["miller", 5], result["smith", 1]]',
            '''
            {
                typedef named_result { result(list(char), int) }
                
                fn require(condition) {
                    condition or back
                }
                
                fn one_of { // demonstrate implicit green cut in composite functions
                    ([]) { back }
                    (h @ t) { h then one_of(t) }
                }
                
                fn member {
                    (x, []) { false }
                    (x, h @ t) { x == h or member(x, t) }
                }

                fn exclude {
                    (l, []) { [] }
                    (l, h @ t) {
                        if (member(h, l)) {
                            exclude(l, t)
                        } else {
                            h @ exclude(l, t)
                        }
                    }
                }
                
                fn abs(n) {
                    if (n < 0) { 0 - n } else { n }
                }
                
                define floors = [1, 2, 3, 4, 5];
                define baker = one_of(floors);
                define cooper = one_of(exclude([baker], floors));
                define fletcher = one_of(exclude([baker, cooper], floors));
                define miller = one_of(exclude([baker, cooper, fletcher], floors));
                define smith = head(exclude([baker, cooper, fletcher, miller], floors));
                require(baker != 5);
                require(cooper != 1);
                require(fletcher != 5);
                require(fletcher != 1);
                require(miller > cooper);
                require(abs(smith - fletcher) != 1);
                require(abs(fletcher - cooper) != 1);
                
                [
                    result("baker", baker),
                    result("cooper", cooper),
                    result("fletcher", fletcher),
                    result("miller", miller),
                    result("smith", smith)
                ];
            }
            ''',
            'multiple dwellings'
        )
