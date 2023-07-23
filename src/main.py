import sys
from parser.tokenizer import Tokenizer

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise TypeError(f"main takes excactly 1 argument ({len(sys.argv)} given)")
    
    program = ""
    with open(sys.argv[1]) as f:
        program = f.read()

    # print(program)
    tokenizer = Tokenizer()
    tokenizer.build(debug=False)
    tokenizer.test(program)
    