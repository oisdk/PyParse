from FunctorApplicativeMonad import Functor, Applicative, Monad
from typing import Callable, Any, TypeVar, Tuple, Generic, cast, Union
from abc import ABCMeta, abstractmethod

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
S = TypeVar('S')

class State(Functor, Applicative, Monad, Generic[S,A]):

    def __init__(self, fn: Callable[[S], Tuple[S, A]]):
        self.__call__ = fn

    def fmap(self, fn: Callable[[A], Any]) -> 'State':
        def run(state):
            return second(self(state), fn)
        return State(run)

    def apply(self, something: 'State') -> 'State':
        def run(state):
            new, val = self(state)
            return val(something(new))
        return State(run)

    def bind(self, fn: Callable[[A], 'State']) -> 'State':
        def run(state):
            new, val = self(state)
            newm = fn(val)
            return newm(new)
        return State(run)

    @staticmethod
    def pure(val) -> 'State':
        return State(lambda s: (s,x))

def second(tup: Tuple[A, B], fn: Callable[B, C]) -> Tuple[A, C]:
    return (tup[0], fn(tup[1]))

get = State(lambda s: (s,s))
def put(val):
    return State(lambda _: (val, None))

