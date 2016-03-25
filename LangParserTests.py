from LangParser import expr
import unittest
from itertools import zip_longest
from random import choice, randrange

class ParseTests(unittest.TestCase):

    def testExpr(self):
        for i in range(100):
            nums = [str(randrange(-1000, 1000)) for _ in range(10)]
            ops = [choice(['*','+','-']) for _ in range(9)]
            lin = ' '.join('%s%s%s' % (n, ' ' if randrange(2) else '' , o) if o else n for n, o in zip_longest(nums, ops))
            py = eval(lin)
            mine = expr()(lin)
            self.assertEqual(py, mine,lin)

if __name__ == '__main__':
    unittest.main()
