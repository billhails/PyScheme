"""
.. module:: inference
   :synopsis: An implementation of the Hindley Milner type checking algorithm
              based on the Scala code by Andrew Forrest, the Perl code by
              Nikita Borisov and the paper "Basic Polymorphic Typechecking"
              by Cardelli.
.. moduleauthor:: Robert Smallshire
"""


# =======================================================#
# Class definitions for the abstract syntax tree nodes
# which comprise the little language for which types
# will be inferred


class AST:
    def analyse(self, env, non_generic=None):
        """Computes the type of the expression given by node.

        The type of the node is computed in the context of the
        supplied type environment env. Data types can be introduced into the
        language simply by having a predefined set of identifiers in the initial
        environment. environment; this way there is no need to change the syntax or, more
        importantly, the type-checking program when extending the language.

        Args:
            self: The root of the abstract syntax tree.
            env: The type environment is a mapping of expression identifier names
                to type assignments.
                to type assignments.
            non_generic: A set of non-generic variables, or None

        Returns:
            The computed type of the expression.

        Raises:
            InferenceError: The type of the expression could not be inferred, for example
                if it is not possible to unify two types such as Integer and Bool
            ParseError: The abstract syntax tree rooted at node could not be parsed
        """
        if non_generic is None:
            non_generic = set()
        return self.analyse_internal(env, non_generic)

    def analyse_internal(self, env, non_generic):
        pass


class Lambda(AST):
    """Lambda abstraction"""

    def __init__(self, v, body):
        self.arg = v
        self.body = body

    def analyse_internal(self, env, non_generic):
        arg_type = TypeVariable()
        new_env = env.copy()
        new_env[self.arg] = arg_type
        new_non_generic = non_generic.copy()
        new_non_generic.add(arg_type)
        result_type = self.body.analyse_internal(new_env, new_non_generic)
        return Function(arg_type, result_type)

    def __str__(self):
        return "fn ({arg}) {{ {body} }}".format(arg=self.arg, body=self.body)


