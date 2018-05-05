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
        'fail': 'FAIL'
    }

    tokens = [
        'NUMBER',
        'ID',
        'COMMENT',
        'EQ',
        'CONS',
        'APPEND'
    ] + list(reserved.values())

    literals = '+{}(),[];'

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

    def t_COMMENT(self, t):
        r'//.*'
        pass

    def t_EQ(self, t):
        r'=='
        return t

    def t_eof(self, t):
        more = self.stream.read()
        if more:
            self.lexer.input(more)
            return self.lexer.token()
        return None

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # A string containing ignored characters (spaces and tabs)
    t_ignore = ' \t'

    # Error handling rule
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)
