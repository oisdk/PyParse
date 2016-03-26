from LangParser import expr, string
import unittest
from itertools import zip_longest, chain
from random import choice, randrange
from string import printable

class ParseTests(unittest.TestCase):

    def testExpr(self):
        for i in range(100):
            nums = [str(randrange(-1000, 1000)) for _ in range(10)]
            ops = [choice(['*','+','-']) for _ in range(9)]
            lin = ' '.join('%s%s%s' % (n, ' ' if randrange(2) else '' , o) if o else n for n, o in zip_longest(nums, ops))
            py = eval(lin)
            mine = expr()(lin)
            self.assertEqual(py, mine,lin)
        for line, col in [('1 + a', 4), ('2 + -d', 5), ('2 + ', 4), ('(4 + 4', 6)]:
            res = expr()._run([line.encode(), None], (0,0))
            self.assertEqual(res._loc, (0,col), 'On string: %s\n%s' % (line, res))

    def testStr(self):
        escdict = {'\t':'\\t', '\n':'\\n', '"':'\\"', '\r':'\\r', '\\': '\\\\'}
        for _ in range(100):
            unesc = ''.join(choice(printable) for _ in range(randrange(30)))
            line = ''.join(chain('"', (escdict.get(c,c) for c in unesc), '"'))
            self.assertEqual(unesc, string()(line))
        for line, col in [('"a\\bc"', 3), ('"abc', 4)]:
            res = string()._run([line.encode(), None], (0,0))
            self.assertEqual(res._loc, (0,col), 'On string: %s\n%s' % (line, res))


if __name__ == '__main__':
    unittest.main()
