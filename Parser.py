from FunctorApplicativeMonad import Functor, Applicative, Monad
from abc import ABCMeta, abstractmethod
from ParseResult import *
from Utils import *

class Parser(Functor, Applicative, Monad):

    """A monadic parser, similar to Haskell's Parsec. In contrast to Parsec,
    this parser backtracks by default: this behaviour can be avoided with the
    `commit` combinator."""

    def __init__(self, run):
        self._run = run

    def fmap(self, mapper) -> 'Parser':
        return Parser(lambda t,l: self._run(t,l).fmap(mapper))

    def apply(self, something: 'Parser') -> 'Parser':
        def run(text, loc):
            result = self._run(text, loc)
            if not result: return result
            return something.fmap(result._val)._run(text, result._loc)
        return Parser(run)

    def bind(self, func) -> 'Parser':
        def run(text, loc):
            result = self._run(text, loc)
            if not result: return result
            return func(result._val)._run(text, result._loc)
        return Parser(run)

    @staticmethod
    def pure(val) -> 'Parser':
        return Parser(lambda _,l: Success(val,l))

    def __call__(self, string: str):
        return self._run(string.encode().splitlines() + [None], (0,0)).finish()

    def __or__(lhs, rhs):
        def run(t, l):
            res = lhs._run(t,l)
            if res or res._com: return res
            return res | rhs._run(t,l)
        return Parser(run)

    def __xor__(self, dsc):
        """Corresponds to Parsec's `<?>` operator. Used to give a parser a
        description"""
        def run(text, loc):
            result = self._run(text, loc)
            if not result: result._exp = {dsc}
            return result
        return Parser(run)

def quote(string: str) -> str:
    return '"%s"' % string

def commit(p: Parser) -> Parser:

    """This turns off backtracking for a given Parser. This is useful for
    giving better error messages, when there is ambiguity at some stage
    of parsing. For instance, in an expression parser, the following:
        1 + (3 + _)
    would ideally give an error pointing to the '_'. However, if backtracking
    is turned on, the parser may give an error on the opening paren, or even
    worse, it may parse '1' without error.
    The solution is to have the parser commit whenever it sees a binary
    operator. This is because what comes after should be unambiguous."""

    def run(b,l):
        result = p._run(b,l)
        if not result: result._com = True
        return result
    return Parser(run)


def advance(loc, by, over):
    lin, col = loc[0], loc[1] + by
    cur = len(over[lin])
    while col >= cur:
        lin += 1
        col -= cur
        if over[lin] == None: return (lin, 0)
    return (lin, col)

def err(text, loc, dsc, length=None):
    if text[loc[0]] == None:
        msg = 'eof'
        loc = loc[0] - 1, len(text[loc[0] - 1])
    else:
        end = length and min(length, len(text[loc[0]]) - loc[1])
        msg = quote(text[loc[0]][loc[1]:][:end].decode())
    return Failure(loc, dsc, msg)

def match(string):
    b = str.encode(string)
    def run(text, loc):
        line, col = loc
        if text[line] != None and text[line].startswith(b, col):
            return Success(string, advance(loc, len(b), text))
        return err(text, loc, {quote(string)}, len(b))
    return Parser(run)

def many(p):
    def run(text, loc):
        results = []
        next = p._run(text,loc)
        while next:
            results.append(next._val)
            loc = next._loc
            next = p._run(text,loc)
        return next | Success(results,loc)
    return Parser(run)

def some(p):
    return p.fmap(lambda x: lambda xs: [x] + xs) * many(p)

def choice(f, *p):
    return reduce(Parser.__or__, (f,) + p)

def bsatisfies(pred, dsc=set()):
    def run(t,l):
        n,i = l
        if t[n]:
            c = t[n][i]
            if pred(c): return Success(chr(c), advance(l,1,t))
        return err(t,l,dsc,1)
    return Parser(run)

def satisfies(pred, dsc=set()):
    return bsatisfies(compose(pred, chr), dsc)

def oneof(chars):
    return bsatisfies(set(str.encode(chars)).__contains__, {quote(c) for c in chars})

def noneof(chars):
    bsetf = set(str.encode(chars)).__contains__
    return bsatisfies(lambda c: not bsetf(c), {quote(c) for c in chars})

anychar = satisfies(const(True), {'any character'})

eof = Parser(lambda t,l: Success(None, l) if t[l[0]] == None else err(t,l,{'eof'}))

def chainl1(p,op):
    def run(t,l):
        x = p()._run(t,l)
        while x:
            o = op._run(t,x._loc)
            if not o: break
            y = p()._run(t,o._loc)
            if not y: return y
            x = Success(o._val(x._val,y._val), y._loc)
        return x
    return Parser(run)
