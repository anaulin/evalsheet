import argparse
import csv
import re

class Sheet:
  """Representation of a spreadsheet.
  """

  ERR = '#ERR'
  OPERATORS = '+-*/'
  CELL_REF_RE = re.compile("(\D+)(\d+)")

  @staticmethod
  def from_file(filename):
    """Returns a Sheet object initialized from the given csv file.
    """
    cells = []
    with open(filename, 'rb') as f:
      reader = csv.reader(f)
      for row in reader:
        cells.append(row)
    return Sheet(cells)

  def __init__(self, cells):
    """Initializes a Sheet object from a two-dimensional array.

    Each item in the array is expected to be a string.
    """
    self._cells = cells
    # Initialize with blank strings an array for the evaluated cells.
    self._cells_eval = [['' for cell in row] for row in self._cells]
    # Dictionary to keep track of visited cells. Used during evaluation.
    self._visited_cells = {}

  def eval_to_csv(self, filename):
    """Evaluates the sheet and writes it out into a file in csv format.
    """
    self.eval()
    with open(filename, 'wb') as f:
      writer = csv.writer(f)
      for row in self._cells_eval:
        writer.writerow(row)

  def eval(self):
    """Evaluates the sheet and returns the resulting two-dimensional array.

    Evaluated cells will contain either a number (float) or an error string.
    """
    for ridx, row in enumerate(self._cells):
      for cidx, cell in enumerate(row):
        try:
          self._eval_cell(ridx, cidx)
        except (ValueError, ZeroDivisionError):
          self._cells_eval[ridx][cidx] = self.ERR
    return self._cells_eval

  # Core of the eval implementation. Uses a recursive algorithm to
  # evaluate cells referred to by a given expression. Keeps track of
  # visited cells in order to detect circular dependencies.
  # Raises ValueError or ZeroDivisionError if it is not possible to evaluate
  # the expression.
  def _eval_cell(self, ridx, cidx):
    # Keep track of visited cells to detect circular dependencies.
    visited_key = str(ridx) + str(cidx)
    if visited_key in self._visited_cells:
      if self._cells_eval[ridx][cidx] == '':
        raise ValueError('Circular cell dependency.')
      else:
        return self._cells_eval[ridx][cidx]
    self._visited_cells[visited_key] = True

    cell = self._cells[ridx][cidx].strip().lower()
    if not cell:
      # Return 0 for whitespace cells.
      self._cells_eval[ridx][cidx] = 0
      return 0

    tokens = cell.split()
    stack = []
    for t in tokens:
      if t in self.OPERATORS:
        if len(stack) < 2:
          raise ValueError('Wrong number of operators for binary operator.')
        stack.append(self._eval_op(t, stack.pop(), stack.pop()))
      else:
        stack.append(self._eval_val(t))

    if len(stack) != 1:
      raise ValueError('Wrong number of items left in stack.')

    self._cells_eval[ridx][cidx] = stack[0]
    return stack[0]

  # Returns the result of evaluating the given operator and operands.
  # Assumes operator is one of: + - * /
  def _eval_op(self, operator, operand2, operand1):
    if operator == '+':
      return operand1 + operand2
    elif operator == '-':
      return operand1 - operand2
    elif operator == '*':
      return operand1 *  operand2
    else:
      return operand1 / operand2

  # Returns the result of evaluating the given token as a value.
  # This could be a reference to a different cell, in which case the
  # cell evaluation method is called recursively.
  def _eval_val(self, token):
    if any(c.isalpha() for c in token):
      # Looks like a reference to another cell. Recurse.
      ridx, cidx = self._get_cell_idx(token)
      return self._eval_cell(ridx, cidx)
    else:
      return float(token)

  # Converts the given token to a (row index, column index) tuple.
  # The token is expected to be in the format {LETTER}{NUMBER}, where
  # LETTER indicates the column, and NUMBER the row of the cell.
  def _get_cell_idx(self, token):
    matches = self.CELL_REF_RE.match(token)
    if not matches or len(matches.groups()) != 2:
      raise ValueError('Error parsing cell reference.')

    ridx = int(matches.group(2)) - 1

    cidx = 0
    for letter in matches.group(1):
      cidx += ord(letter) - ord('a')

    try:
      self._cells[ridx][cidx]
    except IndexError:
      raise ValueError('Reference to non-existent cell.')

    return ridx, cidx


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('filename', help='The name of the file to process.')
  parser.add_argument('--out', help='Name for the output, evaluated file.',
                      default='eval.csv')
  args = parser.parse_args()

  print 'Loading sheet:', args.filename
  s = Sheet.from_file(args.filename)
  print 'Writing evaluated sheet to:', args.out
  s.eval_to_csv(args.out)
