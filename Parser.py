from FunctorApplicativeMonad import Functor, Applicative, Monad
from abc import ABCMeta, abstractmethod
from ParseResult import *
from typing import Callable, Any, Tuple, Optional, cast, Union, List
from Utils import *

Runner = Callable[[List[bytes], Loc], ParseResult]

class Parser(Functor, Applicative, Monad):

    """A monadic parser, similar to Haskell's Parsec. In contrast to Parsec,
    this parser backtracks by default: this behaviour can be avoided with the
    `commit` combinator."""

    def __init__(self, run: Runner) -> None:
        self._run = run

    def fmap(self, mapper: Callable[[Any], Any]) -> 'Parser':
        return Parser(lambda t,l: self._run(t,l).fmap(mapper))

    def apply(self, something: 'Parser') -> 'Parser':
        def run(text: List[bytes], loc: Loc):
            result = self._run(text, loc)
            return result and result * something._run(text, result._loc)
        return Parser(run)

    def bind(self, func: Callable[[Any], 'Parser']) -> 'Parser':
        def run(text: List[bytes], loc: Loc):
            result = self._run(text, loc)
            return result.bind(lambda x: func(x)._run(text,result._loc))
        return Parser(run)

    @staticmethod
    def pure(val) -> 'Parser':
        return Parser(lambda _,l: Success(val,l))

    def __call__(self, string: str) -> Union[Any, str]:
        return self._run(string.encode().splitlines() + [None], (0,0)).finish()

    def __or__(lhs, rhs):
        def run(t, l):
            res = lhs._run(t,l)
            if res: return res
            return res | rhs._run(t,l)
        return Parser(run)

    def __xor__(self, dsc):
        """Corresponds to Parsec's `<?>` operator. Used to give a parser a
        description"""
        def run(text, loc):
            result = self._run(text, loc)
            if result: return result
            result._exp = {dsc}
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


def advance(loc: Loc, by: int, over: List[bytes]) -> Loc:
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
        loc = loc[0] - 1, len(text[loc[0] - 1])
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

    # Too slow:
    # return p.bind(lambda h: many(p).fmap(lambda t: [h] + t)) | Parser.pure([])

    def run(text, loc):
        results = []
        while text[loc[0]]:
            result = p._run(text, loc)
            if not result:
                if result._com: return result
                break
            results.append(result._val)
            loc = result._loc
        return Success(results,loc)
    return Parser(run)

def some(p):
    return p.fmap(lambda x: lambda xs: [x] + xs) * many(p)

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
        return err(text, loc, {dsc} if dsc else set(), 1)
    return Parser(run)

anychar = satisfies(const(True), 'any character')

eof = Parser(_eof)
