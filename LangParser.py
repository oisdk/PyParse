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

@do(Parser)
def token(p):
    a = yield p()
    yield spaces
    yield Parser.pure(a)

def reserved(word): return token(lambda: match(word))

@do(Parser)
def parens(p):
    yield reserved("(")()
    x = yield p()
    yield commit(reserved(")")())
    yield Parser.pure(x)

posinteger = digits.fmap(lambda d: reduce(lambda a,e: e + 10 * a, d, 0))

def negate(p): return match('-') >> neg % p | p

integer = negate(posinteger)

@do(Parser)
def absfloating():
    befor = yield posinteger
    after = yield (match('.') >> digits) | Parser.pure([])
    mant = reduce(lambda a,e: (e+a)/10, reversed(after), 0)
    yield Parser.pure(befor + mant)

floating = lambda: negate(absfloating())

@do(Parser)
def chainl1(p, op):
    a = yield p()
    yield rest(a,p,op)()

def rest(a,p,op): return lambda: recur(a,p,op)() | Parser.pure(a)

@do(Parser)
def recur(a, p, op):
    f = yield op()
    b = yield commit(p())
    yield rest(f(a,b), p, op)()

boollit = const(True) % match('True') | const(False) % match('False')

def infixop(x,f): return lambda: reserved(x)() >> Parser.pure(f)
factor = lambda: token(lambda: integer)() | parens(expr)()
term   = lambda: chainl1(factor, mulop)()
expr   = lambda: chainl1(term, addop)()
bfact  = lambda: token(lambda: boollit)() | parens(bexpr)()
bterm  = lambda: chainl1(bfact, andop)()
bexpr  = lambda: chainl1(bterm, orop)()
addop  = lambda: infixop('+', add)() | infixop('-', sub)()
mulop  = lambda: infixop('*', mul)()
andop  = lambda: infixop('&&', lambda a, b: a and b)()
orop   = lambda: infixop('||', lambda a, b: a or b)()

escdict = {'n':'\n', 'r': '\r', 't': '\t', '"': '"', '\\':'\\'}
escchar = oneof(''.join(escdict))
escpat = match('\\') >> escdict.get % commit(escchar)

@do(Parser)
def string():
    yield match('"')
    cs = yield many(escpat | satisfies(lambda c: c != '"'))
    yield reserved('"')()
    yield Parser.pure(''.join(cs))
