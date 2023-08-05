import ply.yacc as yacc
from ..model.model import Fact, Rule, Predicate


class Parser(object):
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.tokens = tokenizer.tokens

    def p_program(self, p):
        '''program : facts rules
                | facts
                | rules'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = p[1] + p[2]

    def p_facts_list(self, p):
        '''facts : facts fact'''
        p[0] = p[1] + [p[2]]

    def p_facts(self, p):
        '''facts :  fact'''
        p[0] = [p[1]]

    def p_fact(self, p):
        '''fact : block DOT'''
        p[0] = Fact(p[1])
        # p[0] = p[1]

    def p_rules_list(self, p):
        '''rules : rules rule'''
        p[0] = p[1] + [p[2]]

    def p_rules(self, p):
        '''rules :  rule'''
        p[0] = [p[1]]

    def p_rule(self, p):
        '''rule : head IMPLICATION body DOT'''
        p[0] = Rule(p[1], p[3], 'rule')

    def p_head(self, p):
        '''head : block'''
        p[0] = p[1]

    def p_body(self, p):
        '''body : blocklist'''
        p[0] = p[1]

    def p_blocklist1(self, p):
        '''blocklist : blocklist COMMA block'''
        p[0] = p[1] + [p[3]]

    def p_blocklist3(self, p):
        '''blocklist : block'''
        p[0] = [p[1]]

    def p_block(self, p):
        '''block : CONSTANT LEFT_PAR atomlist RIGHT_PAR'''
        p[0] = Predicate(p[1], p[3], False)

    def p_atomlist1(self, p):
        '''atomlist : atomlist COMMA atom'''
        p[0] = p[1] + [p[3]]

    def p_atomlist2(self, p):
        '''atomlist : atom'''
        p[0] = [p[1]]

    def p_atomvariable(self, p):
        '''atom : VARIABLE'''
        p[0] = p[1]

    def p_atomconstant(self, p):
        '''atom : CONSTANT'''
        p[0] = p[1]
        # p[0] = "\'" + p[1] + "\'"

    def p_error(self, p):
        raise Exception(f"Syntax error in input. {p}")

    def build(self, **kwargs):
        '''
        Builds the parser.

            Keyword Args:
                debug (Boolean): Produces debugging information
                debuglog (str): Writes the debugging information in the file
                ...
            
            Returns:
                parser (ply.yacc.yacc): Parser object
        '''
        self.parser = yacc.yacc(module=self, **kwargs)

    def test(self, data):
        '''
        Prints the parser output line by line.

            Args:
                data (str): Data which is to be parsed
            
            Returns:
                None
        '''
        prog = self.parser.parse(data, lexer=self.tokenizer.lexer)
        print(prog)
