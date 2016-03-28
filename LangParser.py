from Parser import *
from Utils import *
from Do import do
import string
from functools import reduce, partial
from operator import neg, add, sub, mul

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
def negate(p): return match('-') >> neg % p | p
integer = negate(posinteger)
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
    x = yield p()
    yield c
    return x
def parens(p): return between(reserved('('), commit(reserved(')')), lambda: commit(p()))

# Infix operator parser
def infixop(x,f): return reserved(x) >> Parser.pure(f)

# Integer expression parser
factor = lambda: token(integer) | parens(expr)()
term   = lambda: chainl1(factor, mulop)
expr   = lambda: chainl1(term, addop)
addop  = lambda: infixop('+', add) | infixop('-', sub)
mulop  = lambda: infixop('*', mul)

# Boolean expression parser
bfact  = lambda: token(boollit) | parens(bexpr)()
bterm  = lambda: chainl1(bfact, andop)
bexpr  = lambda: chainl1(bterm, orop)
andop  = lambda: infixop('&&', lambda a, b: a and b)
orop   = lambda: infixop('||', lambda a, b: a or b)

# Escaping parser for string literals
escdict = {'n':'\n', 'r': '\r', 't': '\t', '"': '"', '\\':'\\'}
escchar = oneof(''.join(escdict))
escpat = match('\\') >> escdict.get % commit(escchar)
string = between(match('"'), reserved('"'),
                 lambda: ''.join % many(escpat | noneof('"')))

# REPL-like function for the parsers
def interact(p):
    for line in iter(input, 'q'):
        res = (p() << eof)._run([line.encode(), None], (0,0))
        if not res:
            i = res._loc[1]
            print(line[:i] + '\033[91m' + line[i:] + '\033[0m')
        print(res.finish())
