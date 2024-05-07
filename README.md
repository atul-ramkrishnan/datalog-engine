# README
## Requirements
Python Lex-Yacc

## How to run the script
1. Go to the root of the project.
2. You can run the program using the naive or semi-naive evaluation method using the command `python -m src.main input.txt naive --output output.txt --verbose`
The first argument `input.txt` specifies the file in which the Datalog program is stored. 
The second argument specifies the method of evaluation -- naive or seminaive.
The third argument (optional) can be used to specify the file in which the output is stored. By default it is stored in output.txt.
The fourth argument (optional) can be used to print some additional logging information per iteration.
