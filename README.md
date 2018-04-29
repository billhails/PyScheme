# PyScheme

A small lambda-language interpreter written in Python

I have a few ideas I'd like to pull in from my abortive F-natural project,
specifically
* incorporate `amb` with keywords `then` and `fail`, i.e. `def x = 5 then 6`
and `if (x == 0) { fail }`.
* strong implicit type checking.
* first-class environments.
* built in linked lists with `@` (cons) and `@@` (append) operators.
* strings are linked lists of char.

I'm also toying with the idea of a three-valued logic
system with values `true` `false` and `unknown`. So `true || unknown == true`
and `false && unknown == false`, also `!unknown == unknown` etc.
It might be useful for decidability problems and if you never use the
`unknown` value all the remaining logic remains standard.

Syntax is very much in the javascript style, and I'm using `ply` to parse.