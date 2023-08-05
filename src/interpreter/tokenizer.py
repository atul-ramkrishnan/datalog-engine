import ply.lex as lex


class Tokenizer(object):
    # TODO: Do we need a token for query?
    tokens = [
        'IMPLICATION',  #:-
        'DOT',          #.
        'LEFT_PAR',     #(
        'RIGHT_PAR',    #)
        'COMMA',        #,
        'CONSTANT',     # Begins with a lowercase letter
        'VARIABLE',     # Begins with an uppercase letter
    ]

    # Ignore spaces and tabs
    t_ignore = ' \t'

    # Tokens' regular expressions
    t_IMPLICATION = r'\:\-'
    t_DOT = r'\.'
    t_LEFT_PAR = r'\('
    t_RIGHT_PAR = r'\)'
    t_COMMA = r'\,'
    t_VARIABLE = r'[A-Z][A-Za-z0-9_]*'
    t_CONSTANT = r'[a-z0-9][a-zA-Z0-9_.]*'

    def t_comment(self, t):
        r"[ ]*\%[^\n]*"  #
        pass

    def t_newline(self, t):
        # Keep track of line numbers
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        # Error handling rule
        raise Exception(f"Illegal character: {t.value[0]}")

    def build(self, **kwargs):
        '''
        Builds the tokenizer.

            Keyword Args:
                debug (Boolean): Produces debugging information
                debuglog (str): Writes the debugging information in the file
                ...
            
            Returns:
                tokenizer (ply.lex.lex): Tokenizer object
        '''
        self.lexer = lex.lex(module=self, **kwargs)

    def test(self, data):
        '''
        Prints the tokenized data line by line.

            Args:
                data (str): Data which is to be tokenized
            
            Returns:
                None
        '''
        self.lexer.input(data)
        while True:
             tok = self.lexer.token()
             if not tok:
                 break
             print(tok)
