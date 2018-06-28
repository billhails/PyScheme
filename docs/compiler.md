# thoughts for an abstract machine

Reminder:


| closure | cont    | fail    |    am   |
|---------|---------|---------|---------|
| `PC`    | `PC`    | `PC`    | `PC`    |
| `ENV`   | `ENV`   | `ENV`   | `ENV`   |
|         | `CONT`  | `CONT`  | `CONT`  |
|         | `temps` | `temps` | `temps` |
|         |         | `AM`    | `AM`    |
|         |         | `RET`   | `RET`   |

# primitive operations for basic language functionality:
* unconditional branching
    * `JMP label`
* arithmetic
    * `ADD 1 2 3` reg[3] = reg[1] + reg[2]
    * _etc._
* boolean logic with branches
    * `AND reg1 reg2 true_label false_label`
    * `EQ  reg1 reg2 true_label false_label`
    * _etc._
* record manipulation
    * `MAKEREC size kind target_register` works for cons
      too, kind is i.e. pair or null not type (hint - BBOP)
    * `GETREC reg offset target`
    * `SETREC reg offset value`
    * we could have some shortcuts for common cases:
        * `MAKEREC0 kind target`
        * `MAKEREC1 kind val target`
        * `MAKEREC2 kind val21 val2 target`
        * _etc._
    * to avoid having to separately fill it, but it
      may not be much of an optimisation
* environment manipulation
    * `GETENV frame index target` get value from
      environment
    * `SETENV frame index value` set value in
      environment
    * `PUSHENV size` create new environment frame
* threading
    * `SPAWN label1 label2` ? the two branches would
      need to set `RET` to true or false appropriately
      then both goto the same continuation.
    * `EXIT` unlink the current thread from the circular
      list of threads
* closure operations
    * `MAKECLOS label target` uses the current
      environment
    * `CALLCLOS reg` closure in reg overwrites
      `AM.closure`
* continuation operations
    * `MAKECONT label` copies `AM.continuation` to new
      `AM.continuation.cont` and makes
      `AM.continuation.cont->closure.pc = label`
    * `CONTINUE` `copies AM.continuation.cont` over
      `AM.continuation`
* amb operations
    * `MAKEBACK label` copies `AM` to new `AM.fail` and
      makes `AM.fail->pc = label`
    * `BACK` overwrites `AM` with current `AM.fail`

# Compiling Pattern Matching

* Where are the fargs? nowhere - abstract
* where are the aargs? in temps? or in a new register
  arglist? or as a list in a single temp? temps is more
  efficient (?) single arglist is easier.

concrete example:
```
fn map {
    (f, []) { [] }
    (f, h @ t) {
        f(h) @ map(f, t)
    }
}
```
Given f is unchanging and we have type-checked already,
we only need inspect the second aarg.

the code we want to generate is
```
  EQ type[farg2] 0 null-branch
  // not-null code
  CONTINUE
null-branch
  // null-code
  CONTINUE
```
# AMB

* `a then b`
```
  // code for a
  MAKEBACK label-b
  CONTINUE
label-b:
  // code for b
  CONTINUE
```
* `a then b then c`
* `a then (b then c)`

```
  MAKEBACK label-b
  // code for a
  CONTINUE
label-b:

    MAKEBACK label-c
    // code for b
    CONTINUE
  label-c
    // code for c
    CONTINUE

  CONTINUE // oops, dead code, unless CONTINUE
           // is part of "code for a" etc.
```

* `a = 10;`

```
SETENV frame index value
```
That's it, typechecking has already disallowed
redefinition, so no need to undo.
the code being backtracked to cannot have any assumption
that `a` is defined.

# Boxed vs Unboxed record fields

`list(char)` should be:

```
+---------+---+
| wchar_t | * |--->
+---------+---+
```

If all fields are the same size then we actually don't care.

`list(some_record)` should be:

```
+---+---+
| * | * |--->
+---+---+
  |
  v
```