class Literal(AST):
    """Abstract Literal"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Number(Literal):
    """Integer Literal"""

    def analyse_internal(self, env, non_generic):
        return Integer


class Boolean(Literal):
    """Boolean literal"""

    def analyse_internal(self, env, non_generic):
        return Bool


class Identifier(AST):
    """Identifier"""

    def __init__(self, name):
        self.name = name

    def analyse_internal(self, env, non_generic):
        return self.get_type(env, non_generic)

    def get_type(self, env, non_generic):
        """Get the type of identifier name from the type environment env.

        Args:
            self: The identifier
            env: The type environment mapping from identifier names to types
            non_generic: A set of non-generic TypeVariables

        Raises:
            ParseError: Raised if name is an undefined symbol in the type
                environment.
        """
        if self.name in env:
            return self.fresh(env[self.name], non_generic)
        else:
            raise ParseError("Undefined symbol {0}".format(self.name))

    @classmethod
    def fresh(cls, t, non_generics):
        """Makes a copy of a type expression.

        The type t is copied. The the generic variables are duplicated and the
        non_generic variables are shared.

        Args:
            t: A type to be copied.
            non_generics: A set of non-generic TypeVariables
        """
        mappings = {}  # A mapping of TypeVariables to TypeVariables

        def freshrec(tp):
            def is_generic(v, non_generic):
                """Checks whether a given variable occurs in a list of non-generic variables

                Note that a variables in such a list may be instantiated to a type term,
                in which case the variables contained in the type term are considered
                non-generic.

                Note: Must be called with v pre-pruned

                Args:
                    v: The TypeVariable to be tested for genericity
                    non_generic: A set of non-generic TypeVariables

                Returns:
                    True if v is a generic variable, otherwise False
                """
                return not v.occurs_in(non_generic)

            p = tp.prune()
            if isinstance(p, TypeVariable):
                if is_generic(p, non_generics):
                    if p not in mappings:
                        mappings[p] = TypeVariable()
                    return mappings[p]
                else:
                    return p
            elif isinstance(p, TypeOperator):
                return TypeOperator(p.name, *[freshrec(x) for x in p.types])

        return freshrec(t)

    def __str__(self):
        return self.name


class Apply(AST):
    """Function application"""

    def __init__(self, fn, arg):
        self.fn = fn
        self.arg = arg

    def analyse_internal(self, env, non_generic):
        result_type = TypeVariable()
        Function(
            self.arg.analyse_internal(env, non_generic),
            result_type
        ).unify(self.fn.analyse_internal(env, non_generic))
        return result_type

    def __str__(self):
        return "({fn} {arg})".format(fn=self.fn, arg=self.arg)


class Let(AST):
    """Let binding"""

    def __init__(self, v, defn, body):
        self.v = v
        self.defn = defn
        self.body = body

    def analyse_internal(self, env, non_generic):
        defn_type = self.defn.analyse_internal(env, non_generic)
        new_env = env.copy()
        new_env[self.v] = defn_type
        return self.body.analyse_internal(new_env, non_generic)

    def __str__(self):
        return "{{ let {v} = {defn} in {body} }}".format(v=self.v, defn=self.defn, body=self.body)


class Letrec(AST):
    """Letrec binding"""

    def __init__(self, v, defn, body):
        self.v = v
        self.defn = defn
        self.body = body

    def analyse_internal(self, env, non_generic):
        var_type = TypeVariable()
        new_env = env.copy()
        new_env[self.v] = var_type
        new_non_generic = non_generic.copy()
        new_non_generic.add(var_type)
        defn_type = self.defn.analyse_internal(new_env, new_non_generic)
        var_type.unify(defn_type)
        return self.body.analyse_internal(new_env, non_generic)

    def __str__(self):
        return "{{ letrec {v} = {defn} in {body} }}".format(v=self.v, defn=self.defn, body=self.body)


# =======================================================#
# Exception types


class InferenceError(Exception):
    """Raised if the type inference algorithm cannot infer types successfully"""

    def __init__(self, message):
        self.__message = message

    message = property(lambda self: self.__message)

    def __str__(self):
        return str(self.message)


class ParseError(Exception):
    """Raised if the type environment supplied for is incomplete"""

    def __init__(self, message):
        self.__message = message

    message = property(lambda self: self.__message)

    def __str__(self):
        return str(self.message)


# =======================================================#
# Types and type constructors

class Type:
    def prune(self):
        """Returns the currently defining instance of t.

        As a side effect, collapses the list of type instances. The function Prune
        is used whenever a type expression has to be inspected: it will always
        return a type expression which is either an uninstantiated type variable or
        a type operator; i.e. it will skip instantiated variables, and will
        actually prune them from expressions to remove long chains of instantiated
        variables.

        Returns:
            An uninstantiated TypeVariable or a TypeOperator
        """
        pass

    def occurs_in(self, types):
        """Checks whether a types variable occurs in any other types.

        Args:
            self:  The TypeVariable to be tested for
            types: The sequence of types in which to search

        Returns:
            True if t occurs in any of types, otherwise False
        """
        return any(self.occurs_in_type(t) for t in types)

    def occurs_in_type(self, other):
        """Checks whether occurs in a type expression.

        Note: Must be called with self pre-pruned

        Args:
            self:  The TypeVariable to be tested for
            other: The type in which to search

        Returns:
            True if v occurs in type2, otherwise False
        """
        pruned_other = other.prune()
        if pruned_other == self:
            return True
        elif isinstance(pruned_other, TypeOperator):
            return self.occurs_in(pruned_other.types)
        return False

    def unify(self, other):
        """Unify the two types self and other.

        Makes the types self and other the same.

        Args:
            self: The first type to be made equivalent
            other: The second type to be be equivalent

        Returns:
            None

        Raises:
            InferenceError: Raised if the types cannot be unified.
        """
        self.prune().unify_internal(other.prune())

    def unify_internal(self, other):
        assert 0, "Not unified"


class TypeVariable(Type):
    """A type variable standing for an arbitrary type.

    All type variables have a unique id, but names are only assigned lazily,
    when required.
    """

    next_variable_id = 0

    def __init__(self):
        self.id = TypeVariable.next_variable_id
        TypeVariable.next_variable_id += 1
        self.instance = None
        self.__name = None

    next_variable_name = 'a'

    @property
    def name(self):
        """Names are allocated to TypeVariables lazily, so that only TypeVariables
        present after analysis consume names.
        """
        if self.__name is None:
            self.__name = TypeVariable.next_variable_name
            TypeVariable.next_variable_name = chr(ord(TypeVariable.next_variable_name) + 1)
        return self.__name

    def prune(self):
        if self.instance is not None:
            self.instance = self.instance.prune()
            return self.instance
        return self

    def unify_internal(self, other):
        if self != other:
            if self.occurs_in_type(other):
                raise InferenceError("recursive unification")
            self.instance = other

    def __str__(self):
        if self.instance is not None:
            return str(self.instance)
        else:
            return self.name

    def __repr__(self):
        return "TypeVariable(id = {0})".format(self.id)


class TypeOperator(Type):
    """An n-ary type constructor which builds a new type from old"""

    def __init__(self, name, *types):
        self.name = name
        self.types = types

    def prune(self):
        return self

    def unify_internal(self, other):
        if isinstance(other, TypeVariable):
            other.unify_internal(self)
        elif isinstance(other, TypeOperator):
            if self.name != other.name or len(self.types) != len(other.types):
                raise InferenceError("Type mismatch: {0} != {1}".format(str(self), str(other)))
            for p, q in zip(self.types, other.types):
                p.unify(q)
        else:
            assert 0, "Not unified"

    def __str__(self):
        num_types = len(self.types)
        if num_types == 0:
            return self.name
        elif num_types == 2:
            return "({0} {1} {2})".format(str(self.types[0]), self.name, str(self.types[1]))
        else:
            return "{0}({1})".format(self.name, ' '.join([str(t) for t in self.types]))


class Function(TypeOperator):
    """A binary type constructor which builds function types"""

    def __init__(self, from_type, to_type):
        super(Function, self).__init__("->", from_type, to_type)


# Basic types are constructed with a nullary type constructor
Integer = TypeOperator("int")  # Basic integer
Bool = TypeOperator("bool")  # Basic bool


# ==================================================================#
# Example code to exercise the above


def try_exp(env, node):
    """Try to evaluate a type printing the result or reporting errors.

    Args:
        env: The type environment in which to evaluate the expression.
        node: The root node of the abstract syntax tree of the expression.

    Returns:
        None
    """
    print(str(node) + " : ", end=' ')
    try:
        t = node.analyse(env)
        print(str(t))
    except (ParseError, InferenceError) as e:
        print('*** ' + str(e) + ' ***')


def main():
    """The main example program.

    Sets up some predefined types using the type constructors TypeVariable,
    TypeOperator and Function.  Creates a list of example expressions to be
    evaluated. Evaluates the expressions, printing the type or errors arising
    from each.

    Returns:
        None
    """

    car = TypeVariable()
    cdr = TypeVariable()
    a = TypeVariable()
    t = TypeVariable()
    list_of_t = TypeOperator("list", t)
    v = TypeVariable()

    my_env = {
        "pair": Function(car, Function(cdr, TypeOperator("*", car, cdr))),  # $car -> $cdr -> *($car $cdr)
        "cond": Function(Bool, Function(a, Function(a, a))),                # bool -> $a -> $a -> $a
        "zero": Function(Integer, Bool),                                    # int -> bool
        "pred": Function(Integer, Integer),                                 # int -> int
        "times": Function(Integer, Function(Integer, Integer)),             # int -> int -> int
        "cons": Function(t, Function(list_of_t, list_of_t)),                # $t -> list($t) -> list($t)
        "append": Function(list_of_t, Function(list_of_t, list_of_t)),      # list($t) -> list($t) -> list($t)
        "null": list_of_t,                                                  # list($t)
        "add": Function(Integer, Function(Integer, Integer)),               # int -> int -> int
        "len": Function(list_of_t, Integer),                                # list($t) -> int
        "eq": Function(v, Function(v, Bool)),                               # $v -> $v -> bool
        "and": Function(Bool, Function(Bool, Bool)),                        # bool -> bool -> bool
    }

    examples = [
        # (and (eq 1 2) true) : bool
        Apply(
            Apply(
                Identifier("and"),
                Apply(
                    Apply(
                        Identifier("eq"),
                        Number(1)
                    ),
                    Number(2)
                )
            ),
            Boolean("true")
        ),

        # (len null) : int
        Apply(
            Identifier("len"),
            Identifier("null")
        ),

        # (add 1 2) : int
        Apply(
            Apply(
                Identifier("add"),
                Number(1)
            ),
            Number(2)
        ),

        # (pair (cons 0 null) (cons true null)) : (list(int) * list(bool))
        Apply(
            Apply(
                Identifier("pair"),
                Apply(
                    Apply(
                        Identifier("cons"),
                        Number(0)
                    ),
                    Identifier("null")
                )
            ),
            Apply(
                Apply(
                    Identifier("cons"),
                    Boolean("true")
                ),
                Identifier("null")
            )
        ),

        # (append (cons 0 null) (cons true null)) should fail
        Apply(
            Apply(
                Identifier("append"),
                Apply(
                    Apply(
                        Identifier("cons"),
                        Number(0)
                    ),
                    Identifier("null")
                )
            ),
            Apply(
                Apply(Identifier("cons"), Boolean("true")),
                Identifier("null")
            )
        ),

        # (append (cons 0 null) (cons 1 null)) : list(int)
        Apply(
            Apply(
                Identifier("append"),
                Apply(
                    Apply(Identifier("cons"), Number(0)),
                    Identifier("null")
                )
            ),
            Apply(
                Apply(Identifier("cons"), Number(1)),
                Identifier("null")
            )
        ),

        # (cons 0 (cons true null)) should fail
        Apply(
            Apply(Identifier("cons"), Number(0)),
            Apply(
                Apply(Identifier("cons"), Boolean("true")),
                Identifier("null")
            )
        ),

        # (cons 0 (cons 1 null)) : list(int)
        Apply(
            Apply(Identifier("cons"), Number(0)),
            Apply(
                Apply(Identifier("cons"), Number(1)),
                Identifier("null")
            )
        ),

        # factorial
        Letrec(
            "factorial",
            Lambda(
                "n",
                Apply(
                    Apply(
                        Apply(
                            Identifier("cond"),
                            Apply(
                                Identifier("zero"),
                                Identifier("n")
                            )
                        ),
                        Number(1)
                    ),
                    Apply(
                        Apply(
                            Identifier("times"),
                            Identifier("n")
                        ),
                        Apply(
                            Identifier("factorial"),
                            Apply(
                                Identifier("pred"),
                                Identifier("n")
                            )
                        )
                    )
                )
            ),
            Apply(
                Identifier("factorial"),
                Number(5)
            )
        ),

        # fn f => (pair(f(3) f(true)) should fail
        Lambda(
            "f",
            Apply(
                Apply(
                    Identifier("pair"),
                    Apply(
                        Identifier("f"),
                        Number(3)
                    )
                ),
                Apply(
                    Identifier("f"),
                    Boolean("true")
                )
            )
        ),

        # pair(f(3), f(true)) should fail with "undefined symbol f"
        Apply(
            Apply(
                Identifier("pair"),
                Apply(
                    Identifier("f"),
                    Number(4)
                )
            ),
            Apply(
                Identifier("f"),
                Boolean("true")
            )
        ),

        # let f = (fn x => x) in ((pair (f 4)) (f true)) : (int * bool)
        Let(
            "f",
            Lambda(
                "x",
                Identifier("x")
            ),
            Apply(
                Apply(
                    Identifier("pair"),
                    Apply(
                        Identifier("f"),
                        Number(4)
                    )
                ),
                Apply(
                    Identifier("f"),
                    Boolean("true")
                )
            )
        ),

        # fn f => f f should fail the occurs check
        Lambda(
            "f",
            Apply(
                Identifier("f"),
                Identifier("f")
            )
        ),

        # let g = fn f => 5 in g g : int
        Let(
            "g",
            Lambda(
                "f",
                Number(5)
            ),
            Apply(
                Identifier("g"),
                Identifier("g")
            )
        ),

        # example that demonstrates generic and non-generic variables:
        # fn g => let f = fn x => g in pair (f 3, f true)
        Lambda(
            "g",
            Let(
                "f",
                Lambda(
                    "x",
                    Identifier("g")
                ),
                Apply(
                    Apply(
                        Identifier("pair"),
                        Apply(
                            Identifier("f"),
                            Number(3)
                        )
                    ),
                    Apply(
                        Identifier("f"),
                        Boolean("true")
                    )
                )
            )
        ),

        # Function composition
        # fn f (fn g (fn arg (f g arg)))
        Lambda(
            "f",
            Lambda(
                "g",
                Lambda(
                    "arg",
                    Apply(
                        Identifier("g"),
                        Apply(
                            Identifier("f"),
                            Identifier("arg")
                        )
                    )
                )
            )
        )
    ]

    for example in examples:
        try_exp(my_env, example)


if __name__ == '__main__':
    main()
