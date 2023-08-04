import sys
from .interpreter.tokenizer import Tokenizer
from .interpreter.parser import Parser
import pprint
from .engine.fixpoint import naive_evaluation, semi_naive_evaluation


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise TypeError(f"main takes excactly 1 argument ({len(sys.argv)} given)")
    
    program = ""
    with open(sys.argv[1]) as f:
        program = f.read()

    # print(program)
    tokenizer = Tokenizer()
    tokenizer.build()
    # tokenizer.test(program)

    parser = Parser(tokenizer)
    parser.build()
    # parser.test(program)

    facts = []
    rules = []
    parsedProgram = parser.parser.parse(program)
    # TODO: Handle syntax errors
    if not parsedProgram:
        print("ERROR")
    for p in parsedProgram:
        if p.type == 'fact':
            facts.append(p)
        elif p.type == 'rule':
            rules.append(p)

    pp = pprint.PrettyPrinter(depth=4)
    # pp.pprint(facts)
    # pp.pprint(rules)
    # test(facts, rules)
    database = semi_naive_evaluation(facts, rules)
    print(database)
    