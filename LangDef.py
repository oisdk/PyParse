from abc import ABCMeta, abstractmethod

class Expr(metaclass=ABCMeta):

class Var(Expr):
    def __init__(self, name: str) -> None:
        self._nam = name

class App(Expr):
    def __init__(self, f: Expr, x: Expr) -> None:
        self._fun, self._var = f, x

class Lam(Expr):
    def __init__(self, f: str, x: Expr) -> None:
        self._nam, self._var = f, x

