from abc import ABCMeta, abstractmethod
from typing import Callable, Any, Generic, TypeVar
from Utils import *

class Functor(metaclass=ABCMeta):

    @abstractmethod
    def fmap(self, fn: Callable[[Any], Any]) -> 'Functor':
        return NotImplemented

    def __rmod__(self, fn: Callable[[Any], Any]) -> 'Functor':
        return self.fmap(fn)

class Applicative(metaclass=ABCMeta):

    @abstractmethod
    def apply(self, something) -> 'Applicative':
        return NotImplemented

    def __mul__(self, something) -> 'Applicative':
        return self.apply(something)

class Monad(metaclass=ABCMeta):

    @abstractmethod
    def bind(self, func: Callable[[Any], Any]) -> 'Monad':
        return NotImplemented

    @staticmethod
    @abstractmethod
    def pure(val: Any) -> 'Monad':
        return NotImplemented

    def __rshift__(self, something: 'Monad') -> 'Monad':
        return self.bind(const(something))

    def __lshift__(self, something: 'Monad') -> 'Monad':
        return self.bind(lambda x: something.fmap(const(x)))
