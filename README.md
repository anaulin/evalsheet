# evalsheet

## Overview
`Evalsheet.py` loads a CSV file containing a spreadsheet, and evaluates it,
assuming that each cell is an expression in postfix notation. Expressions might
reference other cells in the spreadsheet. The output is then written to a new
CSV file.

Basic usage:
```bash
$ python evalsheet.py given.csv
```

A sample input file is provided in `given.csv`.

By default, the output is written to `eval.csv`, in the working directory. Any
existing file with that name will be overwritten. You can provide an alternate
output filename with the option `--out`:
```bash
$ python evalsheet.py given.csv --out=myoutfile.csv
```

## Testing

To run tests:
```bash
$ python evalsheet_test.py
```

## Implementation notes

This implementation uses a recursive algorithm to evaluate the spreadsheet.
The main drawback of this choice is the danger for unbounded stack growth,
and its attendant issues in a memory-restricted environment, or with extremely
complex cell dependencies. The evaluation algorithm can be outlined as follows:
* Given a spreadsheet represented as a two-dimensional array, for each element
  in the array (i.e. cell in the sheet):
  * If the cell has been visited by the evaluation routine before:
    1. If the cell has been evaluated already, return that value.
    2. If the cell has not been evaluated, it means we are in a circular
       dependency. Raise an error, aborting evaluation.
  * Trim and lowercase the cell, for ease of further manipulation.
  * Split the cell into tokens -- these are expected to be either operators,
    operands, or references to other cells.
  * For each token:
    * If it is a number, push it onto a stack
    * If it is a reference to another cell, evaluate that cell and push the
      result onto a stack
    * If it is an operator, evaluate it, using the two most recent values on the
      stack (all of our allowed operators take two arguments)

When errors are encountered during evaluation, an exception is thrown that
propagates to the top-level of the evaluation implementation. It is caught there
and converted to our error string. This exception propagation choice simplifies
the implementation somewhat; for example, we store the result of malformed cells
as the error string, relying on the fact that reusing that string in other
expressions will automatically cause ValueError exceptions to be thrown when
trying to interpret the error string as a number.

The implementation converts all operands to the Python type
`float`, which in turn leads to unnecessary decimal points and zeros in the
resulting output. This could be made more elegant with more careful string
formatting when converting the evaluation results to string.
