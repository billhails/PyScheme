# Typedef

Informal notes to clarify the syntax, semantics and proposed implementation
of this language feature.

## Predefined types

* `list(t)`
* `int`
* `char`
* `string`
* `bool`
* `nothing`

## Examples

Use cases and discussion.

### Enumerations

example:
```
    typedef colour { red | green | blue }
```
This creates a new type `colour` and three type constructors (functions) `red`, `green` and `blue` that,
because they are parameter-less, are effectively values of the type. Because the constructors are
parameter-less they can be used directly in the language (you don't have to say `red()`).

Usage:
```
    fn foo {
        (red) { "red" }
        (green) { "green" }
        (blue) { "blue" }
    }
```

The type checker then correctly infers the type of `foo` to be `colour -> string`.

Having determined the type of `foo`, the type checker should then verify that the function has a
case for each possible value in the enumeration. There would be a run-time error if `foo`
was declared as:
```
    fn foo {
        (red) { "red" }
        (green) { "green" }
    }
```
and then called with `foo(blue)`.

### Discriminated Unions

It should be possible to create discriminated unions as follows:

```
    typedef either(p, q) { first(p) | second(q) }
```
Probably best explained by usage:
```
    fn dissect {
        (first(x)) {
            first(x + 1)
        }
        (second(x)) {
            if (x == "hello") {
                second(true)
            } else {
                second(false)
            }
        }
    }
```
infers `dissect` to be `either(int, string) -> either(int, bool)`.

### Recursive Types

If we didn't already have `list`:
```
    typedef list(t) { pair(t, list(t)) | null }
```
This would do a couple of things:
1. Creates a new type "`list` of `t`" where `t` is a type variable.
1. Creates two type constructors (functions) for this type:
   * `pair` of a `t` and a `list` of `t`
   * `null`

### Uses of pre-existing types
```
typedef named_list(t) { named(string, list(t)) }
```
allows:
```
named("map", [1, 2, 3])
```
which has the type `named_list(int)`

## Restrictions

The formal arguments to the type constructors are existing types, but the type constructor
itself must be a new symbol, i.e.
```
    typedef mystring { list(char) }
```
is not valid as `list` is a pre-existing type. If you want this you have to say
```
    typedef mystring { str(list(char)) }
```
where `str` is not an existing definition.

## Formal Grammar

```
typedef : TYPEDEF flat_type '{' type_body '}'

flat_type : symbol [ '(' symbols ')' ]

type_body : type_constructor { '|' type_constructor }

type_constructor : symbol [ '(' type { ',' type } ')' ]

type : NOTHING
     | KW_LIST '(' type ')'
     | KW_INT
     | KW_CHAR
     | KW_STRING
     | KW_BOOL
     | symbol [ '(' type { ',' type } ')' ]
```
and for the composite functions:
```
construct : ...
          | FN symbol composite_body
          | ...

composite_body : '{' sub_functions '}'

sub_functions : sub_function { sub_function }

sub_function : sub_function_arguments body

sub_function_arguments : '(' sub_function_arg_list ')'

sub_function_arg_list : sub_function_arg [ ',' sub_function_arg_list ]

sub_function_arg : simple_subfunction_arg '@' sub_function_arg
                 | simple_subfunction_arg

sub_function_arg_2 : '[' [ sub_function_arg { ',' sub_function_arg } ] ']'
                   | sub_function_arg_3

sub_function_arg_3 : symbol [ '(' sub_function_arg_list ')' ]
                   | number
                   | string
                   | char
                   | boolean
                   | '(' sub_function_arg ')'
```
Semantics:
* each `type-variable` is bound in the `flat-type` declaration and has scope over the rest of the typedef.
  * note that type variables are not "meta" i.e. they can't themselves take arguments.
  * note also that type variables do not nest in the formal arguments of the `flat-type` either.
* a `predeclared-type` is a type established by a previous `typedef`, and its arguments must agree with its definition.

# Implementation

Three phases:
1. reading
1. type checking
   1. pre-analysis
   1. analysis
1. evaluation

Let's walk through these stages explaining the logic and structures built, for a small
number of example expressions.

## Example 1
Given:
```
typedef lst(t) { pr(t, lst(t)) | nll }

fn add1(x) {
    1 + x
}
```
which results in types
* `pr: t -> lst(t) -> lst(t)`
* `nll: lst(t)`
* `add1: int -> int`

parse, typecheck and evaluate:
```
fn map {
    (fun, nll) { nll }
    (fun, pr(h, t)) { pr(fun(h), map(f, t)) }
}

map(add1, pr(1, nll))
```
### parsing
Things are straightforward until we reach the formal arguments to map. `fun` is an
ordinary variable name, and should be parsed as such. However `nll` is a constant,
because of the typedef, but the parser can not know this (because the type
checker hasn't run yet). So the parser assumes all un-paramaterised symbols at the
top-level of a compound function component are `expr.Symbol`, and builds:
```
Composite(
    CompositeLambda(
        [   // arguments
            Symbol("fun"),
            Symbol("nll")
        ],
        Sequence(...) // body
    )
    CompositeLambda(
        [   // arguments
            Symbol("fun"),
            Application(
                Symbol("pr"),
                [
                    Symbol("h"),
                    Symbol("t")
                ]
            )
        ],
        Sequence(...) // body
    )
)

Application(
    Symbol("map"),
    [
        Symbol("add1"),
        Application(
            Symbol("pr"),
            [
                Number(1),
                Symbol("nll")
            ]
        )
    ]
)
```
We're less interested in the function bodies here, as they are evaluated normally.

### Type checking 1. pre-analysis

This is basically just running through the current sequence of statements (`{...}`)
and pre-installing type variables for the symbols being defined in the current
type environment.
This allows mutually recursive functions to type-check, but additionally it can refuse
to override the definition of a type value, even in a nested scope,
because they behave as constants.

The type environment keeps an additional equivalently scoped set of symbols
that have been defined as type constructors. This allows the type checker to
recognise symbols as type constructors / type values.

### Type checking 2. analysis

At the highest level, the `Composite` object merely iterates over its component
`CompositeLambda` objects calling their analysis method, and unifying all of
the results to produce the type of the `Composite` itself. So we can go straight
to the analysis of a `CompositeLambda`. Let's use the example above to discuss.

The first `CompositeLambda` should result in the following type:
```
(type of fun) -> lst(a) -> (type of Sequence with fun in scope)
```
Note particularly that there is no binding introduced for `nll` in the type
environment. It is not a variable, it is a constant. However the type of the
`CompositeLambda` includes `nll` in its arguments.

This is achieved by the type checker, when encountering a `Symbol`,
checking for it in that set of symbols currently acting as constants, which
is held in the type environment. If it finds such a symbol, it registers its
type in the argument list it is building, but does not add it to the type
environment it is building for the function.

To simplify the following, when I say "constant" I mean either a literal
like `1` or `"hello"`, or a constant symbol registered with the type
environment.

The second `CompositeLambda` should be analysed to the following type:
```
(type of fun)
    -> (type of application of pr to (type of h, type of t))
    -> (type of Sequence with fun, h and t in scope)
```
So the analysis of `fun` is the same, but on encountering the application
formal argument, the type checker knows that it can only legally be a
type constructor. It knows the type of that constructor is:
```text
a -> lst(a) ->lst(a)
```
However the type of the argument being analysed is the result of applying
that type constructor, i.e. `lst(a)`.

Descending recursively into the parmeters of `pr`, the same strategy is followed:
constants and type constructors are used for their type, and symbols are given a
type variable in the type environment.

We therefore build:
```text
type of h -> type of t -> b
```
and unify that with the type of `pr`:
```text
a -> lst(a) ->lst(a)
```

giving

| ls | rhs | result |
| --- | --- | ----- |
| `h` | `a` | `h == a` |
| `t` | `lst(a)` | `t == lst(h)` |
| `b` | `lst(a)` | `b == lst(h)` |

Now the type of the second `CompositeLambda` is more firmly established as
```text
(type of fun) -> lst(h) -> (type of Sequence with fun, h and t in scope)
```
We also know that `t` is `lst(h)` at this point.

Analysis of the body (Sequence) then proceeds by the standard HM type analysis to give
the final type of this `CompositeLambda`.

We then unify with the type of the first composite.

```text
(type of fun) -> lst(a) -> (type of Sequence with fun in scope)
(type of fun) -> lst(h) -> (type of Sequence with fun, h and t in scope)

```

Type checking of the application of `map` uses the standard HM algorithm.

### Evaluation
Now that the type checker has validated the expressions, we can execute them with
a certain confidence. In order to bind values to variables in the run-time,
when some of those variables are embedded inside type constructors, we need to
do a simplified (simpler than unification) pattern matching of the formal
arguments with their actual arguments. But the actual arguments are
constants and type structures, while the formal arguments are still just AST syntax.

Furthermore, we no longer have access to the type environment.

The idea at the moment is to partially evaluate the formal arguments and then
pattern match the result against the actual arguments. The difference between
partial evaluation and full evaluation is that symbols that are not being applied
to arguments are left as-is, and not looked up in the run-time environment.

To continue with our example, in the second clause of the map fn:
```text
(fun, pr(h, t)) { ... }
```
When evaluating the formal arguments, only `pr` is evaluated (looked up) and
applied to the symbols `h` and `t`, resulting in a `NamedTuple` with the name
`pr` and values of the two unevaluated symbols.

We can then pattern match the formal and actual arguments.

* note to self, we need to disallow repetition of a single symbol in formal
argument lists.
* when a constant matches a constant they must be equal.
* when a constant matches a symbol the symbol is bound to the constant in the env.
