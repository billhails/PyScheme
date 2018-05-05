import ply.lex as lex


class Lexer:
    reserved = {
        'if': 'IF',
        'else': 'ELSE',
        'fn': 'FN',
        'true': 'TRUE',
        'false': 'FALSE',
        'unknown': 'UNKNOWN',
        'and': 'LAND',
        'or': 'LOR',
        'not': 'LNOT',
        'xor': 'LXOR',
        'then': 'THEN',
        'fail': 'FAIL',
        'define': 'DEFINE',
    }

    tokens = [
        'NUMBER',
        'STRING',
        'CHAR',
        'ID',
        'EQ',
        'GT',
        'LT',
        'GE',
        'LE',
        'NE',
        'CONS',
        'APPEND'
    ] + list(reserved.values())

    literals = '+-*/%{}(),[];='

    def __init__(self, stream):
        self.lexer = lex.lex(module=self)
        self.stream = stream
        self.lexer.input('')

    def token(self):
        return self.lexer.token()

    def t_APPEND(self, t):
        r'@@'
        return t

    def t_CONS(self, t):
        r'@'
        return t

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value, 'ID')  # Check for reserved words
        return t

    def t_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_STRING(self, t):
        r'"(\\.|[^"])*"'
        t.value = str(t.value)[1:][:-1].strip('\\')
        return t

    def t_CHAR(self, t):
        r"'(\\.|[^'])'"
        t.value = str(t.value)[1:][:-1].strip('\\')
        return t

    def t_COMMENT(self, t):
        r'//.*'
        pass

    def t_EQ(self, t):
        r'=='
        return t

    def t_GE(self, t):
        r'>='
        return t

    def t_LE(self, t):
        r'<='
        return t

    def t_GT(self, t):
        r'>'
        return t

    def t_LT(self, t):
        r'<'
        return t

    def t_NE(self, t):
        r'!='
        return t

    def t_eof(self, t):
        more = self.stream.read()
        if more:
            self.lexer.input(more)
            return self.lexer.token()
        return None

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n'
        t.lexer.lineno += 1

    # A string containing ignored characters (spaces and tabs)
    t_ignore = ' \t'

    # Error handling rule
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)
