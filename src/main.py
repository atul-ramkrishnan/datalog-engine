import sys
from interpreter.tokenizer import Tokenizer
from interpreter.parser import Parser

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
    parser.test(program)
    