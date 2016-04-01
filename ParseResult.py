from FunctorApplicativeMonad import Functor, Applicative, Monad
from abc import ABCMeta, abstractmethod

class ParseResult(Functor, Applicative, Monad, metaclass=ABCMeta):

    @abstractmethod
    def fmap(self, fn) -> 'ParseResult':
        return NotImplemented

    @abstractmethod
    def apply(self, something: 'ParseResult') -> 'ParseResult':
        return NotImplemented

    @abstractmethod
    def bind(self, something) -> 'ParseResult':
        return NotImplemented

    @classmethod
    def pure(cls, x) -> 'Success[A]':
        return Success(x, (0,0))

    @abstractmethod
    def finish(self):
        return NotImplemented

    @abstractmethod
    def __repr__(self) -> str:
        return NotImplemented

    @abstractmethod
    def __bool__(self) -> bool:
        return NotImplemented

    @staticmethod
    @abstractmethod
    def pure(val) -> 'ParseResult':
        return NotImplemented

    def _locstr(self) -> str:
        return "line %i, column %i" % (self._loc[0] + 1, self._loc[1] + 1)

class Success(ParseResult):

    def __init__(self, value, loc) -> None:
        self._loc, self._val = loc, value

    def fmap(self, fn):
        return Success(fn(self._val), self._loc)

    def apply(self, something: ParseResult) -> ParseResult:
        return something.fmap(self._val)

    def bind(self, something):
        return something(self._val)

    @staticmethod
    def pure(val):
        return Success(val, (0,0))

    def finish(self):
        return self._val

    def __bool__(self) -> bool:
        return True

    def __or__(lhs, _):
        return lhs

    def __repr__(self) -> str:
        return "Success! Finished at %s, with %s" % (self._locstr(), self._val)

class Failure(ParseResult):

    def __init__(self, loc, exp, rec: str, com=False):
        self._loc, self._exp, self._rec, self._com = loc, exp, rec, com

    def fmap(self, fn) -> 'Failure':
        return self

    def apply(self, something: ParseResult) -> 'Failure':
        return self

    def bind(self, something):
        return self

    def __bool__(self) -> bool:
        return False

    def __or__(lhs,rhs):
        if lhs._com: return lhs
        if rhs or rhs._com: return rhs
        return Failure(lhs._loc, lhs._exp | rhs._exp, lhs._rec, False)

    @staticmethod
    def pure(val):
        return Success(val, (0,0))

    def finish(self) -> str:
        expect = '\nExpecting '
        if len(self._exp) == 2: expect += ' or '.join(self._exp)
        elif self._exp:
            e = list(self._exp)
            f = ', '.join(e[:-1])
            if f: expect += f + ', or '
            expect += e[-1]
        else: expect = ''
        return "%s:\nUnexpected %s%s" % (self._locstr(), self._rec, expect)

    def __repr__(self) -> str:
        return self.finish()
