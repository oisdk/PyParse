from Parser import *
from Utils import *
from Do import do
import string
from functools import reduce, partial
from operator import neg, mul
from AST import AST

# Language whitespace
spaces = many(oneof(" \n\r"))
def token(p): return p << spaces

def reserved(word): return token(match(word))

# Boolean literal parser
boollit = const(True) % reserved('True') | const(False) % reserved('False')

# Numeric literal parsers
digit = oneof(string.digits) ^ 'a digit'
numdict = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9}
digits = some(numdict.get % digit)
posinteger = digits.fmap(lambda d: reduce(lambda a,e: e + 10 * a, d, 0))
integer = posinteger

@do(Parser)
def absfloating():
    befor = yield posinteger
    after = yield (match('.') >> commit(digits)) | Parser.pure([])
    mant = reduce(lambda a,e: (e+a)/10, reversed(after), 0)
    return befor + mant
floating = lambda: negate(absfloating())

# Parentheses
@do(Parser)
def between(o,c,p):
    yield o
    x = yield commit(p())
    yield commit(c())
    return x

def parens(p): return between(reserved('('), lambda: reserved(')'), p )

# Infix operator parser
def infixop(x,f): return reserved(x) >> Parser.pure(f)
def prefixop(x,f): return infixop(x,f) | Parser.pure(lambda x: x)
notop = prefixop('not', lambda a: AST(not a._res, '!', [a]))
negate = prefixop('-', lambda a: AST(-a._res, '-', [a]))

# Integer expression parser
factor = lambda: negate.apply(token(absfloating().fmap(AST)) | parens(expr)())
term   = lambda: chainl1(factor, mulop)
expr   = lambda: chainl1(term, addop)
def add(a,b): return AST(a._res + b._res, '+', [a,b])
def sub(a,b): return AST(a._res - b._res, '-', [a,b])
def mul(a,b): return AST(a._res * b._res, '*', [a,b])
addop  = infixop('+', add) | infixop('-', sub)
mulop  = infixop('*', mul)

# Boolean expression parser
bfact  = lambda: notop.apply(token(boollit).fmap(AST) | parens(bexpr)())
bterm  = lambda: chainl1(bfact, andop)
bexpr  = lambda: chainl1(bterm, orop)
def andA(a,b): return AST(a._res and b._res, '&', [a,b])
def orA(a,b): return AST(a._res or b._res, '|', [a,b])
andop  = infixop('and', andA)
orop   = infixop('or', orA)

# Escaping parser for string literals
escdict = {'n':'\n', 'r': '\r', 't': '\t', '"': '"', '\\':'\\'}
escchar = oneof(''.join(escdict))
escpat = match('\\') >> escdict.get % commit(escchar)
string = between(match('"'), lambda: reserved('"'),
                 lambda: ''.join % many(escpat | noneof('"')))

# REPL-like function for the parsers
def interact(p):
    for line in iter(input, 'q'):
        res = (p() << eof)._run([line.encode(), None], (0,0))
        if not res:
            i = res._loc[1]
            print(line[:i] + '\033[91m' + line[i:] + '\033[0m')
        print(res.finish().svg())
