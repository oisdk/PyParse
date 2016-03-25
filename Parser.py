from FunctorApplicativeMonad import Functor, Applicative, Monad
from abc import ABCMeta, abstractmethod
from ParseResult import *
from typing import Callable, Any, Tuple, Optional, cast, Union, List

Runner = Callable[[List[bytes], Loc], ParseResult]

class Parser(Functor, Applicative, Monad):

    """This is a semi-traditional monadic parser. It has two fields: a
    description, and a parsing function."""

    def __init__(self, run: Runner, dsc: str) -> None:
        self._dsc, self._run = dsc, run

    def fmap(self, mapper: Callable[[Any], Any]) -> 'Parser':
        def run(text: List[bytes], loc: Loc):
            return self._run(text, loc).fmap(mapper)
        return Parser(run, self._dsc)

    def apply(self, something: 'Parser') -> 'Parser':
        def run(text: List[bytes], loc: Loc):
            result = self._run(text, loc)
            return result and result.apply(something._run(text, result._loc))
        return Parser(run, self._dsc)

    def bind(self, func: Callable[[Any], 'Parser']) -> 'Parser':
        def run(text: List[bytes], loc: Loc):
            result = self._run(text, loc)
            if not result: return result
            return result.bind(lambda x: func(x)._run(text, result._loc))
        return Parser(run, self._dsc)

    @staticmethod
    def pure(val) -> 'Parser':
        def run(text, loc):
            return Success(val, loc)
        return Parser(run, 'anything')

    def __repr__(self) -> str:
        return self._dsc or ''

    def __call__(self, string: str) -> Union[Any, str]:
        return self._run(string.encode().splitlines() + [None], (0,0)).finish()

    def __or__(lhs, rhs):
        dsc = '%s or %s' % (lhs, rhs)
        def run(text, loc): return lhs._run(text, loc) | rhs._run(text, loc)
        return Parser(run, dsc)

def quote(string: str) -> str:
    return '"%s"' % string

def commit(p: Parser) -> Parser:
    def run(b,l):
        result = p._run(b,l)
        if not result: result._com = True
        return result
    return Parser(run, p._dsc)


def advance(loc: Loc, by: int, over: List[bytes]) -> Optional[Loc]:
    lin, col = loc[0], loc[1] + by
    cur = len(over[lin])
    while col >= cur:
        lin += 1
        col -= cur
        if over[lin] == None: return (lin, 0)
    return (lin, col)

def err(text: List[bytes], loc: Loc, dsc: str, length=None, dep=0) -> Failure:
    if text[loc[0]] == None:
        msg = 'eof'
    else:
        end = length and min(length, len(text[loc[0]]) - loc[1])
        msg = quote(text[loc[0]][loc[1]:][:end].decode())
    return Failure(loc, dsc, msg, dep)

def match(string):
    b = str.encode(string)
    def run(text, loc):
        line, col = loc
        if text[line] and text[line].startswith(b, col):
            return Success(string, advance(loc, len(b), text))
        return err(text, loc, quote(string), len(b))
    return Parser(run, quote(string))

def oneof(chars):
    bset = set(str.encode(chars))
    desc = "one of %s" % ", ".join(map(quote, chars))
    def run(text, loc):
        line, col = loc
        if text[line]:
            c = text[line][col]
            if c in bset:
                return Success(chr(c), advance(loc, 1, text))
        return err(text, loc, desc, 1)
    return Parser(run, desc)

def many(p):
    def run(text, loc):
        results = []
        while text[loc[0]]:
            result = p._run(text, loc)
            if not result: break
            results.append(result._val)
            loc = result._loc
        return Success(results,loc)
    return Parser(run, 'many %s' % p)

def some(p):
    return p.fmap(lambda x: lambda xs: [x] + xs).apply(many(p))

def choice(f, *p):
    return reduce(Parser.__or__, (f,) + p)

def _eof(t,l):
    return Success(None, l) if t[l[0]] == None else err(t,l,'eof')

def satisfies(pred, dsc=None) -> Parser:
    def run(text, loc):
        line, col = loc
        if text[line]:
            c = chr(text[line][col])
            if pred(c): return Success(c, advance(loc, 1, text))
        return err(text, loc, dsc, 1)
    return Parser(run, dsc)

anychar = satisfies(lambda _: True, 'any character')

eof = Parser(_eof, 'eof')
