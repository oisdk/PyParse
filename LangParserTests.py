from LangParser import expr, string, bexpr
import unittest
from itertools import zip_longest, chain
from random import choice, randrange
from string import printable
from timeit import timeit
from Utils import *

def exprrun(lines):
    for line in lines:
        res = bexpr()(line)

class ParseTests(unittest.TestCase):

    def testExpr(self):
        for i in range(20):
            lin = ''.join(randnums(10)).lstrip()
            py = eval(lin)
            mine = expr()(lin)._res
            self.assertEqual(py, mine,lin)
        for line, col in [('1 + a', 4), ('2 + -d', 5), ('2 + ', 4), ('(4 + 4', 6), ('1 + (3 * -)', 10)]:
            res = expr()._run([line.encode(), None], (0,0))
            self.assertEqual(res._loc, (0,col), '\nBad error message on string: %s\n%s' % (line, res))

    def testStr(self):
        escdict = {'\t':'\\t', '\n':'\\n', '"':'\\"', '\r':'\\r', '\\': '\\\\'}
        for _ in range(100):
            unesc = ''.join(choice(printable) for _ in range(randrange(30)))
            line = ''.join(chain('"', (escdict.get(c,c) for c in unesc), '"'))
            self.assertEqual(unesc, string()(line))
        for line, col in [('"a\\bc"', 3), ('"abc', 4)]:
            res = string()._run([line.encode(), None], (0,0))
            self.assertEqual(res._loc, (0,col), '\nBad error message on string: %s\n%s' % (line, res))

    def testBool(self):
        for _ in range(100):
            lin = ''.join(randbools(10)).lstrip()
            self.assertEqual(eval(lin), bexpr()(lin)._res, lin)

    def testPerf(self):
        e, m = 7, 8
        with open('exprs', 'r') as file:
            g = list(file)
            print("\nBeginning performance test")
            t = timeit('exprrun(exprs)', setup='from __main__ import exprrun', number=1, globals={'exprs':g})
            print("Took %.2f seconds. (Expected: %i, Maximum: %i)" % (t, e, m))
            self.assertTrue(t < m, "Too slow!")

if __name__ == '__main__':
    unittest.main()
