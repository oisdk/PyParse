from FunctorApplicativeMonad import Functor, Applicative, Monad
from typing import Callable, Any, TypeVar, Tuple, Generic, cast, Union
from abc import ABCMeta, abstractmethod

Loc = Tuple[int, int]
A = TypeVar('A')
B = TypeVar('B')

class ParseResult(Functor, Applicative, Monad, metaclass=ABCMeta):

    @abstractmethod
    def fmap(self, fn: Callable[[Any], Any]) -> 'ParseResult':
        return NotImplemented

    @abstractmethod
    def apply(self, something: 'ParseResult') -> 'ParseResult':
        return NotImplemented

    @abstractmethod
    def bind(self, something: Callable[[Any], 'ParseResult']) -> 'ParseResult':
        return NotImplemented

    @classmethod
    def pure(cls, x: A) -> 'Success[A]':
        return Success(x, (0,0))

    @abstractmethod
    def finish(self) -> Union[str, Any]:
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

class Success(ParseResult, Generic[A]):

    def __init__(self, value: A, loc: Loc, dep=0) -> None:
        self._loc, self._val, self._dep = loc, value, dep

    def fmap(self, fn: Callable[[A], B]) -> 'Success[B]':
        return Success(fn(self._val), self._loc, self._dep)

    def apply(self, something: ParseResult) -> ParseResult:
        res = something.fmap(cast(Callable[[Any], Any], self._val))
        res._dep += self._dep
        return res

    def bind(self, something: Callable[[A], ParseResult]) -> ParseResult:
        res = something(self._val)
        res._dep += self._dep
        return res

    @staticmethod
    def pure(val):
        return Success(val, (0,0))

    def finish(self) -> A:
        return self._val

    def __bool__(self) -> bool:
        return True

    def __or__(lhs, _):
        return lhs

    def __repr__(self) -> str:
        return "Success! Finished at %s, with %s" % (self._locstr(), self._val)

class Failure(ParseResult):

    def __init__(self, loc: Loc, exp: str, rec: str, dep=0) -> None:
        self._loc, self._exp, self._rec, self._dep = loc, exp, rec, dep

    def fmap(self, fn: Callable[[Any], Any]) -> 'Failure':
        return self

    def apply(self, something: ParseResult) -> 'Failure':
        return self

    def bind(self, something: Callable[[A], ParseResult]) -> 'Failure':
        return self

    def __bool__(self) -> bool:
        return False

    def __or__(lhs,rhs):
        if rhs or rhs._dep > lhs._dep:
            return rhs
        return lhs
        # elif lhs._loc > rhs._loc:
        #     return lhs
        # elif lhs._loc < rhs._loc:
        #     return rhs


    @staticmethod
    def pure(val):
        return Success(val, (0,0))

    def finish(self) -> str:
        expect = ("\nExpecting %s" % self._exp) if self._exp else ""
        return "%s:\nUnexpected %s%s" % (self._locstr(), self._rec, expect)

    def __repr__(self) -> str:
        return self.finish()

