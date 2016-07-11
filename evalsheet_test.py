import evalsheet
import unittest

class TestSheet(unittest.TestCase):
  def test_empty(self):
    s = evalsheet.Sheet([['', '     ']])
    self.assertSequenceEqual(s.eval(), [[0, 0]])

  def test_operand(self):
    s = evalsheet.Sheet([['3']])
    self.assertSequenceEqual(s.eval(), [[3.0]])

  def test_expression(self):
    s = evalsheet.Sheet([['5 1 2 + 4 * + 3 -']])
    self.assertSequenceEqual(s.eval(), [[14.0]])

  def test_mix_of_cells(self):
    s = evalsheet.Sheet([['1', '', '5 1 2 + 4 * + 3 -'],['','2']])
    self.assertSequenceEqual(s.eval(), [[1.0, 0, 14.0], [0, 2.0]])

  def test_malformed_expressions(self):
    s = evalsheet.Sheet([['foobar']])
    self.assertSequenceEqual(s.eval(), [['#ERR']])

    s = evalsheet.Sheet([['3-2']])
    self.assertSequenceEqual(s.eval(), [['#ERR']])

    s = evalsheet.Sheet([['3-foo']])
    self.assertSequenceEqual(s.eval(), [['#ERR']])

    s = evalsheet.Sheet([['3-/']])
    self.assertSequenceEqual(s.eval(), [['#ERR']])

  def test_cell_reference(self):
    s = evalsheet.Sheet([['a2 b1 +', '1'], ['3']])
    self.assertSequenceEqual(s.eval(), [[4.0, 1.0], [3.0]])

  def test_cell_reference_malformed(self):
    s = evalsheet.Sheet([['a2 + b1', '1'], ['3']])
    self.assertSequenceEqual(s.eval(), [['#ERR', 1.0], [3.0]])

  def test_circular_cell_reference(self):
    s = evalsheet.Sheet([['b1', 'a1'], ['a1', '2', 'b1']])
    self.assertSequenceEqual(s.eval(),
        [['#ERR', '#ERR'], ['#ERR', 2.0, '#ERR']])

  def test_division_by_zero(self):
    s = evalsheet.Sheet([['3 0 /']])
    self.assertSequenceEqual(s.eval(), [['#ERR']])

  def test_reference_to_nonexistent_cell(self):
    s = evalsheet.Sheet([['a49']])
    self.assertSequenceEqual(s.eval(), [['#ERR']])

if __name__ == '__main__':
  unittest.main()
