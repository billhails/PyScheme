# PyScheme lambda language written in Python
#
# Expressions (created by the parser) for evaluation
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

from typing import Callable, Union, TypeVar, List

S = TypeVar('S')
Maybe = Union[S, None]

# Promises are used by the trampoline in the repl.
# A promise is either None or a callable of no arguments that returns a Promise, or a list of those callables.
# If the trampoline sees None it will terminate the current thread (used by `exit).
# If the trampoline sees a list, it will install each element as a separate thread (used by `spawn`).
CallablePromise = Callable[[], 'Promise']
Promise = Union[None, CallablePromise, List[CallablePromise]]

# A Continuation is a callable that takes an Expr and an Amb (backtracking continuation)
# and returns a promise.
Continuation = Callable[[Maybe['expr.Expr'], 'Amb'], Promise]

# An Amb (backtracking continuation) is a callable of no arguments that returns a Promise to resume a
# chronologically previous operation.
Amb = Callable[[], Promise]