from FunctorApplicativeMonad import Functor, Applicative, Monad
from typing import Callable, Any
from functools import partial

class Maybe(Functor, Applicative, Monad):

    def __init__(self, value):
        self._is_just = True
        self._value = value

    def fmap(self, mapper: Callable[[Any], Any]) -> 'Maybe':
        if self._is_just:
            value = self._value
            try: return Maybe(mapper(value))
            except TypeError: return Maybe(partial(mapper, value))
        else:
            nothing = Maybe(None)
            nothing._is_just = False
            return nothing

    def apply(self, something: 'Maybe') -> 'Maybe':
        if self._is_just:
            return something.fmap(self._value)
        else: return self

    def bind(self, func: Callable[[Any], 'Maybe']) -> 'Maybe':
        if self._is_just:
            value = self._value
            return func(value)
        else:
            nothing = Maybe(None)
            nothing._is_just = False
            return nothing

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Maybe):
            return self._is_just == other._is_just and self._value == other._value
        return False

    def __repr__(self) -> str:
        return 'Just %s' % self._value if self._is_just else 'Nothing'

    @staticmethod
    def pure(val) -> 'Maybe':
        return Maybe(val)

Nothing = Maybe(None)
Nothing._is_just = False

def Just(val):
    return Maybe(val)
