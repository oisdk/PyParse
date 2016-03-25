from Parser import *
from Do import do
import string
from functools import reduce, partial
from operator import neg, add, sub, mul

lowers = string.ascii_lowercase
uppers = string.ascii_uppercase
numbrs = string.digits
alphas = string.ascii_letters
alpnms = alphas + numbrs

lowercase = oneof(lowers)
uppercase = oneof(uppers)
letter = oneof(alphas)
alphanum = oneof(alpnms)
digit = oneof(numbrs)

numdict = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9}

digits = some(digit.fmap(numdict.get))
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
    yield reserved(")")()
    yield Parser.pure(x)

posinteger = digits.fmap(lambda d: reduce(lambda a,e: e + 10 * a, d, 0))

def negate(p): return match('-') >> p.fmap(neg) | p

integer = negate(posinteger)

@do(Parser)
def absfloating():
    befor = yield posinteger
    after = yield (match('.') >> digits) | Parser.pure([])
    mant = reduce(lambda a,e: (e+a)/10, reversed(after), 0)
    yield Parser.pure(befor + mant)

floating = lambda: negate(absfloating()())

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

def factor(): return token(lambda: integer)() | parens(expr)()
def term(): return chainl1(factor, mulop)()
def expr(): return chainl1(term, addop)()
def infixop(x, f): return lambda: reserved(x)() >> Parser.pure(f)
def addop(): return infixop('+', add)() | infixop('-', sub)()
def mulop(): return infixop('*', mul)()

for line in iter(input, 'q'):
    print(expr()(line))

# from itertools import zip_longest
# from random import choice, randrange
# for i in range(1000):
#     if not i % 100: print(i)
#     nums = [str(randrange(-1000, 1000)) for _ in range(10)]
#     ops = [choice(['*','+','-']) for _ in range(9)]
#     lin = ' '.join('%s%s%s' % (n, ' ' if randrange(2) else '' , o) if o else n for n, o in zip_longest(nums, ops))
#     py = eval(lin)
#     mine = expr()(lin)
#     if py != mine:
#         print(lin)
#         print(py)
#         print(mine)
#         break
