# `prepare_analysis`

This method is intended to run through a sequence before it is
analysed. It looks for definitions and pre-installs them as
`TypeVariable`s in the current type environment, so that within the
current scope we can type-check forward references.

There are only two kinds of definition:
1. standard `define` statements (and `fn` and `env` statements
that are rewritten to `define` statements.)
1. type constructors in the body of a `typedef`.

We can lump these both together under the general heading of
`definition`.

It would be an error for `prepare_analysis` to recurse in to
nests, or anything else really, so to avoid this it calls
`prepare_definition` on its immediate children.
`prepare_definition` is a no-op in the base `Expr` class and
is only redefined for `Definition`, `Typedef` and
`TypeConstructor` (which `Typedef` calls.)

`prepare_analysis` should only be called **by `analyse_internal`**
as the first preliminary step when analysing a sequence.

However definitions can also occur at the top-level, and
in this case the `analyse_internal` method of the definitions
must call their own `prepare_definition` methods.

The problem is that within a sequence, `prepare_definition` will
already have been called (and needs to have been called) by the
parent sequence:

```text
top-level           definition
   |                     |
   |--analyse_internal-->+---+
   |                     |   |
   |                     |   | prepare_definition
   |                     |   |
   |                     +<--+
   |                     |
```

but:

```text
top-level             sequence                  definition
   |                     |                           |
   |--analyse_internal-->+---+                       |
   |                     |   |                       |
   |                     |   | prepare_analysis      |
   |                     |   |                       |
   |                     |   +--prepare_definition-->+
   |                     |   |                       |
   |                     +<--+                       |
   |                     |                           |
   |                     +--analyse_internal-------->+---+
   |                     |                           |   |
   |                     |                           |   | prepare_definition
   |                     |                           |   |
   |                     |                           +<--+
   |                     |                           |
```

the repl actually calls `analyse` on whatever the parser returns,
and `analyse` calls `analyse_internal` on itself. Of course
`prepare_definition` could check to see if the symbol being defined
already had an entry in the current environment frame, and do nothing
in that case, but then that would allow/ignore real re-definitions,
which should throw an error.

Solution, I think is that `analyse_internal` should not call
`prepare_analysis` or `prepare_definition` on itself, but it should be
the caller's responsibility:

##### `Expr.analyse`
1. call `prepare_analysis` on `self`
1. call `analyse_internal` on `self`

##### `Expr.prepare_analysis`
1. no-op

##### `Expr.prepare_definition`
1. no-op

##### `Expr.analyse_internal`
1. basic get static type method

##### `Sequence.prepare_analysis`
1. call `prepare_definition` on each of its children.

##### `Sequence.analyse_internal`
1. call `analyse_internal` on each of its children.
1. return the type of the last child.

##### `{Typedef | Definition}.prepare_definition`
1. pre-instates the TypeVriable in the type environment
