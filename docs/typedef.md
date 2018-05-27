# Typedef

Informal notes to clarify the syntax and semantics of this language feature.

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
where `str` is not a pre-existing definition.

## Formal Grammar

```
typedef : TYPEDEF flat-type '{' type-constructor { '|' type-constructor } '}'

flat-type : symbol [ '(' type-variable { ',' type-variable } ')' ]

type-constructor : symbol [ '(' type { ',' type } ')' ]

type : INT
     | CHAR
     | STRING
     | BOOL
     | LIST '(' type ')'
     | type-variable
     | predeclared-type [ '(' type { ',' type } ')' ]

type-variable : symbol

predeclared-type : symbol
```
Semantics:
* each `type-variable` is bound in the `flat-type` declaration and has scope over the rest of the typedef.
  * note that type variables are not "meta" i.e. they can't themselves take arguments.
  * note also that type variables do not nest in the formal arguments of the `flat-type` either.
* a `predeclared-type` is a type established by a previous `typedef`, and its arguments must agree with its definition.