import argparse
from .interpreter.tokenizer import Tokenizer
from .interpreter.parser import Parser
from .engine.fixpoint import naive_evaluation, semi_naive_evaluation
from .utilities.timer import Timer


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Evaluate a Datalog program.")
    parser.add_argument("file", type=str, help="The name of the file containing the Datalog program.")
    parser.add_argument("method", type=str, choices=["naive", "seminaive"], help="The method of evaluation (naive or seminaive).")
    parser.add_argument("--output", type=str, default="output.txt", help="The name of the file to which the output will be written (default: output.txt).")

    args = parser.parse_args()

    file_name = args.file
    method = args.method
    output = args.output
    
    program = ""
    with open(file_name) as f:
        program = f.read()

    tokenizer = Tokenizer()
    tokenizer.build()

    parser = Parser(tokenizer)
    parser.build()

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

    database = ""
    if method == "naive":
        with Timer("Naive evaluation"):
            database = naive_evaluation(facts, rules)
            
    else:
        with Timer("Semi-naive evaluation"):
            database = semi_naive_evaluation(facts, rules)

    with open(output, 'w') as file:
                file.write(database)
