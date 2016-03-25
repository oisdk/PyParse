from FunctorApplicativeMonad import Functor, Applicative, Monad
from typing import Callable, Any, TypeVar, Tuple, Generic, cast, Union
from abc import ABCMeta, abstractmethod

Loc = Tuple[int, int]
A = TypeVar('A')
B = TypeVar('B')

class TypeResult(Functor, Applicative, Monad, metaclass=ABCMeta):

    @abstractmethod
    def fmap(self, fn: Callable[[Any], Any]) -> 'TypeResult':
        return NotImplemented

    @abstractmethod
    def apply(self, something: 'TypeResult') -> 'TypeResult':
        return NotImplemented

    @abstractmethod
    def bind(self, something: Callable[[Any], 'TypeResult']) -> 'TypeResult':
        return NotImplemented

    @classmethod
    def pure(cls, x: A) -> 'Success[A]':
        return Success(x, (0,0))

    @abstractmethod
    def __repr__(self) -> str:
        return NotImplemented

    @abstractmethod
    def __bool__(self) -> bool:
        return NotImplemented

    @staticmethod
    @abstractmethod
    def pure(val) -> 'TypeResult':
        return NotImplemented

    def _locstr(self) -> str:
        return "line %i, column %i" % (self._loc[0] + 1, self._loc[1] + 1)

class TypeSuccess(TypeResult, Generic[A]):

    def __init__(self, value: A) -> None:
        self._val = value

    def fmap(self, fn: Callable[[A], B]) -> 'TypeSuccess[B]':
        return TypeSuccess(fn(self._val))

    def apply(self, something: TypeResult) -> TypeResult:
        res = something.fmap(cast(Callable[[Any], Any], self._val))
        return res

    def bind(self, something: Callable[[A], TypeResult]) -> TypeResult:
        res = something(self._val)
        return res

    @staticmethod
    def pure(val):
        return TypeSuccess(val)

    def finish(self) -> A:
        return self._val

    def __bool__(self) -> bool:
        return True

    def __repr__(self) -> str:
        return "Type check with %s" % self._val

class TypeFailure(TypeResult):

    def __init__(self, exp, got) -> None:
        self._exp, self._got = exp, got

    def fmap(self, fn: Callable[[Any], Any]) -> 'TypeFailure':
        return self

    def apply(self, something: TypeResult) -> 'TypeFailure':
        return self

    def bind(self, something: Callable[[A], TypeResult]) -> 'TypeFailure':
        return self

    def __bool__(self) -> bool:
        return False

    @staticmethod
    def pure(val):
        return Success(val)

    def __repr__(self) -> str:
        return 'Expected type %s, received %s' % self._exp, self._got
