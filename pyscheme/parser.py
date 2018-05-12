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


from lark import Lark

grammar = """
        ?statement: expression ';'
                  | IF '(' expression ')' nest ELSE nest
                  | FN symbol '(' formals ')' body
                  | nest

        ?nest : body
        
        ?body: '{' multi_statement '}'

        ?multi_statement: statement
                        | statement multi_statement

        ?expression: binop_then

        ?binop_then: binop_and 'then' binop_then
               | binop_and

        ?binop_and: unop_not ['and' unop_not]
               | unop_not ['or' unop_not]
               | unop_not ['xor' unop_not]
               | unop_not

        ?unop_not: 'not' unop_not
               | binop_compare

        ?binop_compare: binop_cons '==' binop_cons
               | binop_cons '!=' binop_cons
               | binop_cons '>' binop_cons
               | binop_cons '<' binop_cons
               | binop_cons '>=' binop_cons
               | binop_cons '<=' binop_cons
               | binop_cons

        ?binop_cons: binop_add '@' binop_cons
               | binop_add '@@' binop_cons
               | binop_add

        ?binop_add: binop_mul ['+' binop_mul]
               | binop_mul ['-' binop_mul]
               | binop_mul

        ?binop_mul: op_funcall ['*' op_funcall]
            | op_funcall ['/' op_funcall]
            | op_funcall ['%' op_funcall]
            | op_funcall

        ?op_funcall: atom ['(' actuals ')']
            | atom

        ?atom: NAME -> symbol
               | number
               | string
               | char
               | boolean
               | lst
               | 'fn' '(' formals ')' body
               | 'define' symbol '=' expression
               | 'back'
               | '(' expression ')'
        
        ?char
        %import common.CNAME -> NAME
        %import common.INT -> number
        %import common.ESCAPED_STRING -> string
        %import common.WS_INLINE
        
        %ignore WS_INLINE
"""