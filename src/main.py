import argparse
import sys
from .interpreter.tokenizer import Tokenizer
from .interpreter.parser import Parser
from .engine.naive import naive_evaluation
from .engine.seminaive import semi_naive_evaluation
from .utilities.timer import Timer
from .interpreter.safety import check_safety_rules


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Evaluate a Datalog program.")
    parser.add_argument("file", type=str, help="The name of the file containing the Datalog program.")
    parser.add_argument("method", type=str, choices=["naive", "seminaive"], help="The method of evaluation (naive or seminaive).")
    parser.add_argument("--output", type=str, default="output.txt", help="The name of the file to which the output will be written (default: output.txt).")
    parser.add_argument("--verbose", action="store_true", default=False, help="Enable verbose output")

    args = parser.parse_args()

    program = ""
    with open(args.file) as f:
        program = f.read()

    tokenizer = Tokenizer()
    tokenizer.build()

    parser = Parser(tokenizer)
    parser.build(debug=True)

    facts = []
    rules = []
    try:
        parsedProgram = parser.parser.parse(program)
        if not parsedProgram:
            raise Exception("Unknown error while parsing program.")
        for p in parsedProgram:
            if p.type == 'fact':
                facts.append(p)
            elif p.type == 'rule':
                rules.append(p)

        check_safety_rules(facts, rules)
    except Exception as e:
        print(e)
        sys.exit(1)

    database = ""
    if args.method == "naive":
        with Timer("Naive evaluation"):
            database = naive_evaluation(facts, rules, args.verbose)

    else:
        with Timer("Semi-naive evaluation"):
            database = semi_naive_evaluation(facts, rules, args.verbose)

    with open(args.output, 'w') as file:
        file.write(database)
