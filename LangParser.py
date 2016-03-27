from Parser import *
from Utils import *
from Do import do
import string
from functools import reduce, partial
from operator import neg, add, sub, mul

digit = oneof(string.digits) ^ 'a digit'
numdict = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9}
digits = some(numdict.get % digit)
spaces = many(oneof(" \n\r"))

def token(p): return p << spaces

def reserved(word): return token(match(word))

@do(Parser)
def between(o,c,p):
    yield o
    x = yield p()
    yield c
    return x

def parens(p): return between(reserved('('), commit(reserved(')')), lambda: commit(p()))

posinteger = digits.fmap(lambda d: reduce(lambda a,e: e + 10 * a, d, 0))

def negate(p): return match('-') >> neg % p | p

integer = negate(posinteger)

@do(Parser)
def absfloating():
    befor = yield posinteger
    after = yield (match('.') >> digits) | Parser.pure([])
    mant = reduce(lambda a,e: (e+a)/10, reversed(after()), 0)
    return befor + mant

floating = lambda: negate(absfloating())

boollit = const(True) % reserved('True') | const(False) % reserved('False')

def infixop(x,f): return reserved(x) >> Parser.pure(f)
factor = lambda: token(integer) | parens(expr)()
term   = lambda: chainl1(factor, mulop)
expr   = lambda: chainl1(term, addop)
bfact  = lambda: token(boollit) | parens(bexpr)()
bterm  = lambda: chainl1(bfact, andop)
bexpr  = lambda: chainl1(bterm, orop)
addop  = lambda: infixop('+', add) | infixop('-', sub)
mulop  = lambda: infixop('*', mul)
andop  = lambda: infixop('&&', lambda a, b: a and b)
orop   = lambda: infixop('||', lambda a, b: a or b)

escdict = {'n':'\n', 'r': '\r', 't': '\t', '"': '"', '\\':'\\'}
escchar = oneof(''.join(escdict))
escpat = match('\\') >> escdict.get % commit(escchar)

string = between(match('"'), reserved('"'),
                 lambda: many(escpat | noneof('"')).fmap(''.join))

def interact(p):
    for line in iter(input, 'q'):
        res = p()._run([line.encode(), None], (0,0))
        if not res: print(''.join('^' if i == res._loc[1] else ' ' for i in range(len(line))))
        print(res.finish())
