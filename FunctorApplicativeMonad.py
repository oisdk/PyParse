from abc import ABCMeta, abstractmethod
from Utils import *

class Functor(metaclass=ABCMeta):

    @abstractmethod
    def fmap(self, fn) -> 'Functor':
        return NotImplemented

    def __rmod__(self, fn) -> 'Functor':
        return self.fmap(fn)

class Applicative(metaclass=ABCMeta):

    @abstractmethod
    def apply(self, something) -> 'Applicative':
        return NotImplemented

    def __mul__(self, something) -> 'Applicative':
        return self.apply(something)

    def __rshift__(self, something: 'Applicative') -> 'Applicative':
        return self.fmap(lambda _: lambda x: x).apply(something)
        # return self.bind(const(something))

    def __lshift__(self, something: 'Applicative') -> 'Applicative':
        return self.fmap(lambda x: lambda _: x).apply(something)
        # return self.bind(lambda x: something.fmap(const(x)))

class Monad(metaclass=ABCMeta):

    @abstractmethod
    def bind(self, func) -> 'Monad':
        return NotImplemented

    @staticmethod
    @abstractmethod
    def pure(val) -> 'Monad':
        return NotImplemented

    # def __rshift__(self, something: 'Monad') -> 'Monad':
    #     return self.bind(const(something))

    # def __lshift__(self, something: 'Monad') -> 'Monad':
    #     return self.bind(lambda x: something.fmap(const(x)))
