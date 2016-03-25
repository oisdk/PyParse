from FunctorApplicativeMonad import Functor, Applicative, Monad
from abc import ABCMeta, abstractmethod
from ParseResult import *
from typing import Callable, Any, Tuple, Optional, cast, Union, List

Runner = Callable[[List[bytes], Loc], ParseResult]

class Parser(Functor, Applicative, Monad):

    """This is a semi-traditional monadic parser. It has two fields: a
    description, and a parsing function."""

    def __init__(self, run: Runner) -> None:
        self._run = run

    def fmap(self, mapper: Callable[[Any], Any]) -> 'Parser':
        def run(text: List[bytes], loc: Loc):
            return self._run(text, loc).fmap(mapper)
        return Parser(run)

    def apply(self, something: 'Parser') -> 'Parser':
        def run(text: List[bytes], loc: Loc):
            result = self._run(text, loc)
            return result and result.apply(something._run(text, result._loc))
        return Parser(run)

    def bind(self, func: Callable[[Any], 'Parser']) -> 'Parser':
        def run(text: List[bytes], loc: Loc):
            result = self._run(text, loc)
            if not result: return result
            return result.bind(lambda x: func(x)._run(text, result._loc))
        return Parser(run)

    @staticmethod
    def pure(val) -> 'Parser':
        def run(text, loc):
            return Success(val, loc)
        return Parser(run)

    def __call__(self, string: str) -> Union[Any, str]:
        return self._run(string.encode().splitlines() + [None], (0,0)).finish()

    def __or__(lhs, rhs):
        return Parser(lambda t, l: lhs._run(t,l) | rhs._run(t,l))

    def __xor__(self, dsc):
        def run(text, loc):
            result = self._run(text, loc)
            if result: return result
            result._exp = {dsc}
            return result
        return Parser(run)

def quote(string: str) -> str:
    return '"%s"' % string

def commit(p: Parser) -> Parser:
    def run(b,l):
        result = p._run(b,l)
        if not result: result._com = True
        return result
    return Parser(run)


def advance(loc: Loc, by: int, over: List[bytes]) -> Optional[Loc]:
    lin, col = loc[0], loc[1] + by
    cur = len(over[lin])
    while col >= cur:
        lin += 1
        col -= cur
        if over[lin] == None: return (lin, 0)
    return (lin, col)

def err(text: List[bytes], loc: Loc, dsc: Set[str], length=None) -> Failure:
    if text[loc[0]] == None:
        msg = 'eof'
        loc = loc[0] - 1, len(text[loc[0] - 1]) - 1
    else:
        end = length and min(length, len(text[loc[0]]) - loc[1])
        msg = quote(text[loc[0]][loc[1]:][:end].decode())
    return Failure(loc, dsc, msg)

def match(string):
    b = str.encode(string)
    def run(text, loc):
        line, col = loc
        if text[line] and text[line].startswith(b, col):
            return Success(string, advance(loc, len(b), text))
        return err(text, loc, {quote(string)}, len(b))
    return Parser(run)

def oneof(chars):
    bset = set(str.encode(chars))
    def run(text, loc):
        line, col = loc
        if text[line]:
            c = text[line][col]
            if c in bset:
                return Success(chr(c), advance(loc, 1, text))
        return err(text, loc, {quote(c) for c in chars}, 1)
    return Parser(run)

def many(p):
    def run(text, loc):
        results = []
        while text[loc[0]]:
            result = p._run(text, loc)
            if not result: break
            results.append(result._val)
            loc = result._loc
        return Success(results,loc)
    return Parser(run)

def some(p):
    return p.fmap(lambda x: lambda xs: [x] + xs).apply(many(p))

def choice(f, *p):
    return reduce(Parser.__or__, (f,) + p)

def _eof(t,l):
    return Success(None, l) if t[l[0]] == None else err(t,l,{'eof'})

def satisfies(pred, dsc=None) -> Parser:
    def run(text, loc):
        line, col = loc
        if text[line]:
            c = chr(text[line][col])
            if pred(c): return Success(c, advance(loc, 1, text))
        return err(text, loc, {dsc}, 1)
    return Parser(run)

anychar = satisfies(lambda _: True, ['any character'])

eof = Parser(_eof)
