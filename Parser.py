from FunctorApplicativeMonad import Functor, Applicative, Monad
from abc import ABCMeta, abstractmethod
from ParseResult import *
from typing import Callable, Any, Tuple, Optional, cast, Union, List

Runner = Callable[[List[bytes], Loc], ParseResult]

class Parser(Functor, Applicative, Monad):

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
            new = func(result._val)
            return new._run(text, result._loc)
        return Parser(run, self._dsc)

    @staticmethod
    def pure(val) -> 'Parser':
        def run(text, loc):
            return Success(val, loc)
        return Parser(run, 'anything')

    def __repr__(self) -> str:
        return self._dsc

    def __call__(self, string: str) -> Union[Any, str]:
        return self._run(string.encode().splitlines(), (0,0)).finish()


def pastEnd(text: List[bytes], loc: Loc) -> bool:
    return loc[0] >= len(text) or loc[0] + 1 == len(text) and loc[1] >= len(text[loc[0]])

def quote(string: str) -> str:
    return '"%s"' % string

def advance(by: int, linelen: int, loc: Loc) -> Loc:
    newcol = loc[1] + by
    return (loc[0] + newcol // linelen, newcol % linelen)

def err(text: List[bytes], loc: Loc, dsc: str, length=None) -> Failure:
    return Failure(loc, dsc, 'eof' if pastEnd(text,loc) else quote(text[loc[0]][loc[1]:][:length].decode()))

def matchString(string):
    b = str.encode(string)
    def run(text, loc):
        line, col = loc
        try:
            if text[line].startswith(b, col):
                return Success(string, advance(len(b), len(text[line]), loc))
        except IndexError: pass
        return err(text, loc, quote(string), len(b))
    return Parser(run, string)

def oneOf(chars):
    bset = set(str.encode(chars))
    desc = "one of %s" % ", ".join(map(quote, chars))
    def run(text, loc):
        line, col = loc
        try:
            c = text[line][col]
            if c in bset:
                return Success(chr(c), advance(1, len(text[line]), loc))
        except IndexError: pass
        return err(text, loc, desc, 1)
    return Parser(run, desc)

def anyChar():
    def run(text, loc):
        if pastEnd(text, loc): return err(text, loc, 'any character')
        return Success(chr(text[loc[0]][loc[1]]), advance(1, len(text[loc[0]]), loc))
    return withFunc(run, 'any character')

def many(p):
    def run(text, loc):
        results = []
        while not pastEnd(text,loc):
            result = p._run(text, loc)
            if not result: break
            results.append(result._val)
            loc = result._loc
        return Success(results,loc)
    return Parser(run, 'many %s' % p)

def choice(f, *p):
    ps = (f,) + p
    desc = 'One of: %s' % ', '.join(map(str, ps))
    def run(text, loc):
        for parser in ps:
            result = parser._run(text, loc)
            if result: return result
        return err(text, loc, desc)
    return Parser(run, desc)

def _eof(t,l):
    return Success(None, l) if pastEnd(t,l) else err(t,l,'eof')


eof = Parser(_eof, 'eof')
